# Deep Research Agent Setup Guide

## Quick Setup

### 1. Set up your OpenAI API Key

You need to create a `.env` file in the project root with your OpenAI API key:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file and replace with your actual API key
# OPENAI_API_KEY=your-actual-api-key-here
```

**To get your OpenAI API key:**

1. Go to [OpenAI API Keys](https://platform.openai.com/account/api-keys)
2. Click "Create new secret key"
3. Copy the key and paste it in your `.env` file

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Test the QA Agent

```bash
python qa_agent.py
```

## What Was Fixed

✅ **Updated LangChain imports** - Now using the correct package structure:

- `langchain_openai` for OpenAI components
- `langchain_community` for vector stores
- `langchain` for core components

✅ **Fixed API key loading** - Now properly loads from `.env` file

✅ **Updated requirements.txt** - Added all necessary packages

## Troubleshooting

If you get an authentication error:

1. Make sure your `.env` file exists
2. Check that your API key is correct
3. Ensure there are no extra spaces in the `.env` file

If you get import errors:

1. Run `pip install -r requirements.txt` again
2. Make sure you're using Python 3.8+ (recommended: 3.11+)
