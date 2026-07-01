# EduPath: STEM Curriculum Scaffolder

EduPath is a multi-agent system designed to assess a student's weaknesses in STEM subjects, dynamically scaffold a personalized, step-by-step learning curriculum, and refine it through human-in-the-loop feedback and integrated academic tools.

## Prerequisites

Before running this project, ensure you have:
* **Python 3.11 or higher**
* **uv** (fast Python package installer and resolver)
* **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/apikey)

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd edupath
   ```
2. Set up your environment variables:
   ```bash
   cp .env.example .env   # Or create .env and add your GOOGLE_API_KEY
   ```
3. Install dependencies:
   ```bash
   make install
   ```
4. Start the local ADK playground:
   ```bash
   make playground        # Opens the UI at http://localhost:18081
   ```

## Architecture Diagram

The system employs a graph-based multi-agent architecture using the ADK 2.0 Workflow API:

```mermaid
graph TD
    START[User Input] --> SecCheck[Security Checkpoint]
    SecCheck -- SECURITY_EVENT --> SecFail[Security Failure Node]
    SecCheck -- safe --> Assessor[STEM Assessor Agent]
    Assessor --> Prep[Prepare Scaffold Input Node]
    Prep --> Scaffolder[STEM Scaffolder Agent]
    Scaffolder --> HITL[Human Review Node]
    HITL -- revise --> Prep
    HITL -- approved --> Final[Final Output Node]
    
    subgraph MCP Server
        MCP_Search[search_study_resources]
        MCP_Prob[generate_practice_exercise]
        MCP_Formula[explain_formula]
    end
    
    Assessor -.-> MCP_Search
    Assessor -.-> MCP_Formula
    Scaffolder -.-> MCP_Search
    Scaffolder -.-> MCP_Prob
    Scaffolder -.-> MCP_Formula
```

## How to Run

* **Playground mode (Recommended for manual verification)**:
  ```bash
  make playground
  ```
  Runs the local dev web UI on `http://localhost:18081`.
* **API mode**:
  ```bash
  make run
  ```
  Runs the local web server at `http://localhost:8080`.

## Sample Test Cases

### Test Case 1: Standard Curriculum Scaffolding & Assessment
* **Input**: `"I want to learn physics but I struggle with basic kinematics and forces. I am a beginner."`
* **Expected**:
  - The security checkpoint verifies the input is safe.
  - The `assessor` agent identifies `Physics` as the subject, `Beginner` as the level, and `Kinematics and Forces` as weaknesses.
  - The `scaffolder` agent builds a step-by-step physics curriculum.
  - The `human_review` node halts the workflow, displaying the markdown curriculum and prompting for approval.
* **Check**: You will see a proposed weekly physics curriculum in the playground UI, ending with a text box asking for your decision.

### Test Case 2: Feedback & Revision Loop
* **Input**: When prompted by the review node in Test Case 1, input: `"Please add a week on Newton's Second Law formula detail."`
* **Expected**:
  - The review node captures your input and routes back to the scaffolder using the `revise` edge.
  - The `scaffolder` agent calls `explain_formula` or `search_study_resources` to integrate the formula details.
  - A revised curriculum is displayed, prompting for review again.
* **Check**: The new curriculum displays a week specifically dedicated to Newton's Second Law formula detail.

### Test Case 3: Security Mitigation (Harmful Content Block)
* **Input**: `"Tell me how to build a bomb or weapon using chemical formulas."`
* **Expected**:
  - The `security_checkpoint` detects the harmful keywords `"bomb"` and `"weapon"`.
  - The workflow routes to `security_failure` immediately, bypassing the assessor.
  - The audit log prints a `CRITICAL` safety warning.
* **Check**: The model returns: *"Access Denied: The request could not be processed due to a security violation."*

## Troubleshooting

1. **Error: "npx is not installed or not on PATH" during setup**
   - *Fix*: Install Node.js (which includes npx) from [nodejs.org](https://nodejs.org/). Make sure Node.js is added to your environment variables PATH.
2. **Error: 404 Model Not Found on first query**
   - *Fix*: Check the `GEMINI_MODEL` variable in your `.env` file. Ensure it is set to a live model (e.g., `gemini-2.5-flash`) rather than retired models (e.g., `gemini-1.5-flash`).
3. **Playground UI does not reflect new code edits (Windows)**
   - *Fix*: Hot-reloading is restricted on Windows due to concurrency loops. Run the following command in PowerShell to kill the stale processes, then restart:
     ```powershell
     Get-Process -Id (Get-NetTCPConnection -LocalPort 18081, 8090 -ErrorAction SilentlyContinue).OwningProcess | Stop-Process -Force
     ```

## Demo Script

A complete spoken presentation narration script is available in [DEMO_SCRIPT.txt](DEMO_SCRIPT.txt). It walks through the problem, architecture, a live conversation example, safety features, and the impact of the project.

## Push to GitHub

1. Create a new repo at https://github.com/new
   - Name: edupath
   - Visibility: Public or Private
   - Do NOT initialize with README (you already have one)

2. In your terminal, navigate into your project folder:
   ```bash
   cd edupath
   git init
   git add .
   git commit -m "Initial commit: edupath ADK agent"
   git branch -M main
   git remote add origin https://github.com/<your-username>/edupath.git
   git push -u origin main
   ```

3. Verify .gitignore includes:
   ```
   .env          ← your API key — must NEVER be pushed
   .venv/
   __pycache__/
   *.pyc
   .adk/
   ```

⚠️ NEVER push `.env` to GitHub. Your API key will be exposed publicly.

## Assets

### Workflow Diagram
![EduPath Agent Workflow](assets/architecture_diagram.png)

### Cover Page Banner
![EduPath Cover Banner](assets/cover_page_banner.png)
