from dotenv import load_dotenv
load_dotenv()

from agents.testing.agent import TestingAgent 

import asyncio

agent = TestingAgent()

async def main():
    rwc = "def add(a, b): return a + b"
    result = await agent.generate_tests(rewritten_code=rwc)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
