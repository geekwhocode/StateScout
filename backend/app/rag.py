"""
Data Pipeline & Vector Storage Module
Handles the ingestion, cleaning, and structural chunking of web data.
Uses `trafilatura` to extract clean Markdown from URLs, and LangChain's 
`MarkdownHeaderTextSplitter` combined with a tiktoken `RecursiveCharacterTextSplitter` 
to maintain precise semantic context windows before embedding the vectors into PostgreSQL via pgvector.
"""

import trafilatura
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
import hashlib
import json
from app.config import settings
from typing import List, Dict

# Need google genai embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=settings.GOOGLE_API_KEY)

def fetch_and_parse(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return trafilatura.extract(downloaded, output_format="markdown")
    return ""

def chunk_document(markdown_text: str) -> List[Dict]:
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(markdown_text)

    # RecursiveCharacterTextSplitter with tiktoken
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=50
    )
    
    splits = text_splitter.split_documents(md_header_splits)
    
    chunks = []
    for doc in splits:
        chunk_hash = hashlib.sha256(doc.page_content.encode('utf-8')).hexdigest()
        parent_section = doc.metadata.get("Header 1") or doc.metadata.get("Header 2") or doc.metadata.get("Header 3") or "General"
        chunks.append({
            "content": doc.page_content,
            "hash": chunk_hash,
            "parent_section": parent_section
        })
    return chunks

# Note: In a real app we'd use async pg driver, but keeping it simple with sync PGVector for now.
# Langchain's PGVector is deprecated in favor of langchain_postgres but since pgvector was installed,
# we'll use the community integration for simplicity if it works, or raw psycopg2 if needed.
# Since the requirements explicitly mention pgvector, we can also use raw psycopg2.
import psycopg2

def store_chunks(url: str, chunks: List[Dict]):
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor()
    for chunk in chunks:
        # Generate embedding
        vector = embeddings.embed_query(chunk["content"])
        
        cursor.execute(
            """
            INSERT INTO research_chunks (source_url, chunk_hash, parent_section, content, embedding)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (url, chunk["hash"], chunk["parent_section"], chunk["content"], vector)
        )
    conn.commit()
    cursor.close()
    conn.close()

def search_chunks(query: str, top_k: int = 5) -> List[Dict]:
    vector = embeddings.embed_query(query)
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor()
    
    # Cosine distance
    cursor.execute(
        """
        SELECT source_url, parent_section, content, 1 - (embedding <=> %s::vector) as similarity
        FROM research_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (vector, vector, top_k)
    )
    results = []
    for row in cursor.fetchall():
        results.append({
            "source_url": row[0],
            "parent_section": row[1],
            "content": row[2],
            "similarity": row[3]
        })
    cursor.close()
    conn.close()
    return results
