# Agentic Research Platform

A production-grade, containerized AI Research Agent platform built for Ubuntu desktop environments. The platform leverages autonomous agents to take a research topic, decompose it, search the web, ingest/extract data into a vector database, and stream stateful updates to a modern React UI.

## Architecture & Tech Stack

- **Backend:** FastAPI with Server-Sent Events (SSE) streaming via Starlette.
- **Agent Framework:** LangGraph for stateful multi-actor graphs, coupled with LangChain.
- **LLM Gateway:** LiteLLM abstracted API supporting Gemini & Groq.
- **Data Pipeline:** `trafilatura` for clean markdown scraping, and `MarkdownHeaderTextSplitter` + `RecursiveCharacterTextSplitter` with `tiktoken` encoding.
- **Frontend:** React (Vite) + Tailwind CSS + React-Markdown (Dark mode styling).
- **Vector Database:** PostgreSQL + pgvector for embedded storage.
- **Evaluation:** Evaluated using `ragas` with mock business scenarios.

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js v20+

### Installation

1. Copy the reference environment file and update your keys:
   ```bash
   cp .env.example .env
   ```

2. Spin up the infrastructure via Docker:
   ```bash
   docker-compose up --build
   ```

3. **Seeding the Database:**
   To validate the pipeline without live search, seed the mock business data (Bank Employees & Shopping Store Data):
   ```bash
   docker-compose exec backend python seed.py
   ```

4. **Running Evaluation:**
   Execute the RAGAS framework tests:
   ```bash
   docker-compose exec backend python test_eval.py
   ```

### Manual Launch (Without Docker)

If you do not have Docker installed, you can run the services manually:

**1. Start the Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env .env
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**2. Start the Frontend:**
```bash
cd frontend
npm install
npm run dev -- --host --port 5174
```
*(Note: A PostgreSQL database instance with the `pgvector` extension must still be provided to the backend `DATABASE_URL` environment variable for vector operations to execute.)*

## References & Resources

- [Docker Setup & Ubuntu Dependencies [00:15:23]](https://example.com/docker-setup)
- [LiteLLM Integration Tutorial [00:42:10]](https://example.com/litellm)
- [PostgreSQL + pgvector configuration [01:05:45]](https://example.com/pgvector)
