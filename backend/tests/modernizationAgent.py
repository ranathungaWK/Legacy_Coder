from dotenv import load_dotenv
load_dotenv()

from agents.modernization.agent import ModernizationAgent
from app.schemas.explanation import ExplanationOutput

import asyncio

async def test_js_add_function_modernization():
    explanation = ExplanationOutput(
        purpose="Adds two values using JavaScript '+' semantics.",
        inputs=[
            {"name": "a", "description": "First operand", "type": "any"},
            {"name": "b", "description": "Second operand", "type": "any"},
        ],
        outputs=[
            {"name": "return_value", "description": "Result of a + b", "type": "number | string"}
        ],
        assumptions=[
            "Python version should preserve numeric addition behavior"
        ],
        side_effects=[],
        edge_cases=[
            "String concatenation behavior differs from JavaScript"
        ],
        confidence_level="high"
    )

    legacy_code = """
    function add(a, b) {
        return a + b;
    }
    """

    agent = ModernizationAgent()
    result = await agent.rewrite(legacy_code = legacy_code , language = "javascript" , explanation = explanation)
    print(result.model_dump())

    assert "def add" in result.python_code

if __name__ == "__main__":
    asyncio.run(test_js_add_function_modernization())