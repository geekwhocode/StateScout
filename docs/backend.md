# Backend Documentation

The backend of the Agentic Research Platform is a stateful orchestration layer built with **FastAPI**, **LangChain**, and **LangGraph**. It manages API endpoints, real-time event streams, embedded vector storage, and autonomous LLM routing.

## 1. Core Architecture

- **Web Framework:** FastAPI (with `sse-starlette` for Server-Sent Events).
- **Agent Orchestrator:** LangGraph.
- **LLM Gateway:** LiteLLM (accessed via LangChain's `ChatLiteLLM`).
- **Database:** PostgreSQL with `pgvector` extension.
- **Scraper & Chunker:** `trafilatura` and LangChain's `MarkdownHeaderTextSplitter` + `RecursiveCharacterTextSplitter`.

---

## 2. API Endpoints (`app/main.py`)

### `POST /api/research`
Initiates a new research task or resumes a session.
- **Payload Schema:**
  ```json
  {
    "topic": "string",
    "session_id": "string",
    "api_key": "string | null",
    "provider": "string | null"
  }
  ```
- **Logic:** Evaluates the `session_id` against an in-memory ledger. If the user provides a `provider` and `api_key`, it dynamically sets the backend environment variables (`GEMINI_API_KEY` or `GROQ_API_KEY`) and overrides the 3-credit restriction. Otherwise, it subtracts 1 credit and returns `403 CREDIT_EXHAUSTED` if none remain.

### `GET /api/stream/{topic}`
Consumes the LangGraph execution stream via Server-Sent Events (SSE).
- **Yields:** JSON strings representing the state of the active node.
- **Events:** `update`, `done`, `error`.

---

## 3. The LangGraph Agent (`app/agent.py`)

The graph runs on an `AgentState` schema defining the `topic`, `sub_questions`, current progress index, and the final `report`.

### Graph Nodes:
1. **`planner_node`:**
   - **LLM:** Groq (Llama3-70b).
   - **Role:** Deconstructs the core `topic` into 3-5 specific search queries.
2. **`researcher_node`:**
   - **Tools:** DuckDuckGoSearchAPIWrapper, `trafilatura`.
   - **Role:** Iterates over the sub-questions, executes web searches, downloads site HTML, converts it to Markdown, and passes it to the RAG pipeline.
3. **`critic_node`:**
   - **Role:** Queries the vector database (`pgvector`) to ensure enough contextual data was extracted. Calculates similarity and decides whether to route back for more research or proceed to synthesis.
4. **`synthesizer_node`:**
   - **LLM:** Google Gemini 1.5 Pro.
   - **Role:** Performs a top-K semantic search against the accumulated vectors and generates the final, heavily cited Markdown report.

---

## 4. The Data Pipeline (`app/rag.py`)

### Web Scraping
- Utilizes `trafilatura` to strip boilerplate, navbars, and sidebars from URLs, outputting clean, highly readable Markdown.

### Semantic Chunking
- **Step 1:** Uses `MarkdownHeaderTextSplitter` to separate content strictly by markdown headers (`#`, `##`, `###`), preserving contextual themes (e.g., keeping "Dress Code" sections together).
- **Step 2:** Uses `RecursiveCharacterTextSplitter.from_tiktoken_encoder` to cleanly fit chunks into a specific 500-token limit without severing mid-word.

### Vector Storage
- Connects to Postgres via `psycopg2`.
- Embeds text using `GoogleGenerativeAIEmbeddings` (default 768 dimensions for Gemini).
- Performs Cosine distance similarity queries (`<=>`) natively in PostgreSQL using the `pgvector` extension.
