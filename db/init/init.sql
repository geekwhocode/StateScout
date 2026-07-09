CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS research_chunks (
    id SERIAL PRIMARY KEY,
    source_url TEXT NOT NULL,
    chunk_hash TEXT NOT NULL,
    parent_section TEXT,
    content TEXT NOT NULL,
    embedding vector(1536), -- 1536 is standard for many models, though groq/gemini embeddings might differ (e.g. gemini is 768). Let's use 768 for gemini text-embedding-004.
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- We'll just define 768 as Gemini text-embedding-004 returns 768.
-- If we need flexibility, we can drop and recreate or alter later.
ALTER TABLE research_chunks ALTER COLUMN embedding TYPE vector(768);
