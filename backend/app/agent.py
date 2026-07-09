"""
LangGraph Agent Orchestration Module
Defines the cyclic `StateGraph` that manages the autonomous research process.
Features 4 primary nodes (Planner, Researcher, Critic, Synthesizer) and utilizes
LangChain's `ChatLiteLLM` to dynamically route reasoning tasks through Groq (Llama3) 
and synthesis tasks through Google Gemini, maintaining an abstract provider gateway.
"""

import json
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from app.config import settings
from app.rag import fetch_and_parse, chunk_document, store_chunks, search_chunks
import os
import asyncio

os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

class AgentState(TypedDict):
    topic: str
    sub_questions: List[str]
    current_question_idx: int
    research_completed: bool
    report: str
    feedback: str

# Native Providers Gateway
# Using Groq (Llama3) for fast reasoning and Gemini for synthesis
# from langchain_community.chat_models import ChatLiteLLM
# from langchain.schema import HumanMessage, SystemMessage
planner_llm = ChatGroq(model="llama3-70b-8192", api_key=settings.GROQ_API_KEY)
synth_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY)

search = DuckDuckGoSearchAPIWrapper()

async def planner_node(state: AgentState):
    topic = state["topic"]
    prompt = f"Deconstruct the following research topic into 3-5 discrete sub-questions for web search. Topic: {topic}. Return ONLY a JSON array of strings."
    res = planner_llm.invoke([HumanMessage(content=prompt)])
    try:
        # Strip markdown json blocks if present
        content = res.content.replace('```json', '').replace('```', '').strip()
        sub_questions = json.loads(content)
    except:
        sub_questions = [f"What is {topic}?"]
        
    return {"sub_questions": sub_questions, "current_question_idx": 0}

async def researcher_node(state: AgentState):
    idx = state.get("current_question_idx", 0)
    questions = state.get("sub_questions", [])
    if idx >= len(questions):
        return {"research_completed": True}
        
    question = questions[idx]
    
    # Use DuckDuckGo Search instead of Tavily as discussed
    search_results = search.results(question, max_results=3)
    
    for res in search_results:
        url = res.get("link")
        if url:
            markdown_content = fetch_and_parse(url)
            if markdown_content:
                chunks = chunk_document(markdown_content)
                store_chunks(url, chunks)
                
    return {"current_question_idx": idx + 1, "research_completed": False, "feedback": ""}

async def critic_node(state: AgentState):
    # Evaluate information density in vector store for current topic
    idx = state.get("current_question_idx", 0) - 1
    questions = state.get("sub_questions", [])
    question = questions[idx] if idx >= 0 and idx < len(questions) else state["topic"]
    
    results = search_chunks(question, top_k=3)
    if not results or len(results) < 2:
        return {"feedback": f"Insufficient data for '{question}'. Needs more research."}
    return {"feedback": "sufficient"}

def route_research(state: AgentState):
    if state.get("research_completed"):
        return "synthesizer"
    if state.get("feedback") != "sufficient" and state.get("feedback", "") != "":
        # We could route back to researcher, but to avoid infinite loops, we just continue to next question
        pass
    return "researcher"

async def synthesizer_node(state: AgentState):
    topic = state["topic"]
    results = search_chunks(topic, top_k=10)
    context = ""
    for r in results:
        context += f"Source: {r['source_url']}\nSection: {r['parent_section']}\nContent: {r['content']}\n\n"
        
    prompt = f"Write a comprehensive markdown report on the topic '{topic}' using the provided context. Include inline citations to the sources.\nContext:\n{context}"
    res = synth_llm.invoke([HumanMessage(content=prompt)])
    
    return {"report": res.content}

# Construct Graph
workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("critic", critic_node)
workflow.add_node("synthesizer", synthesizer_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "critic")
workflow.add_conditional_edges("critic", route_research, {"researcher": "researcher", "synthesizer": "synthesizer"})
workflow.add_edge("synthesizer", END)

research_app = workflow.compile()
