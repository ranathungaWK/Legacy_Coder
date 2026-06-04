from dotenv import load_dotenv
load_dotenv()

from agents.comprehension.agent import ComprehensionAgent
from app.schemas.input import LegacyCodeInput
from app.schemas.explanation import ExplanationOutput

import asyncio

agent = ComprehensionAgent()

async def main():
    result = await agent.analyze(
        LegacyCodeInput(
            language="c",
            code='''#include <stdio.h>

                    int main() {
                        int number; 
                        int i;

                        // 1. Ask the user for input
                        printf("Enter a whole number: ");
                        
                        // 2. Read the user's input and store it in the 'number' variable
                        scanf("%d", &number);

                        printf("\n--- Multiplication Table for %d ---\n", number);

                        // 3. Loop 10 times to print the table
                        for(i = 1; i <= 10; i++) {
                            printf("%d x %d = %d\n", number, i, number * i);
                        }

                        return 0;
                    }'''
        )
    )
    explanation = ExplanationOutput.model_validate(result)
    print(explanation.model_dump())

if __name__ == "__main__":
    asyncio.run(main())
