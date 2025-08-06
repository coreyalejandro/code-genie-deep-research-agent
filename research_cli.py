#!/usr/bin/env python3
"""
Deep Research Agent CLI
A command-line interface for the research agent
"""

import argparse
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_setup():
    """Check if the environment is properly set up"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Run: cp .env.example .env")
        print("   Then add your OpenAI API key to .env")
        return False
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your-actual-api-key-here':
        print("❌ OpenAI API key not configured!")
        print("   Add your API key to .env file")
        return False
    
    return True

def run_qa_agent():
    """Run the interactive QA agent"""
    if not check_setup():
        return 1
    
    print("🧠 Starting Deep Research Agent...")
    try:
        # Import and run the qa_agent module
        import qa_agent  # noqa: F401 - Import needed to trigger main block
        # The qa_agent.py will run its main block when imported
        return 0
    except Exception as e:
        print(f"❌ Error starting QA agent: {e}")
        return 1

def init_database():
    """Initialize the database"""
    print("🗄️  Initializing database...")
    try:
        from db_utils import init_db
        success = init_db()
        if success:
            print("✅ Database initialized successfully!")
            return 0
        else:
            print("❌ Database initialization failed!")
            return 1
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return 1

def show_schema():
    """Show the current database schema"""
    print("📊 Database Schema:")
    try:
        from db_utils import show_schema
        show_schema()
        return 0
    except Exception as e:
        print(f"❌ Error showing schema: {e}")
        return 1

def reset_database():
    """Reset the database (with confirmation)"""
    print("⚠️  WARNING: This will delete all data!")
    confirm = input("Are you sure? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Database reset cancelled.")
        return 0
    
    print("🗑️  Resetting database...")
    try:
        from db_utils import DatabaseManager
        db = DatabaseManager()
        success = db.reset_database()
        if success:
            print("✅ Database reset successfully!")
            return 0
        else:
            print("❌ Database reset failed!")
            return 1
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return 1

def setup_environment():
    """Set up the environment"""
    print("🔧 Setting up environment...")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("📋 Creating .env from .env.example...")
            os.system('cp .env.example .env')
            print("✅ .env file created!")
            print("   Please edit .env and add your OpenAI API key")
        else:
            print("❌ .env.example not found!")
            return 1
    
    # Initialize database
    db_result = init_database()
    if db_result != 0:
        return db_result
    
    print("✅ Environment setup complete!")
    print("   Don't forget to add your OpenAI API key to .env")
    return 0

def run_dashboard():
    """Run the dashboard"""
    if not check_setup():
        return 1
    
    print("📊 Starting dashboard...")
    try:
        import importlib.util
        if importlib.util.find_spec("streamlit") is None:
            print("❌ Streamlit not installed!")
            print("   Install with: pip install streamlit")
            return 1
        
        os.system('streamlit run dashboard.py')
        return 0
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return 1

def run_pdf_ingester():
    """Run the PDF ingester"""
    print("📚 Starting PDF Ingester...")
    try:
        from pdf_ingester import main as pdf_main
        pdf_main()
        return 0
    except Exception as e:
        print(f"❌ Error starting PDF ingester: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(
        description="Deep Research Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  research setup          # Set up environment
  research run            # Start interactive QA agent
  research db-init        # Initialize database
  research db-show        # Show database schema
  research ingest-pdf     # Add PDF files to database
  research dashboard      # Start web dashboard
        """
    )
    
    parser.add_argument(
        'command',
        choices=['setup', 'run', 'db-init', 'db-show', 'db-reset', 'dashboard', 'ingest-pdf', 'help'],
        help='Command to run'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Deep Research Agent CLI v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Command routing
    if args.command == 'setup':
        return setup_environment()
    elif args.command == 'run':
        return run_qa_agent()
    elif args.command == 'db-init':
        return init_database()
    elif args.command == 'db-show':
        return show_schema()
    elif args.command == 'db-reset':
        return reset_database()
    elif args.command == 'dashboard':
        return run_dashboard()
    elif args.command == 'ingest-pdf':
        return run_pdf_ingester()
    elif args.command == 'help':
        parser.print_help()
        return 0

if __name__ == '__main__':
    sys.exit(main()) 