import datetime
import re
import json
import logging
from typing import List, Optional, Any
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.workflow import Workflow, START, FunctionNode
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents.context import Context
from google.genai import types

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from app.config import config

# Logger setup
logger = logging.getLogger("security_checkpoint")
logging.basicConfig(level=logging.INFO)

# --- Schemas ---

class AssessmentResult(BaseModel):
    subject: str = Field(description="The main STEM subject being assessed (e.g., Mathematics, Physics, Computer Science).")
    student_level: str = Field(description="Assessed level of the student (e.g., Beginner, Intermediate, Advanced).")
    identified_weaknesses: List[str] = Field(description="List of specific weaknesses or gaps in foundational knowledge identified.")
    assessment_summary: str = Field(description="A brief explanation of the assessment results.")

class Module(BaseModel):
    week_number: int = Field(description="The week or step number of this module.")
    topic: str = Field(description="The topic to be covered.")
    description: str = Field(description="Detailed explanation of what the module covers.")
    learning_resources: List[str] = Field(description="Suggested topics or resources to study.")

class CurriculumPlan(BaseModel):
    subject: str = Field(description="The STEM subject.")
    title: str = Field(description="A catchy title for the curriculum.")
    modules: List[Module] = Field(description="Weekly learning modules.")
    practice_problems: List[str] = Field(description="Sample practice problems for the student to try.")

# --- MCP Toolset Setup ---

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "python", "-m", "app.mcp_server"],
        ),
    ),
)

# --- Sub-Agents ---

assessor = LlmAgent(
    name="assessor",
    model=config.model,
    instruction=(
        "You are a STEM subject assessor. Your job is to analyze the student's background, "
        "stated struggles, and current STEM request. Identify their level, main subject, "
        "and specific foundational gaps or weaknesses. You can use search_study_resources or explain_formula "
        "to check resources and formulas to verify content if needed. Output a structured JSON result."
    ),
    output_schema=AssessmentResult,
    output_key="assessment",
    tools=[mcp_toolset],
)

scaffolder = LlmAgent(
    name="scaffolder",
    model=config.model,
    instruction=(
        "You are a STEM Curriculum Scaffolder. Take the student's assessment results (weaknesses, subject, level) "
        "and build a highly personalized, structured learning curriculum. If the student has provided feedback "
        "for revisions, adjust the curriculum accordingly to address their requests. "
        "You should use search_study_resources to find good resources for the modules, generate_practice_exercise "
        "to create sample problems, and explain_formula if you need to explain formulas. Output a structured JSON result."
    ),
    output_schema=CurriculumPlan,
    output_key="curriculum",
    tools=[mcp_toolset],
)

# --- Workflow Nodes ---

def security_checkpoint(ctx: Context, node_input: types.Content) -> Event:
    """Checks input for PII, prompt injection, and domain safety.
    Scrubs PII (Emails, Phones, SSNs), detects prompt injection attempts,
    validates educational safety rules, and outputs a structured audit log.
    """
    text = ""
    if node_input and node_input.parts:
        text = "".join(part.text for part in node_input.parts if part.text)
    
    session_id = ctx.session.id
    
    # 1. PII Scrubbing
    scrubbed_text = text
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
    
    emails_found = re.findall(email_pattern, text)
    phones_found = re.findall(phone_pattern, text)
    ssns_found = re.findall(ssn_pattern, text)
    
    scrubbed_text = re.sub(email_pattern, "[EMAIL]", scrubbed_text)
    scrubbed_text = re.sub(phone_pattern, "[PHONE]", scrubbed_text)
    scrubbed_text = re.sub(ssn_pattern, "[SSN]", scrubbed_text)
    
    pii_detected = bool(emails_found or phones_found or ssns_found)
    
    # 2. Prompt Injection Detection
    injection_keywords = [
        "ignore previous instructions", 
        "system prompt", 
        "jailbreak", 
        "you are now", 
        "developer mode", 
        "override instructions"
    ]
    injection_detected = any(kw in text.lower() for kw in injection_keywords)
    
    # 3. Domain-Specific Safety Check (Harmful Content)
    harmful_keywords = ["bomb", "weapon", "hack", "harm", "explosive", "illegal"]
    harmful_detected = any(kw in text.lower() for kw in harmful_keywords)
    
    # Audit logging
    log_data = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "session_id": session_id,
        "input_length": len(text),
        "pii_detected": pii_detected,
        "pii_scrubbed_count": len(emails_found) + len(phones_found) + len(ssns_found),
        "injection_detected": injection_detected,
        "harmful_content_detected": harmful_detected,
    }
    
    if harmful_detected:
        log_data["severity"] = "CRITICAL"
        log_data["action"] = "BLOCK_AND_ROUTE_TO_SECURITY_EVENT"
        logger.warning(json.dumps(log_data))
        return Event(output="Security Checkpoint: Harmful content block.", route="SECURITY_EVENT")
        
    if injection_detected:
        log_data["severity"] = "WARNING"
        log_data["action"] = "BLOCK_AND_ROUTE_TO_SECURITY_EVENT"
        logger.warning(json.dumps(log_data))
        return Event(output="Security Checkpoint: Prompt injection block.", route="SECURITY_EVENT")
        
    if pii_detected:
        log_data["severity"] = "INFO"
        log_data["action"] = "SCRUB_AND_CONTINUE"
        logger.info(json.dumps(log_data))
        # Update user's text with scrubbed text inside a Content object
        scrubbed_content = types.Content(role="user", parts=[types.Part.from_text(text=scrubbed_text)])
        return Event(output=scrubbed_content, route="safe")
        
    log_data["severity"] = "INFO"
    log_data["action"] = "ALLOW"
    logger.info(json.dumps(log_data))
    return Event(output=node_input, route="safe")

def security_failure(ctx: Context, node_input: str):
    """Outputs a security warning."""
    msg = "Access Denied: The request could not be processed due to a security violation."
    yield Event(content=types.Content(role="model", parts=[types.Part.from_text(text=msg)]))
    yield Event(output=msg)

def prepare_scaffold_input(ctx: Context, node_input: Any) -> str:
    """Constructs prompt for the scaffolder based on assessment and feedback."""
    assessment = ctx.state.get("assessment", {})
    feedback = ctx.state.get("feedback")
    
    if feedback:
        return (
            f"Please revise the STEM curriculum. "
            f"Foundational gaps/assessment: {assessment}. "
            f"Student feedback for revision: {feedback}"
        )
    else:
        return f"Generate a STEM curriculum. Foundational gaps/assessment: {assessment}"

async def human_review(ctx: Context, node_input: dict):
    """Presents proposed curriculum to the student and prompts for approval or feedback."""
    ctx.state["curriculum"] = node_input
    
    if not ctx.resume_inputs or "student_decision" not in ctx.resume_inputs:
        title = node_input.get("title", "Curriculum Plan")
        subject = node_input.get("subject", "STEM")
        modules = node_input.get("modules", [])
        problems = node_input.get("practice_problems", [])
        
        md_text = f"### Proposed Curriculum: {title} ({subject})\n\n"
        for m in modules:
            md_text += f"**Week {m.get('week_number', '?')}: {m.get('topic', 'Topic')}**\n"
            md_text += f"{m.get('description', '')}\n"
            md_text += f"Resources: {', '.join(m.get('learning_resources', []))}\n\n"
            
        md_text += "**Practice Problems:**\n"
        for p in problems:
            md_text += f"- {p}\n"
            
        yield Event(content=types.Content(role="model", parts=[types.Part.from_text(text=md_text)]))
        yield RequestInput(
            interrupt_id="student_decision",
            message="Please review the proposed curriculum. Reply with 'yes' to approve, or describe any changes you want."
        )
        return

    decision = ctx.resume_inputs["student_decision"]
    if isinstance(decision, str) and decision.lower().strip() in ["yes", "approve", "y", "looks good"]:
        yield Event(output=node_input, route="approved")
    else:
        yield Event(output=decision, route="revise", state={"feedback": decision})

def final_output(ctx: Context, node_input: dict):
    """Outputs the finalized curriculum."""
    msg = "🎉 Curriculum approved and finalized!"
    yield Event(content=types.Content(role="model", parts=[types.Part.from_text(text=msg)]))
    yield Event(output=node_input)

# --- Workflow Definition ---

root_agent = Workflow(
    name="edupath_workflow",
    edges=[
        (START, security_checkpoint),
        (security_checkpoint, {"SECURITY_EVENT": security_failure, "safe": assessor}),
        (assessor, prepare_scaffold_input),
        (prepare_scaffold_input, scaffolder),
        (scaffolder, human_review),
        (human_review, {"revise": prepare_scaffold_input, "approved": final_output}),
    ],
)

app = App(
    root_agent=root_agent,
    name="edupath_app",
)
