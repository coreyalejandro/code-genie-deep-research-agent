#!/usr/bin/env python3
"""
Julius Tool-Use System
Provides various tools for the Julius Research Agent to use during research
"""

import os
import json
import sqlite3
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JuliusTools:
    """
    Tool-use system for Julius Research Agent.
    Provides various tools that can be used during research sessions.
    """
    
    def __init__(self, db_path="knowledge.db"):
        self.db_path = db_path
        self.tool_usage_history = []
    
    def search_knowledge_base(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant documents with metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple keyword search (can be enhanced with vector search)
        cursor.execute("""
            SELECT title, summary, raw_text, url 
            FROM knowledge 
            WHERE (title LIKE ? OR summary LIKE ? OR raw_text LIKE ?)
            AND (raw_text IS NOT NULL AND raw_text != '')
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            title, summary, raw_text, url = row
            results.append({
                "title": title,
                "summary": summary,
                "content": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
                "url": url,
                "relevance_score": 0.8  # Placeholder for actual relevance scoring
            })
        
        conn.close()
        
        # Record tool usage
        self._record_tool_usage("search_knowledge_base", query, len(results))
        
        return results
    
    def summarize_text(self, text: str, max_length: int = 300) -> str:
        """
        Summarize a given text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        if len(text) <= max_length:
            return text
        
        # Simple summarization (can be enhanced with AI)
        sentences = text.split('. ')
        summary = '. '.join(sentences[:3]) + '.'
        
        if len(summary) > max_length:
            summary = summary[:max_length-3] + '...'
        
        self._record_tool_usage("summarize_text", f"Length: {len(text)}", len(summary))
        
        return summary
    
    def create_visualization(self, data: Dict[str, Any], chart_type: str = "bar") -> str:
        """
        Create a visualization of data.
        
        Args:
            data: Data to visualize
            chart_type: Type of chart (bar, line, pie)
            
        Returns:
            Path to saved visualization
        """
        try:
            # Create output directory
            output_dir = Path("visualizations")
            output_dir.mkdir(exist_ok=True)
            
            # Generate sample data if none provided
            if not data:
                data = {
                    "Research Topics": ["Machine Learning", "JavaScript", "React", "Data Science"],
                    "Document Count": [15, 12, 8, 10]
                }
            
            # Create visualization
            plt.figure(figsize=(10, 6))
            
            if chart_type == "bar":
                plt.bar(data.keys(), data.values())
                plt.title("Research Data Visualization")
                plt.xlabel("Categories")
                plt.ylabel("Count")
            elif chart_type == "pie":
                plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
                plt.title("Research Data Distribution")
            elif chart_type == "line":
                plt.plot(list(data.keys()), list(data.values()))
                plt.title("Research Trends")
                plt.xlabel("Time")
                plt.ylabel("Count")
            
            plt.tight_layout()
            
            # Save visualization
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"visualization_{chart_type}_{timestamp}.png"
            filepath = output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            self._record_tool_usage("create_visualization", chart_type, str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            return f"Error creating visualization: {e}"
    
    def get_research_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the research database.
        
        Returns:
            Dictionary with various statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get basic statistics
        cursor.execute("SELECT COUNT(*) FROM knowledge")
        total_documents = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM knowledge WHERE raw_text IS NOT NULL AND raw_text != ''")
        text_documents = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM research_sessions")
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_feedback = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute("""
            SELECT topic, timestamp 
            FROM research_sessions 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        recent_sessions = cursor.fetchall()
        
        # Get feedback statistics
        cursor.execute("SELECT AVG(rating) FROM feedback")
        avg_rating = cursor.fetchone()[0] or 0
        
        conn.close()
        
        stats = {
            "total_documents": total_documents,
            "text_documents": text_documents,
            "total_research_sessions": total_sessions,
            "total_feedback": total_feedback,
            "average_rating": round(avg_rating, 2),
            "recent_sessions": recent_sessions,
            "database_size_mb": round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
        }
        
        self._record_tool_usage("get_research_statistics", "stats", len(stats))
        
        return stats
    
    def export_research_report(self, topic: str, format: str = "json") -> str:
        """
        Export a research report for a given topic.
        
        Args:
            topic: Research topic
            format: Export format (json, txt, md)
            
        Returns:
            Path to exported report
        """
        try:
            # Get research sessions for the topic
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT topic, steps, tools_used, timestamp 
                FROM research_sessions 
                WHERE topic LIKE ? 
                ORDER BY timestamp DESC
            """, (f'%{topic}%',))
            
            sessions = cursor.fetchall()
            
            # Get relevant documents
            cursor.execute("""
                SELECT title, summary 
                FROM knowledge 
                WHERE (title LIKE ? OR summary LIKE ?)
                AND summary IS NOT NULL AND summary != ''
            """, (f'%{topic}%', f'%{topic}%'))
            
            documents = cursor.fetchall()
            conn.close()
            
            # Create report data
            report_data = {
                "topic": topic,
                "export_date": datetime.now().isoformat(),
                "sessions": [
                    {
                        "topic": session[0],
                        "steps": json.loads(session[1]) if session[1] else [],
                        "tools_used": json.loads(session[2]) if session[2] else [],
                        "timestamp": session[3]
                    }
                    for session in sessions
                ],
                "relevant_documents": [
                    {
                        "title": doc[0],
                        "summary": doc[1]
                    }
                    for doc in documents
                ]
            }
            
            # Create output directory
            output_dir = Path("reports")
            output_dir.mkdir(exist_ok=True)
            
            # Export based on format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_report_{topic.replace(' ', '_')}_{timestamp}"
            
            if format == "json":
                filepath = output_dir / f"{filename}.json"
                with open(filepath, 'w') as f:
                    json.dump(report_data, f, indent=2)
            
            elif format == "txt":
                filepath = output_dir / f"{filename}.txt"
                with open(filepath, 'w') as f:
                    f.write(f"Research Report: {topic}\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    f.write("RESEARCH SESSIONS:\n")
                    for session in report_data["sessions"]:
                        f.write(f"\nSession: {session['topic']}\n")
                        f.write(f"Date: {session['timestamp']}\n")
                        f.write(f"Tools Used: {', '.join(session['tools_used'])}\n")
                        f.write("Steps:\n")
                        for i, step in enumerate(session['steps'], 1):
                            f.write(f"  {i}. {step[:200]}...\n")
                    
                    f.write("\nRELEVANT DOCUMENTS:\n")
                    for doc in report_data["relevant_documents"]:
                        f.write(f"\n- {doc['title']}\n")
                        f.write(f"  {doc['summary'][:200]}...\n")
            
            elif format == "md":
                filepath = output_dir / f"{filename}.md"
                with open(filepath, 'w') as f:
                    f.write(f"# Research Report: {topic}\n\n")
                    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    f.write("## Research Sessions\n\n")
                    for session in report_data["sessions"]:
                        f.write(f"### {session['topic']}\n\n")
                        f.write(f"**Date:** {session['timestamp']}\n\n")
                        f.write(f"**Tools Used:** {', '.join(session['tools_used'])}\n\n")
                        f.write("**Steps:**\n\n")
                        for i, step in enumerate(session['steps'], 1):
                            f.write(f"{i}. {step[:200]}...\n\n")
                    
                    f.write("## Relevant Documents\n\n")
                    for doc in report_data["relevant_documents"]:
                        f.write(f"### {doc['title']}\n\n")
                        f.write(f"{doc['summary'][:200]}...\n\n")
            
            self._record_tool_usage("export_research_report", f"{topic}_{format}", str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            return f"Error exporting report: {e}"
    
    def _record_tool_usage(self, tool_name: str, input_data: str, output_data: str):
        """Record tool usage for analytics."""
        usage = {
            "tool": tool_name,
            "input": input_data,
            "output": output_data,
            "timestamp": datetime.now().isoformat()
        }
        self.tool_usage_history.append(usage)
    
    def get_tool_usage_analytics(self) -> Dict[str, Any]:
        """Get analytics about tool usage."""
        tool_counts = {}
        for usage in self.tool_usage_history:
            tool = usage["tool"]
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        return {
            "total_tool_uses": len(self.tool_usage_history),
            "tool_breakdown": tool_counts,
            "recent_usage": self.tool_usage_history[-10:] if self.tool_usage_history else []
        }

def main():
    """Test the Julius Tools system."""
    print("🔧 Julius Tools System")
    print("=" * 40)
    
    tools = JuliusTools()
    
    while True:
        print("\nAvailable Tools:")
        print("1. Search Knowledge Base")
        print("2. Summarize Text")
        print("3. Create Visualization")
        print("4. Get Research Statistics")
        print("5. Export Research Report")
        print("6. View Tool Analytics")
        print("7. Exit")
        
        choice = input("\nChoose a tool (1-7): ").strip()
        
        if choice == "1":
            query = input("Enter search query: ").strip()
            if query:
                results = tools.search_knowledge_base(query)
                print(f"\nFound {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['title']}")
                    print(f"   {result['summary'][:100]}...")
        
        elif choice == "2":
            text = input("Enter text to summarize: ").strip()
            if text:
                summary = tools.summarize_text(text)
                print(f"\nSummary: {summary}")
        
        elif choice == "3":
            print("Creating sample visualization...")
            data = {"A": 10, "B": 20, "C": 15, "D": 25}
            chart_type = input("Chart type (bar/pie/line): ").strip() or "bar"
            filepath = tools.create_visualization(data, chart_type)
            print(f"Visualization saved to: {filepath}")
        
        elif choice == "4":
            stats = tools.get_research_statistics()
            print("\n📊 Research Statistics:")
            print(f"   Total Documents: {stats['total_documents']}")
            print(f"   Text Documents: {stats['text_documents']}")
            print(f"   Research Sessions: {stats['total_research_sessions']}")
            print(f"   Total Feedback: {stats['total_feedback']}")
            print(f"   Average Rating: {stats['average_rating']}/5")
            print(f"   Database Size: {stats['database_size_mb']} MB")
        
        elif choice == "5":
            topic = input("Enter research topic: ").strip()
            if topic:
                format_choice = input("Export format (json/txt/md): ").strip() or "json"
                filepath = tools.export_research_report(topic, format_choice)
                print(f"Report exported to: {filepath}")
        
        elif choice == "6":
            analytics = tools.get_tool_usage_analytics()
            print("\n🔧 Tool Usage Analytics:")
            print(f"   Total Tool Uses: {analytics['total_tool_uses']}")
            print("   Tool Breakdown:")
            for tool, count in analytics['tool_breakdown'].items():
                print(f"     - {tool}: {count} uses")
        
        elif choice == "7":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 