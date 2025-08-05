import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# ✅ Load environment variables from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ Constants
DB_DIR = "db"
COLLECTION_NAME = "deep_research"
KNOWLEDGE_DIR = "knowledge"

def load_documents():
    docs = []
    for filename in os.listdir(KNOWLEDGE_DIR):
        if filename.endswith(".txt"):
            path = os.path.join(KNOWLEDGE_DIR, filename)
            loader = TextLoader(path, encoding='utf-8')
            docs.extend(loader.load())
    return docs

def build_vector_store(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = Chroma.from_documents(texts, embeddings, collection_name=COLLECTION_NAME, persist_directory=DB_DIR)
    db.persist()
    return db

def query_vector_store(vectordb, query):
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    results = retriever.get_relevant_documents(query)
    return results

if __name__ == "__main__":
    print("🧠 Loading documents...")
    documents = load_documents()
    print(f"✅ Loaded {len(documents)} documents.")

    print("🔍 Building vector store...")
    vectordb = build_vector_store(documents)
    print("✅ Vector store built.")

    print("❓ Ask a question:")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        results = query_vector_store(vectordb, user_input)
        for idx, doc in enumerate(results, 1):
            print(f"\n🔹 Result {idx}:\n{doc.page_content}")
