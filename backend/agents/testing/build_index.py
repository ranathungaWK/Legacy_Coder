import os 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document


def load_kb_documents(folder_path):
    documents = []

    for root, _ , files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r" , encoding="utf-8") as f:
                    content = f.read()

                    documents.append(Document(
                        page_content=content,
                        metadata={"source": file}
                    ))

    return documents

def build_index():
    print("Loading documents from knowledge base...")
    raw_docs = load_kb_documents(r"knowledge_base")

    if not raw_docs:
        raise ValueError("No documents found in the knowledge base.")
        return 
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap =50
    )

    documents = splitter.split_documents(raw_docs)

    print(f"Creating embeddings for {len(documents)} chunks...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model = "models/embedding-001"
    )

    vectorstore = FAISS.from_documents(documents, embeddings)

    os.makedirs(r"vectorstore", exist_ok=True)
    vectorstore.save_local(r"vectorstore\faiss_index")
    print("Index saved successfully to testing/vectorstore/faiss_index")


if __name__ == "__main__":
    build_index()

