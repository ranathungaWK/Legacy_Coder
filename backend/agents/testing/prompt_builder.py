from langchain_core.prompts import ChatPromptTemplate

try :
    from .prompts import SYSTEM_PROMPT , USER_PROMPT
except ImportError:

    SYSTEM_PROMPT = "You are a QA expert. Use the provided context to write tests."
    USER_PROMPT = "Code: {code}\nContext: {context}"

class PromptBuilder:
    def __init__(self ,system_template: str = SYSTEM_PROMPT , user_template: str = USER_PROMPT) -> None:
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system" , system_template),
            ("user" , user_template)
        ])

    def build(self , code:str , context:str) -> str:
        """ Returns a ChatPromptValue that can be passed directly 
        to llm.invoke() or a chain.""" 

        if not code:
            raise ValueError("Code snippet is required to build a prompt.")   
        return self.prompt_template.invoke({
            "code" : code ,
            "context" : context if context else "No additional context found. "
        })