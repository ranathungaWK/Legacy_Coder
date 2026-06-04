from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.schemas.rewrite import RewriteOutput
from .prompts import SYSTEM_PROMPT , USER_PROMPT
from app.schemas.input import LegacyCodeInput
from app.schemas.explanation import ExplanationOutput



class ModernizationAgent:

    def __init__(self , model_name : str = "gemini-2.5-flash"):
        self._model_name = model_name
        self.llm = None

        self.prompt = ChatPromptTemplate.from_messages([
            ("system" , SYSTEM_PROMPT) ,
            ("user" , USER_PROMPT + "\n\n{format_instructions}")
        ])

        self.parser = JsonOutputParser(pydantic_object=RewriteOutput)

    def _ensure_llm(self):
        if self.llm is None:
            self.llm = ChatGoogleGenerativeAI(
                model = self._model_name,
                temperature = 0.0,
                convert_system_message_to_human=True
            )

    async def rewrite(self , legacy_code :str , language : str ,explanation : ExplanationOutput) -> RewriteOutput :
        """Modernize the legacy code"""

        self._ensure_llm()
        chain = self.prompt | self.llm | self.parser

        explanation_obj = (
            explanation
            if isinstance(explanation, ExplanationOutput)
            else ExplanationOutput.model_validate(explanation)
        )
        result = await chain.ainvoke({
            "language": language,
            "code": legacy_code,
            "explanation": explanation_obj,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        return RewriteOutput.model_validate(result)


