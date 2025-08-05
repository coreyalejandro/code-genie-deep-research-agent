import sqlite3
import os

def init_database():
    """Initialize the database using the schema_sqlite.sql file"""
    
    # Connect to database
    conn = sqlite3.connect("knowledge.db")
    cursor = conn.cursor()
    
    # Read and execute schema_sqlite.sql
    schema_file = "schema_sqlite.sql"
    if os.path.exists(schema_file):
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = schema_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"✅ Executed: {statement[:50]}...")
                except sqlite3.OperationalError as e:
                    if "already exists" in str(e):
                        print(f"ℹ️  Table already exists: {statement[:50]}...")
                    else:
                        print(f"⚠️  Error: {e}")
    else:
        print(f"❌ Schema file {schema_file} not found!")
        return False
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully!")
    return True

if __name__ == "__main__":
    init_database()
