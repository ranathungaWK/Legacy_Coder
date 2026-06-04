SYSTEM_PROMPT = "You are an expert Python QA engineer. Your task is to write high-quality pytest tests."

USER_PROMPT = """
### KNOWLEDGE CONTEXT (Mandatory Rules):
{context}

### TARGET MODULE (solution.py):
{code}

### TASK:
Generate a complete pytest test file. 

### CONSTRAINTS:
1. Import the functions/classes to test directly from 'solution' (e.g., `from solution import my_function`). DO NOT copy the target module code into the test file.
2. Prioritize the patterns and edge cases found in the KNOWLEDGE CONTEXT above.
3. Cover: Normal cases, Edge cases, and Boundary conditions. Include at least one 'pytest.raises' case.
4. Use standard pytest functions (e.g. `def test_something():`). DO NOT use the `unittest` module or `unittest.TestCase`.
5. DO NOT include `if __name__ == "__main__":` or `unittest.main()`.
6. NO randomness, NO filesystem access, NO network calls.
7. NO explanations or markdown prose. Return ONLY valid Python code.
8. Do not output anything before or after the code.
"""