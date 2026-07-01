import sys
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("EduPath Tools")

@mcp.tool()
def search_study_resources(topic: str) -> str:
    """Searches for educational study resources, videos, and documentation for a specific STEM topic.

    Args:
        topic: The STEM topic to search resources for (e.g., 'Calculus limits', 'Newtonian mechanics', 'Recursion').

    Returns:
        A formatted markdown string containing recommended educational resources, videos, and articles.
    """
    topic_lower = topic.lower()
    
    if "calculus" in topic_lower or "limit" in topic_lower or "derivative" in topic_lower:
        return (
            "### Recommended Study Resources for Calculus:\n"
            "1. **Khan Academy: Calculus 1** - Comprehensive video series covering limits, derivatives, and integrals.\n"
            "2. **OpenStax Calculus Volume 1** - Free peer-reviewed textbook. Recommended: Chapter 2: Limits, and Chapter 3: Derivatives.\n"
            "3. **3Blue1Brown: Essence of Calculus** - Highly visual series for intuitive understanding of calculus concepts.\n"
            "4. **Paul's Online Math Notes** - Detailed written tutorials and walkthroughs with practice problems."
        )
    elif "mechanics" in topic_lower or "newton" in topic_lower or "physics" in topic_lower:
        return (
            "### Recommended Study Resources for Physics (Mechanics):\n"
            "1. **OpenStax College Physics** - Chapter 4: Two-Dimensional Kinematics, Chapter 5: Dynamics: Force and Newton's Laws of Motion.\n"
            "2. **MIT OpenCourseWare: Classical Mechanics** - Video lectures and lecture notes by Walter Lewin.\n"
            "3. **Flipping Physics** - Interactive, fun videos covering AP Physics / introductory college mechanics."
        )
    elif "recursion" in topic_lower or "algorithm" in topic_lower or "computer science" in topic_lower:
        return (
            "### Recommended Study Resources for Computer Science (Algorithms):\n"
            "1. **GeeksforGeeks: Recursion** - Interactive articles, visual diagrams, and code snippets in Python/C++.\n"
            "2. **MIT 6.006: Introduction to Algorithms** - Free lecture videos on recursion, dynamic programming, and search.\n"
            "3. **LeetCode / HackerRank Practice** - Scaffolded coding tasks to practice recursive functions."
        )
    else:
        return (
            f"### Study Resources for {topic}:\n"
            f"1. **OpenStax Academic Search** - Search results for '{topic}' across college textbook library.\n"
            f"2. **YouTube Educational** - Search query: '{topic} tutorial for beginners'.\n"
            f"3. **Wolfram Alpha** - Excellent tool for computational lookup and definitions related to '{topic}'."
        )

@mcp.tool()
def generate_practice_exercise(topic: str, difficulty: str = "Beginner") -> str:
    """Generates a scaffolded practice exercise or problem for a STEM topic.

    Args:
        topic: The STEM topic to generate the problem for (e.g., 'Algebra', 'Forces', 'Arrays').
        difficulty: The difficulty level ('Beginner', 'Intermediate', or 'Advanced').

    Returns:
        A practice question, multiple choice options or prompt, and a hidden step-by-step solution guide.
    """
    topic_lower = topic.lower()
    diff = difficulty.capitalize()
    
    if "algebra" in topic_lower or "linear equation" in topic_lower:
        if diff == "Beginner":
            return (
                "### Practice Problem: Solve for x\n"
                "**Question:** 3x + 7 = 22\n\n"
                "**Steps to Solve:**\n"
                "1. Subtract 7 from both sides: 3x = 15\n"
                "2. Divide both sides by 3: x = 5\n"
                "**Solution:** x = 5"
            )
        else:
            return (
                f"### Practice Problem: Solve the Quadratic Equation ({diff})\n"
                "**Question:** x^2 - 5x + 6 = 0\n\n"
                "**Solution Hint:** Factor the quadratic equation: (x - 2)(x - 3) = 0. "
                "Therefore, the roots are x = 2 and x = 3."
            )
    elif "force" in topic_lower or "gravity" in topic_lower or "physics" in topic_lower:
        return (
            f"### Practice Problem: Newton's Second Law ({diff})\n"
            "**Question:** A box with a mass of 10 kg is pushed across a frictionless surface. "
            "If it accelerates at a rate of 3 m/s^2, what is the net force acting on the box?\n\n"
            "**Formula:** F = m * a\n"
            "**Calculation:** F = 10 kg * 3 m/s^2 = 30 N\n"
            "**Solution:** 30 Newtons (N)"
        )
    else:
        return (
            f"### Practice Problem: {topic} ({diff})\n"
            f"**Question:** Explain the core concept of {topic} and give a practical example.\n\n"
            f"**Recommended Check:** Make sure you can write a brief definition and identify at least one real-world application."
        )

@mcp.tool()
def explain_formula(formula_name: str) -> str:
    """Provides a detailed definition, variables breakdown, and worked example for a STEM formula.

    Args:
        formula_name: The name of the formula to explain (e.g., 'Quadratic Formula', 'Newton's Second Law', 'Euler's Formula').

    Returns:
        A comprehensive breakdown of the formula and how to use it.
    """
    name = formula_name.lower()
    
    if "quadratic" in name:
        return (
            "### Formula: The Quadratic Formula\n"
            "**Mathematical Expression:** x = [-b ± √(b² - 4ac)] / 2a\n\n"
            "**Variables:**\n"
            "- **x**: The roots of the quadratic equation ax² + bx + c = 0.\n"
            "- **a**: Coefficient of x² (a ≠ 0).\n"
            "- **b**: Coefficient of x.\n"
            "- **c**: Constant term.\n"
            "- **b² - 4ac**: The Discriminant (determines the number and type of roots).\n\n"
            "**Worked Example:** Solve x² - 5x + 6 = 0 (a=1, b=-5, c=6):\n"
            "1. Discriminant: (-5)² - 4(1)(6) = 25 - 24 = 1.\n"
            "2. roots: [5 ± √1] / 2 = [5 ± 1] / 2.\n"
            "3. roots are x = 3 and x = 2."
        )
    elif "newton" in name or "f = ma" in name or "second law" in name:
        return (
            "### Formula: Newton's Second Law of Motion\n"
            "**Mathematical Expression:** F = m * a\n\n"
            "**Variables:**\n"
            "- **F**: Net Force acting on the object (measured in Newtons, N).\n"
            "- **m**: Mass of the object (measured in kilograms, kg).\n"
            "- **a**: Acceleration of the object (measured in meters per second squared, m/s²).\n\n"
            "**Key Concept:** Acceleration is directly proportional to net force and inversely proportional to mass.\n"
            "**Worked Example:** Mass = 5 kg, Acceleration = 2 m/s² → F = 5 * 2 = 10 N."
        )
    else:
        return (
            f"### STEM Formula Lookup: '{formula_name}'\n"
            f"**Definition:** A formula represents a standard mathematical or physical relationship between quantities.\n"
            f"**Tip:** Verify variables and check their units before applying the formula to a problem."
        )

if __name__ == "__main__":
    mcp.run(transport="stdio")
