"""
Database utilities for the Deep Research Agent
Makes schema management more tractable and organized
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """Manages database operations and schema"""
    
    def __init__(self, db_path: str = "knowledge.db"):
        self.db_path = db_path
        self.schema_file = "schema_sqlite.sql"
    
    def init_database(self) -> bool:
        """Initialize database using schema_sqlite.sql"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if not os.path.exists(self.schema_file):
                print(f"❌ Schema file {self.schema_file} not found!")
                return False
            
            # Read and execute schema
            with open(self.schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Execute each statement
            statements = [s.strip() for s in schema_sql.split(';') if s.strip() and not s.startswith('--')]
            
            for statement in statements:
                try:
                    cursor.execute(statement)
                    print(f"✅ Executed: {statement[:50]}...")
                except sqlite3.OperationalError as e:
                    if "already exists" in str(e):
                        print(f"ℹ️  Table already exists")
                    else:
                        print(f"⚠️  Error: {e}")
            
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
    
    def get_table_info(self, table_name: str = "knowledge") -> List[Dict[str, Any]]:
        """Get information about table structure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                "name": col[1],
                "type": col[2],
                "not_null": bool(col[3]),
                "default": col[4],
                "primary_key": bool(col[5])
            }
            for col in columns
        ]
    
    def list_tables(self) -> List[str]:
        """List all tables in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tables
    
    def reset_database(self) -> bool:
        """Reset database by dropping all tables and reinitializing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            tables = self.list_tables()
            
            # Drop all tables
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"🗑️  Dropped table: {table}")
            
            conn.commit()
            conn.close()
            
            # Reinitialize
            return self.init_database()
            
        except Exception as e:
            print(f"❌ Database reset failed: {e}")
            return False

# Convenience functions
def init_db():
    """Initialize the database"""
    db = DatabaseManager()
    return db.init_database()

def show_schema():
    """Show current database schema"""
    db = DatabaseManager()
    tables = db.list_tables()
    
    print("📊 Current Database Schema:")
    print("=" * 40)
    
    for table in tables:
        print(f"\n📋 Table: {table}")
        columns = db.get_table_info(table)
        for col in columns:
            pk = " (PK)" if col["primary_key"] else ""
            nn = " NOT NULL" if col["not_null"] else ""
            default = f" DEFAULT {col['default']}" if col["default"] else ""
            print(f"  - {col['name']}: {col['type']}{pk}{nn}{default}")

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Show schema
    show_schema() 