class QueryBuilder:
    def build_query(self, code: str, context: str = "") -> str:
        """
        Builds a prompt for the AI agent.
        If context is provided (from the Retriever), it is injected to guide the agent.
        """
        
        
        context_section = ""
        if context:
            context_section = f"""
                ### RELEVANT KNOWLEDGE & PATTERNS
                Use the following patterns and edge cases to inform your test generation:
                {context}
                """

        return f"""
            You are an expert Python QA Engineer specializing in legacy code migration.
            Your task is to generate high-quality pytest test cases for the provided code.

            {context_section}

            ### TARGET CODE
            ```python
            {code} 
            """