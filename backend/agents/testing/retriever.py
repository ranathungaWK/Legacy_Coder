from re import search
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import os 

_cached_embeddings = None
_cached_vectorstores = {}

class Retriever:

    def __init__(self, index_path: str = os.path.join("agents", "testing", "vectorstore")) -> None:
        global _cached_embeddings
        if _cached_embeddings is None:
            _cached_embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001"
            )
        self.embeddings = _cached_embeddings

        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Vector store not found at {index_path}. Have you run the ingestion script ?")

        normalized_path = os.path.abspath(index_path)
        if normalized_path not in _cached_vectorstores:
            _cached_vectorstores[normalized_path] = FAISS.load_local(
                index_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        self.vectorstore = _cached_vectorstores[normalized_path]

        self.retriever = self.vectorstore.as_retriever(
            search_type = "mmr" ,
            search_kwargs = {"k" : 5 , "fetch_k" : 10}
        )

    async def get_context(self, query: str) -> str:
        """ Retrieves and formats context for the test building agent """
        try:
            docs = await self.retriever.ainvoke(query)
            context_parts = []
            for doc in docs:
                source = doc.metadata.get('source' , 'Unkown Source')
                context_parts.append(f"--- Source: {source} ---\n{doc.page_content}")

            return "\n\n".join(context_parts)
        except Exception as e:
            return f"Error retrieving context: {str(e)}"
            