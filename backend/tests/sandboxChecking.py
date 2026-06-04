from execution.sandbox import run_pytest_in_docker

solution = """
def add(a, b):
    return a + b
"""

tests = """
from solution import add

def test_add():
    assert add(2, 3) == 5
"""

result = run_pytest_in_docker(solution, tests)
print(result)

