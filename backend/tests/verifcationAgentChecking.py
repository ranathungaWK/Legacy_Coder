from agents.verification.agent import VerificationAgent

rewritten = """
def add(a, b):
    return a + b
"""

tests = """
from solution import add

def test_add():
    assert add(2, 3) == 5
"""

import asyncio

agent = VerificationAgent()

async def main():
    result = await agent.verify(rewritten, tests)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())