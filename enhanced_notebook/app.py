#!/usr/bin/env python3
"""
Enhanced Notebook - Your Personal Research Workspace
Like NotebookLM but with your own research agent integration
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import threading
import time

# Import your research agent
from julius_researcher import JuliusResearchAgent
from julius_tools import JuliusTools

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

class EnhancedNotebook:
    def __init__(self, db_path="knowledge.db"):
        self.db_path = db_path
        self.research_agent = JuliusResearchAgent(db_path)
        self.tools = JuliusTools(db_path)
        self.active_sessions = {}
        self.notebook_data = self.load_notebook_data()
    
    def load_notebook_data(self):
        """Load notebook data from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create notebook tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notebook_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                page_type TEXT DEFAULT 'note',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notebook_research (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                sources TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES notebook_pages (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        return self.get_all_pages()
    
    def get_all_pages(self):
        """Get all notebook pages."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, content, page_type, created_at, updated_at 
            FROM notebook_pages 
            ORDER BY updated_at DESC
        """)
        
        pages = []
        for row in cursor.fetchall():
            page_id, title, content, page_type, created_at, updated_at = row
            
            # Get research for this page
            cursor.execute("""
                SELECT query, response, sources 
                FROM notebook_research 
                WHERE page_id = ? 
                ORDER BY created_at DESC
            """, (page_id,))
            
            research = []
            for r_row in cursor.fetchall():
                research.append({
                    "query": r_row[0],
                    "response": r_row[1],
                    "sources": r_row[2]
                })
            
            pages.append({
                "id": page_id,
                "title": title,
                "content": content,
                "page_type": page_type,
                "created_at": created_at,
                "updated_at": updated_at,
                "research": research
            })
        
        conn.close()
        return pages
    
    def create_page(self, title, content="", page_type="note"):
        """Create a new notebook page."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notebook_pages (title, content, page_type)
            VALUES (?, ?, ?)
        """, (title, content, page_type))
        
        page_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Reload notebook data
        self.notebook_data = self.get_all_pages()
        return page_id
    
    def update_page(self, page_id, title, content):
        """Update a notebook page."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE notebook_pages 
            SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title, content, page_id))
        
        conn.commit()
        conn.close()
        
        # Reload notebook data
        self.notebook_data = self.get_all_pages()
    
    def add_research(self, page_id, query, response, sources=None):
        """Add research to a notebook page."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notebook_research (page_id, query, response, sources)
            VALUES (?, ?, ?, ?)
        """, (page_id, query, response, json.dumps(sources) if sources else None))
        
        conn.commit()
        conn.close()
        
        # Reload notebook data
        self.notebook_data = self.get_all_pages()
    
    def run_research(self, query, context=""):
        """Run research using the Julius agent."""
        try:
            result = self.research_agent.run_research(query, depth=2, user_context=context)
            return result
        except Exception as e:
            return {
                "error": str(e),
                "topic": query,
                "steps": [],
                "tools_used": [],
                "summary": f"Error: {e}"
            }

# Initialize the notebook
notebook = EnhancedNotebook()

@app.route('/')
def index():
    """Main notebook interface."""
    return render_template('index.html', pages=notebook.notebook_data)

@app.route('/api/pages', methods=['GET'])
def get_pages():
    """Get all notebook pages."""
    return jsonify(notebook.notebook_data)

@app.route('/api/pages', methods=['POST'])
def create_page():
    """Create a new notebook page."""
    data = request.json
    title = data.get('title', 'Untitled')
    content = data.get('content', '')
    page_type = data.get('page_type', 'note')
    
    page_id = notebook.create_page(title, content, page_type)
    
    # Emit to all connected clients
    socketio.emit('page_created', {
        'page_id': page_id,
        'title': title,
        'content': content,
        'page_type': page_type
    })
    
    return jsonify({'success': True, 'page_id': page_id})

@app.route('/api/pages/<int:page_id>', methods=['PUT'])
def update_page(page_id):
    """Update a notebook page."""
    data = request.json
    title = data.get('title', 'Untitled')
    content = data.get('content', '')
    
    notebook.update_page(page_id, title, content)
    
    # Emit to all connected clients
    socketio.emit('page_updated', {
        'page_id': page_id,
        'title': title,
        'content': content
    })
    
    return jsonify({'success': True})

@app.route('/api/research', methods=['POST'])
def run_research():
    """Run research using the Julius agent."""
    data = request.json
    query = data.get('query', '')
    context = data.get('context', '')
    page_id = data.get('page_id')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Run research in a background thread
    def research_task():
        try:
            result = notebook.run_research(query, context)
            
            # Add to notebook if page_id provided
            if page_id and result.get('summary'):
                notebook.add_research(
                    page_id, 
                    query, 
                    result['summary'], 
                    result.get('tools_used', [])
                )
            
            # Emit result to client
            socketio.emit('research_complete', {
                'query': query,
                'result': result,
                'page_id': page_id
            })
            
        except Exception as e:
            socketio.emit('research_error', {
                'query': query,
                'error': str(e)
            })
    
    thread = threading.Thread(target=research_task)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Research started'})

@app.route('/api/tools/stats', methods=['GET'])
def get_stats():
    """Get research statistics."""
    stats = notebook.tools.get_research_statistics()
    return jsonify(stats)

@app.route('/api/tools/export/<int:page_id>', methods=['POST'])
def export_page(page_id):
    """Export a notebook page."""
    data = request.json
    format_type = data.get('format', 'json')
    
    # Find the page
    page = None
    for p in notebook.notebook_data:
        if p['id'] == page_id:
            page = p
            break
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    try:
        filepath = notebook.tools.export_research_report(
            page['title'], 
            format_type
        )
        return jsonify({'success': True, 'filepath': filepath})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to Enhanced Notebook'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"Client disconnected: {request.sid}")

if __name__ == '__main__':
    print("🧠 Starting Enhanced Notebook...")
    print("📚 Your personal research workspace")
    print("🌐 Open http://localhost:5000 in your browser")
    print("=" * 50)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 