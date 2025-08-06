#!/usr/bin/env python3
"""
Julius-Style Research Agent
Combines Chain-of-Thought reasoning with tool-use scaffolding and emotional intelligence
"""

import os
import json
import sqlite3
from typing import List
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Load environment variables
load_dotenv()

class JuliusResearchAgent:
    """
    A research agent that combines:
    - Chain-of-Thought reasoning
    - Tool-use scaffolding
    - Emotional intelligence
    - Feedback loops
    - Long-term memory
    """
    
    def __init__(self, db_path="knowledge.db", vector_db_path="db"):
        self.db_path = db_path
        self.vector_db_path = vector_db_path
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.llm = OpenAI(
            openai_api_key=self.openai_api_key,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Initialize vector store
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.vector_store = self._load_or_create_vector_store()
        
        # Research session tracking
        self.current_session = None
        self.steps = []
        self.tools_used = []
        self.feedback_history = []
    
    def _load_or_create_vector_store(self):
        """Load existing vector store or create new one from database."""
        try:
            # Try to load existing vector store
            if os.path.exists(self.vector_db_path):
                return Chroma(
                    persist_directory=self.vector_db_path,
                    embedding_function=self.embeddings,
                    collection_name="deep_research"
                )
        except Exception as e:
            print(f"⚠️  Could not load existing vector store: {e}")
        
        # Create new vector store from database
        print("🔍 Building vector store from database...")
        documents = self._load_documents_from_sqlite()
        
        if not documents:
            print("❌ No documents found in database!")
            return None
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)
        
        vector_store = Chroma.from_documents(
            texts, 
            self.embeddings, 
            collection_name="deep_research",
            persist_directory=self.vector_db_path
        )
        vector_store.persist()
        print(f"✅ Vector store created with {len(texts)} chunks")
        return vector_store
    
    def _load_documents_from_sqlite(self):
        """Load research documents from SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT title, raw_text FROM knowledge WHERE raw_text IS NOT NULL AND raw_text != ''")
        rows = cursor.fetchall()
        conn.close()
        
        docs = []
        for title, raw_text in rows:
            if title and raw_text:
                content = f"Title: {title}\n\nContent: {raw_text}"
                doc = Document(page_content=content, metadata={"title": title})
                docs.append(doc)
        
        return docs
    
    def _get_julius_persona_prompt(self):
        """Get the Julius-style persona prompt with emotional intelligence."""
        return """
You are an emotionally intelligent research agent with neurodivergent-friendly communication.

CORE PRINCIPLES:
- Explain complex ideas with clear analogies and simple language
- Break down complex topics into digestible steps
- Avoid overwhelming the user with too much information at once
- Use bullet points and summaries for clarity
- If you're unsure about something, say so clearly
- Show your reasoning process step by step
- Be patient and thorough in your explanations

COMMUNICATION STYLE:
- Use simple, clear language
- Provide context before diving into details
- Use analogies to explain complex concepts
- Break information into small, manageable chunks
- Always summarize key points at the end
- Ask clarifying questions when needed

RESEARCH APPROACH:
- Think aloud about your reasoning process
- Consider multiple perspectives
- Acknowledge limitations and uncertainties
- Provide evidence for your conclusions
- Suggest next steps or areas for further research
"""
    
    def _get_chain_of_thought_prompt(self, topic: str, depth: int, step: int):
        """Generate a chain-of-thought prompt for research steps."""
        return f"""
You are conducting research on "{topic}" at depth {depth}, step {step}.

THINKING PROCESS:
1. First, reflect on what you know about this topic
2. Consider what specific aspects need deeper investigation
3. Think about what tools or information would be most helpful
4. Formulate specific questions to guide your research

CURRENT CONTEXT:
- Research Topic: {topic}
- Depth Level: {depth}
- Step Number: {step}
- Previous Steps: {len(self.steps)} completed

Please think through your approach step by step, then provide your analysis.
"""
    
    def _get_relevant_documents(self, query: str, limit: int = 5):
        """Retrieve relevant documents using vector search."""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=limit)
            return [doc.page_content for doc in results]
        except Exception as e:
            print(f"⚠️  Error retrieving documents: {e}")
            return []
    
    def _record_feedback(self, query: str, response: str, rating: int, notes: str = ""):
        """Record user feedback for continuous improvement."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create feedback table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                rating INTEGER NOT NULL,
                notes TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO feedback (query, response, rating, notes)
            VALUES (?, ?, ?, ?)
        """, (query, response, rating, notes))
        
        conn.commit()
        conn.close()
        
        self.feedback_history.append({
            "query": query,
            "rating": rating,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        })
    
    def _save_research_session(self, topic: str, steps: List[str], tools_used: List[str]):
        """Save the research session to long-term memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create research_sessions table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                steps TEXT NOT NULL,
                tools_used TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO research_sessions (topic, steps, tools_used)
            VALUES (?, ?, ?)
        """, (topic, json.dumps(steps), json.dumps(tools_used)))
        
        conn.commit()
        conn.close()
    
    def run_research(self, topic: str, depth: int = 3, user_context: str = ""):
        """
        Run a Julius-style research session with chain-of-thought reasoning.
        
        Args:
            topic: The research topic
            depth: Number of research iterations
            user_context: Additional context from the user
        """
        print(f"🧠 Starting Julius Research Agent for: '{topic}'")
        print(f"📊 Research Depth: {depth} iterations")
        print("=" * 60)
        
        # Initialize session
        self.current_session = {
            "topic": topic,
            "depth": depth,
            "start_time": datetime.now(),
            "user_context": user_context
        }
        self.steps = []
        self.tools_used = []
        
        # Research loop with chain-of-thought reasoning
        for iteration in range(depth):
            print(f"\n🔄 Research Iteration {iteration + 1}/{depth}")
            print("-" * 40)
            
            # Step 1: Chain-of-Thought reasoning
            thought_prompt = self._get_chain_of_thought_prompt(topic, depth, iteration + 1)
            print("💭 Thinking through the research approach...")
            
            # Step 2: Retrieve relevant documents
            print("🔍 Searching for relevant documents...")
            relevant_docs = self._get_relevant_documents(topic, limit=5)
            self.tools_used.append("📚 Vector Search")
            
            if relevant_docs:
                print(f"✅ Found {len(relevant_docs)} relevant documents")
            else:
                print("⚠️  No relevant documents found")
            
            # Step 3: Generate research response
            print("🧠 Analyzing and synthesizing information...")
            
            # Build the research prompt
            research_prompt = f"""
{self._get_julius_persona_prompt()}

{thought_prompt}

RESEARCH CONTEXT:
Topic: {topic}
Iteration: {iteration + 1} of {depth}
User Context: {user_context if user_context else "None provided"}

RELEVANT DOCUMENTS:
{chr(10).join(relevant_docs) if relevant_docs else "No relevant documents found."}

PREVIOUS STEPS:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(self.steps)) if self.steps else "This is the first iteration."}

Please provide a comprehensive analysis that:
1. Shows your reasoning process step by step
2. Synthesizes information from the documents
3. Identifies key insights and patterns
4. Suggests areas for further investigation
5. Provides a clear summary of findings

Use simple language, analogies, and bullet points for clarity.
"""
            
            try:
                response = self.llm.predict(research_prompt)
                self.steps.append(response)
                
                print(f"\n📝 Research Step {iteration + 1} Complete")
                print("=" * 40)
                print(response)
                print("=" * 40)
                
            except Exception as e:
                error_msg = f"Error in research iteration {iteration + 1}: {e}"
                print(f"❌ {error_msg}")
                self.steps.append(error_msg)
        
        # Save research session
        self._save_research_session(topic, self.steps, self.tools_used)
        
        # Generate final summary
        final_summary = self._generate_final_summary(topic, self.steps)
        
        print("\n🎯 Research Complete!")
        print(f"📊 Tools Used: {', '.join(set(self.tools_used))}")
        print(f"📝 Steps Completed: {len(self.steps)}")
        
        return {
            "topic": topic,
            "steps": self.steps,
            "tools_used": self.tools_used,
            "summary": final_summary,
            "session_id": self.current_session["start_time"].isoformat()
        }
    
    def _generate_final_summary(self, topic: str, steps: List[str]):
        """Generate a final summary of the research session."""
        summary_prompt = f"""
{self._get_julius_persona_prompt()}

Please provide a clear, concise summary of the research conducted on "{topic}".

RESEARCH STEPS:
{chr(10).join(f"Step {i+1}: {step[:200]}..." for i, step in enumerate(steps))}

Create a summary that:
1. Highlights the key findings
2. Identifies the most important insights
3. Suggests practical applications
4. Notes any limitations or areas for further research
5. Uses simple, clear language with bullet points

Keep it concise but comprehensive.
"""
        
        try:
            return self.llm.predict(summary_prompt)
        except Exception as e:
            return f"Error generating summary: {e}"
    
    def get_feedback_stats(self):
        """Get feedback statistics for continuous improvement."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*), AVG(rating) FROM feedback")
        result = cursor.fetchone()
        
        cursor.execute("SELECT query, rating, notes FROM feedback ORDER BY timestamp DESC LIMIT 5")
        recent_feedback = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_feedback": result[0] or 0,
            "average_rating": result[1] or 0,
            "recent_feedback": recent_feedback
        }

def main():
    """Interactive Julius Research Agent."""
    print("🧠 Julius-Style Research Agent")
    print("=" * 50)
    
    try:
        agent = JuliusResearchAgent()
        
        while True:
            print("\nOptions:")
            print("1. Run research session")
            print("2. View feedback statistics")
            print("3. Exit")
            
            choice = input("\nChoose an option (1-3): ").strip()
            
            if choice == "1":
                topic = input("Enter research topic: ").strip()
                if not topic:
                    print("❌ Topic cannot be empty")
                    continue
                
                depth = input("Enter research depth (1-5, default 3): ").strip()
                depth = int(depth) if depth.isdigit() and 1 <= int(depth) <= 5 else 3
                
                context = input("Enter any additional context (optional): ").strip()
                
                result = agent.run_research(topic, depth, context)
                
                # Ask for feedback
                print("\n📊 Research Complete! How was this session?")
                rating = input("Rate 1-5 (5=excellent): ").strip()
                if rating.isdigit() and 1 <= int(rating) <= 5:
                    notes = input("Any additional notes (optional): ").strip()
                    agent._record_feedback(topic, result["summary"], int(rating), notes)
                    print("✅ Feedback recorded! Thank you!")
            
            elif choice == "2":
                stats = agent.get_feedback_stats()
                print("\n📊 Feedback Statistics:")
                print(f"   Total feedback: {stats['total_feedback']}")
                print(f"   Average rating: {stats['average_rating']:.1f}/5")
                
                if stats['recent_feedback']:
                    print("   Recent feedback:")
                    for query, rating, notes in stats['recent_feedback']:
                        print(f"     - '{query[:50]}...' (Rating: {rating}/5)")
            
            elif choice == "3":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure your OpenAI API key is set correctly in .env")

if __name__ == "__main__":
    main() 