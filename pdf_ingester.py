#!/usr/bin/env python3
"""
PDF Ingester for Deep Research Agent
Processes PDF files and adds them to the research database
"""

import sqlite3
from pathlib import Path
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PDFIngester:
    def __init__(self, db_path="knowledge.db"):
        self.db_path = db_path
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            print(f"📖 Processing {pdf_path.name} ({len(reader.pages)} pages)...")
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\n--- Page {page_num} ---\n{page_text}\n"
                
                # Progress indicator
                if page_num % 10 == 0:
                    print(f"   Processed {page_num}/{len(reader.pages)} pages...")
            
            return text.strip()
        except Exception as e:
            print(f"❌ Error processing {pdf_path}: {e}")
            return None
    
    def add_to_database(self, title, content, source_path=None):
        """Add extracted content to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create a summary (first 500 characters)
        summary = content[:500] + "..." if len(content) > 500 else content
        
        cursor.execute("""
            INSERT INTO knowledge (title, raw_text, summary, url)
            VALUES (?, ?, ?, ?)
        """, (title, content, summary, source_path))
        
        conn.commit()
        conn.close()
        print(f"✅ Added '{title}' to database")
    
    def process_pdf_file(self, pdf_path):
        """Process a single PDF file."""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            print(f"❌ File not found: {pdf_path}")
            return False
        
        if not pdf_path.suffix.lower() == '.pdf':
            print(f"❌ Not a PDF file: {pdf_path}")
            return False
        
        # Extract text
        content = self.extract_text_from_pdf(pdf_path)
        if not content:
            return False
        
        # Use filename as title (remove .pdf extension)
        title = pdf_path.stem
        
        # Add to database
        self.add_to_database(title, content, str(pdf_path))
        return True
    
    def process_directory(self, directory_path):
        """Process all PDF files in a directory."""
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return
        
        pdf_files = list(directory.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ No PDF files found in {directory}")
            return
        
        print(f"📚 Found {len(pdf_files)} PDF files to process:")
        for pdf_file in pdf_files:
            print(f"   - {pdf_file.name}")
        
        print("\n🚀 Starting processing...")
        successful = 0
        
        for pdf_file in pdf_files:
            if self.process_pdf_file(pdf_file):
                successful += 1
            print()  # Add spacing between files
        
        print(f"✅ Successfully processed {successful}/{len(pdf_files)} files!")
    
    def show_database_stats(self):
        """Show current database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM knowledge")
        total_entries = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM knowledge WHERE raw_text IS NOT NULL AND raw_text != ''")
        text_entries = cursor.fetchone()[0]
        
        cursor.execute("SELECT title FROM knowledge ORDER BY id DESC LIMIT 5")
        recent_entries = cursor.fetchall()
        
        conn.close()
        
        print("📊 Database Statistics:")
        print(f"   Total entries: {total_entries}")
        print(f"   Text entries: {text_entries}")
        print("   Recent entries:")
        for title, in recent_entries:
            print(f"     - {title}")

def main():
    ingester = PDFIngester()
    
    print("📚 PDF Ingester for Deep Research Agent")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Process a single PDF file")
        print("2. Process all PDFs in a directory")
        print("3. Show database statistics")
        print("4. Exit")
        
        choice = input("\nChoose an option (1-4): ").strip()
        
        if choice == "1":
            file_path = input("Enter PDF file path: ").strip()
            if file_path:
                ingester.process_pdf_file(file_path)
        
        elif choice == "2":
            dir_path = input("Enter directory path: ").strip()
            if dir_path:
                ingester.process_directory(dir_path)
        
        elif choice == "3":
            ingester.show_database_stats()
        
        elif choice == "4":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 