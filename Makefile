# Deep Research Agent Makefile
# Simplifies common development and deployment tasks

.PHONY: help install setup test run clean db-init db-reset lint format

# Default target
help:
	@echo "Deep Research Agent - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install    - Install Python dependencies"
	@echo "  make setup      - Initialize database and setup environment"
	@echo ""
	@echo "Development:"
	@echo "  make run        - Run the QA agent"
	@echo "  make test       - Run tests (placeholder)"
	@echo "  make lint       - Run linting checks"
	@echo "  make format     - Format code with black"
	@echo ""
	@echo "Database:"
	@echo "  make db-init    - Initialize database with schema"
	@echo "  make db-reset   - Reset database (WARNING: deletes all data)"
	@echo "  make db-show    - Show current database schema"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean      - Clean up temporary files"
	@echo "  make help       - Show this help message"

# Installation
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

setup: install db-init
	@echo "🔧 Setup complete! Don't forget to:"
	@echo "   1. Copy .env.example to .env"
	@echo "   2. Add your OpenAI API key to .env"

# Development
run:
	@echo "🚀 Starting Deep Research Agent..."
	python qa_agent.py

test:
	@echo "🧪 Running tests..."
	@echo "⚠️  Tests not implemented yet"
	@echo "   Run 'make run' to test the agent manually"

# Code quality
lint:
	@echo "🔍 Running linting checks..."
	@echo "Checking Python files..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check .; \
	else \
		echo "⚠️  Ruff not installed. Install with: pip install ruff"; \
	fi
	@echo "Checking markdown files..."
	@if command -v markdownlint >/dev/null 2>&1; then \
		markdownlint *.md; \
	else \
		echo "⚠️  markdownlint not installed. Install with: npm install -g markdownlint-cli"; \
	fi

format:
	@echo "🎨 Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black .; \
	else \
		echo "⚠️  Black not installed. Install with: pip install black"; \
	fi

# Database operations
db-init:
	@echo "🗄️  Initializing database..."
	python db_utils.py

db-reset:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "🗑️  Resetting database..."
	python -c "from db_utils import DatabaseManager; DatabaseManager().reset_database()"

db-show:
	@echo "📊 Showing database schema..."
	python -c "from db_utils import show_schema; show_schema()"

# Maintenance
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	@echo "✅ Cleanup complete!"

# Quick development workflow
dev: lint format test
	@echo "✅ Development checks complete!"

# Deployment helpers
deploy-check: lint test
	@echo "✅ Ready for deployment!"

# Research CLI
research:
	@echo "🔍 Research CLI available!"
	@echo "   Install with: pip install -e ."
	@echo "   Then use: research <command>"
	@echo ""
	@echo "Available commands:"
	@echo "  research setup      - Set up environment"
	@echo "  research run        - Start QA agent"
	@echo "  research db-init    - Initialize database"
	@echo "  research ingest-pdf - Add PDF files to database"
	@echo "  research db-show    - Show schema"
	@echo "  research dashboard  - Start web dashboard"

install-cli:
	@echo "📦 Installing CLI..."
	pip install -e .
	@echo "✅ CLI installed! Use 'research --help' for commands" 