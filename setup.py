#!/usr/bin/env python3
"""
Setup script for Deep Research Agent
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Deep Research Agent - AI-powered research assistant"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="deep-research-agent",
    version="1.0.0",
    description="AI-powered research assistant with vector search and knowledge management",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Corey Alejandro",
    author_email="your.email@example.com",
    url="https://github.com/coreyalejandro/code-genie-deep-research-agent",
    packages=find_packages(),
    py_modules=[
        'qa_agent',
        'db_utils', 
        'init_db',
        'research_cli'
    ],
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'black',
            'ruff',
            'bandit',
            'safety'
        ],
        'dashboard': [
            'streamlit'
        ]
    },
    entry_points={
        'console_scripts': [
            'research=research_cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    include_package_data=True,
    package_data={
        "": ["*.sql", "*.md", "*.txt"],
    },
    keywords="ai research assistant vector-search knowledge-management openai langchain",
    project_urls={
        "Bug Reports": "https://github.com/coreyalejandro/code-genie-deep-research-agent/issues",
        "Source": "https://github.com/coreyalejandro/code-genie-deep-research-agent",
        "Documentation": "https://github.com/coreyalejandro/code-genie-deep-research-agent#readme",
    },
) 