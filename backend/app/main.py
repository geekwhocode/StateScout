"""
Agentic Research Platform - Main API Gateway
This module initializes the FastAPI application, manages CORS for the frontend,
and defines the core endpoints for initiating research sessions and streaming
real-time SSE (Server-Sent Events) from the LangGraph agent.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from app.agent import research_app
from app.config import settings
import json
import asyncio
import os

app = FastAPI(title="Agentic Research Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session tracking for 3 free credits
session_credits = {}

class ResearchRequest(BaseModel):
    topic: str
    session_id: str
    api_key: str | None = None
    provider: str | None = None

@app.post("/api/research")
async def start_research(req: ResearchRequest):
    """
    Initializes a research task and manages the Bring Your Own Key (BYOK) monetization model.
    By default, anonymous sessions receive exactly 3 free credits. If the credits are exhausted,
    the user is required to supply a valid API Key and Provider, which dynamically updates
    the backend environment execution variables for the duration of their requests.
    """
    # Check BYOK logic
    credits = session_credits.get(req.session_id, 3)
    
    if req.api_key and req.provider:
        # User provided key, update environment dynamically for this session
        if req.provider.lower() == "google":
            os.environ["GEMINI_API_KEY"] = req.api_key
        elif req.provider.lower() == "groq":
            os.environ["GROQ_API_KEY"] = req.api_key
        # Free pass when key provided
        pass
    else:
        if credits <= 0:
            raise HTTPException(status_code=403, detail="CREDIT_EXHAUSTED")
        session_credits[req.session_id] = credits - 1

    return {"status": "started", "remaining_credits": session_credits.get(req.session_id, 0) if not req.api_key else "unlimited"}

@app.get("/api/stream/{topic}")
async def stream_research(topic: str):
    """
    Consumes the asynchronous state stream emitted by the LangGraph cyclic agent.
    Yields JSON events over an SSE (Server-Sent Events) connection, allowing the frontend
    React interface to build a live 'terminal-like' HUD of the agent's thought process
    and node transitions.
    """
    async def event_generator():
        try:
            # Stream events from LangGraph
            # LangGraph's astream yields (node_name, node_state)
            async for output in research_app.astream({"topic": topic}):
                for node_name, state in output.items():
                    event_data = {
                        "node": node_name,
                        "state": {k: v for k, v in state.items() if k != "topic"} # Filter to avoid sending whole state
                    }
                    yield {
                        "event": "update",
                        "data": json.dumps(event_data)
                    }
                await asyncio.sleep(0.5) # Slight delay for UI visualization effect
            yield {
                "event": "done",
                "data": json.dumps({"status": "completed"})
            }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"detail": str(e)})
            }
            
    return EventSourceResponse(event_generator())
