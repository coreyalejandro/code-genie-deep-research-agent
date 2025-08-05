-- Deep Research Agent Database Schema (SQLite)
-- This file contains the database schema for the research agent

-- Knowledge table for storing research documents
CREATE TABLE knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT,
    raw_text TEXT,
    summary TEXT,
    cluster_label INTEGER DEFAULT 0,
    depth INTEGER DEFAULT 1
);

-- Research sessions tracking
CREATE TABLE research_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT NOT NULL,
    query TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
); 