import os
import sqlite3
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# ✅ Load environment variables from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ Constants
DB_DIR = "db"
COLLECTION_NAME = "deep_research"
DB_PATH = "knowledge.db"

def load_documents_from_sqlite():
    """Load research notes from SQLite DB into LangChain Document objects."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, summary FROM knowledge WHERE summary IS NOT NULL AND summary != ''")
    rows = cursor.fetchall()
    conn.close()

    docs = []
    for title, summary in rows:
        if title and summary:
            # Create a document with both title and summary
            content = f"Title: {title}\n\nSummary: {summary}"
            doc = Document(page_content=content, metadata={"title": title})
            docs.append(doc)
    
    return docs

def build_vector_store(docs):
    if not docs:
        print("⚠️  No documents found in database!")
        return None
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = Chroma.from_documents(texts, embeddings, collection_name=COLLECTION_NAME, persist_directory=DB_DIR)
    db.persist()
    return db

def query_vector_store(vectordb, query):
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    results = retriever.get_relevant_documents(query)
    return results

if __name__ == "__main__":
    print("🧠 Loading documents from database...")
    documents = load_documents_from_sqlite()
    print(f"✅ Loaded {len(documents)} documents from database.")

    if not documents:
        print("❌ No documents found! Please add some research data to the database.")
        print("   You can use the existing data or add new research notes.")
        exit(1)

    print("🔍 Building vector store...")
    vectordb = build_vector_store(documents)
    print("✅ Vector store built.")

    print("\n💬 Ask anything about your research! Type 'exit' to quit.")
    print("📚 Available topics: AI tutors, educational technology, Khan Academy, etc.")
    print("-" * 50)
    
    while True:
        user_input = input("\n🧠 You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        
        if not user_input.strip():
            continue
            
        try:
            results = query_vector_store(vectordb, user_input)
            if results:
                print(f"\n📖 Found {len(results)} relevant documents:")
                for idx, doc in enumerate(results, 1):
                    print(f"\n🔹 Result {idx}:")
                    print(doc.page_content)
                    print("-" * 40)
            else:
                print("❓ No relevant documents found for your question.")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("   Make sure your OpenAI API key is set correctly in .env")
