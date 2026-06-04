import asyncio
from agents.testing.agent import TestingAgent

TestAgent = TestingAgent()

async def main():
    rewritten = """
    def divide(a, b):
        return a / b
    """
    result = await TestAgent.generate_tests(rewritten_code=rewritten)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())