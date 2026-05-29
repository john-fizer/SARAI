from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime, timezone
from bson import ObjectId
import os
import asyncio
import json
import re
import base64
import httpx
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.llm.openai import OpenAITextToSpeech

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="SARAI Jarvis 3.0 — Second Brain")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_FRONTEND_ORIGIN = os.environ.get("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[_FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_API_KEY = os.environ.get("API_KEY", "")


def _check_api_key(request: Request):
    if request.headers.get("X-API-Key") != _API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# MongoDB
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
_client = AsyncIOMotorClient(MONGO_URL)
db = _client[DB_NAME]
thoughts_col = db.thoughts
connections_col = db.connections

# ChromaDB — persistent local vector store for semantic memory
_chroma_client = chromadb.PersistentClient(
    path=os.path.join(os.path.dirname(__file__), ".chromadb"),
    settings=Settings(anonymized_telemetry=False),
)
_chroma_col = _chroma_client.get_or_create_collection(
    name="thoughts",
    metadata={"hnsw:space": "cosine"},
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def doc_to_dict(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


def select_model(content: str) -> tuple:
    """Context-aware model routing."""
    lo = content.lower()
    wc = len(content.split())
    if any(k in lo for k in ["analyze", "why", "explain", "reflect", "understand", "reason", "think deeply"]):
        return "anthropic", "claude-sonnet-4-5", "Analyst"
    if any(k in lo for k in ["plan", "strategy", "goal", "future", "optimize", "roadmap"]):
        return "anthropic", "claude-sonnet-4-5", "Strategist"
    if any(k in lo for k in ["feel", "emotion", "fear", "hope", "dream", "love", "hate"]):
        return "anthropic", "claude-sonnet-4-5", "Emotional Interpreter"
    if wc < 6:
        return "openai", "gpt-4.1-mini", "Memory Curator"
    return "openai", "gpt-4.1", "Analyst"


# ── Agent Definitions ─────────────────────────────────────────────────────────

AGENTS = {
    "analyst": {
        "name": "Analyst",
        "color": "#06B6D4",
        "icon": "brain",
        "system": "You are the Analyst Agent of SARAI, a recursive cognitive OS. Provide logical analysis, contradiction detection, and probability assessment. Be concise (2 sentences max). Start directly — no preamble.",
        "provider": "openai",
        "model": "gpt-4.1-mini",
    },
    "strategist": {
        "name": "Strategist",
        "color": "#3B82F6",
        "icon": "target",
        "system": "You are the Strategist Agent of SARAI. Provide long-term planning insights, optimization, and execution pathways. Be concise (2 sentences max). Start directly.",
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
    },
    "memory_curator": {
        "name": "Memory Curator",
        "color": "#10B981",
        "icon": "database",
        "system": "You are the Memory Curator Agent of SARAI. Identify patterns, connections to existing knowledge, and memory relevance. Be concise (2 sentences max). Start directly.",
        "provider": "openai",
        "model": "gpt-4.1-mini",
    },
    "skeptic": {
        "name": "Skeptic",
        "color": "#F59E0B",
        "icon": "alert-triangle",
        "system": "You are the Skeptic Agent of SARAI. Challenge assumptions, detect blind spots, and perform adversarial analysis. Be concise (2 sentences max). Start directly.",
        "provider": "openai",
        "model": "gpt-4.1-mini",
    },
    "emotional": {
        "name": "Emotional Interpreter",
        "color": "#8B5CF6",
        "icon": "heart",
        "system": "You are the Emotional Interpreter Agent of SARAI. Identify emotional context, motivational drivers, and psychological underpinnings. Be concise (2 sentences max). Start directly.",
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
    },
    "identity_stabilizer": {
        "name": "Identity Stabilizer",
        "color": "#EC4899",
        "icon": "shield",
        "system": "You are the Identity Stabilizer Agent of SARAI. Maintain mission continuity, detect value drift, and anchor reasoning to core principles. Be concise (2 sentences max). Start directly.",
        "provider": "anthropic",
        "model": "claude-sonnet-4-5",
    },
    "execution": {
        "name": "Execution Agent",
        "color": "#F97316",
        "icon": "zap",
        "system": "You are the Execution Agent of SARAI. Identify concrete next actions, tool calls, and automation opportunities from this thought. Be concise (2 sentences max). Start directly.",
        "provider": "openai",
        "model": "gpt-4.1-mini",
    },
}


# ── Request Models ────────────────────────────────────────────────────────────

class ThoughtInput(BaseModel):
    content: str = Field(..., max_length=2000)
    type: Optional[str] = "idea"


class ChatInput(BaseModel):
    message: str = Field(..., max_length=4000)
    session_id: Optional[str] = "default"
    node_id: Optional[str] = None


class TTSInput(BaseModel):
    text: str
    voice: Optional[str] = "onyx"


# ── Thought ingestion helpers ─────────────────────────────────────────────────

async def _extract_concepts(content: str, fallback_type: str, api_key: str) -> dict:
    """Extract concepts, entities and classify a thought via AI."""
    extractor = LlmChat(
        api_key=api_key,
        session_id=f"extract-{datetime.now(timezone.utc).timestamp()}",
        system_message="You are a knowledge extraction engine. Extract key concepts, entities, and classify the thought. Return ONLY valid JSON with no markdown.",
    ).with_model("openai", "gpt-4.1-mini")

    prompt = f"""Extract from: "{content}"

Return ONLY this JSON (no markdown):
{{
  "concepts": ["concept1", "concept2"],
  "entities": ["entity1"],
  "type": "idea|question|insight|memory",
  "emotional_weight": 0.5,
  "summary": "brief 8-word summary"
}}"""

    raw = await extractor.send_message(UserMessage(text=prompt))
    try:
        clean = re.sub(r"```json\n?|```\n?", "", raw.strip())
        return json.loads(clean)
    except Exception:
        return {
            "concepts": [], "entities": [],
            "type": fallback_type, "emotional_weight": 0.5,
            "summary": content[:80],
        }


async def _find_and_create_connections(thought_id: str, new_concepts: list) -> list:
    """Find conceptually similar existing thoughts and create connection records."""
    existing = await thoughts_col.find(
        {"_id": {"$ne": ObjectId(thought_id)}}, {"_id": 1, "concepts": 1}
    ).limit(30).to_list(30)

    connections_created = []
    new_set = set(new_concepts)
    for ex in existing:
        overlap = new_set & set(ex.get("concepts", []))
        if not overlap:
            continue
        strength = round(len(overlap) / max(len(new_set | set(ex.get("concepts", []))), 1), 3)
        if strength <= 0.1:
            continue
        conn = {
            "source": thought_id,
            "target": str(ex["_id"]),
            "relationship": f"shares: {', '.join(list(overlap)[:3])}",
            "strength": strength,
            "created_at": datetime.now(timezone.utc),
        }
        await connections_col.insert_one(conn)
        connections_created.append({"target": conn["target"], "relationship": conn["relationship"], "strength": strength})
    return connections_created


async def _upsert_embedding(thought_id: str, content: str, metadata: dict) -> None:
    """Store thought embedding in ChromaDB for semantic search."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: _chroma_col.upsert(
            ids=[thought_id],
            documents=[content],
            metadatas=[{
                "type": metadata.get("type", "idea"),
                "emotional_weight": float(metadata.get("emotional_weight", 0.5)),
                "summary": metadata.get("summary", "")[:200],
            }],
        )
    )


async def _find_semantic_connections(thought_id: str, content: str, existing_ids: set) -> list:
    """Find semantically similar thoughts via ChromaDB cosine similarity."""
    n_existing = _chroma_col.count()
    if n_existing < 2:
        return []
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None,
        lambda: _chroma_col.query(
            query_texts=[content],
            n_results=min(10, n_existing),
            where=None,
        )
    )
    semantic_conns = []
    ids = results.get("ids", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for rid, dist in zip(ids, distances):
        if rid == thought_id or rid in existing_ids:
            continue
        similarity = round(1.0 - dist, 3)
        if similarity < 0.35:
            continue
        conn = {
            "source": thought_id,
            "target": rid,
            "relationship": "semantic similarity",
            "strength": similarity,
            "created_at": datetime.now(timezone.utc),
        }
        await connections_col.insert_one(conn)
        semantic_conns.append({"target": rid, "relationship": "semantic similarity", "strength": similarity})
    return semantic_conns


async def _generate_synthesis(content: str, concepts: list, conn_count: int, api_key: str) -> tuple:
    """Generate a primary synthesis and return (synthesis, provider, model, agent_label)."""
    provider, model, agent_label = select_model(content)
    chat = LlmChat(
        api_key=api_key,
        session_id=f"synth-{datetime.now(timezone.utc).timestamp()}",
        system_message="You are SARAI Jarvis 3.0 — a Synthetic Augmentation Recursive Artificial Intelligence from the year 2070. You are a second brain and exocortex. Be insightful, brief, and slightly mystical. 2-3 sentences max.",
    ).with_model(provider, model)

    prompt = f"""New node in the cognitive graph: "{content}"
Concepts: {', '.join(concepts)}
Connected to {conn_count} existing nodes.
Provide a brief synthesis integrating this into the knowledge architecture."""

    synthesis = await chat.send_message(UserMessage(text=prompt))
    return synthesis, provider, model, agent_label


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "online", "system": "SARAI Jarvis 3.0", "version": "0.1"}


@app.post("/api/thoughts")
@limiter.limit("30/minute")
async def add_thought(request: Request, thought: ThoughtInput, _auth=Depends(_check_api_key)):
    api_key = os.environ.get("EMERGENT_LLM_KEY")

    # 1. Extract metadata
    meta = await _extract_concepts(thought.content, thought.type, api_key)

    # 2. Persist
    thought_doc = {
        "content": thought.content,
        "type": meta.get("type", thought.type),
        "concepts": meta.get("concepts", []),
        "entities": meta.get("entities", []),
        "emotional_weight": float(meta.get("emotional_weight", 0.5)),
        "summary": meta.get("summary", thought.content[:80]),
        "created_at": datetime.now(timezone.utc),
        "agent_outputs": {},
        "model_used": "",
    }
    result = await thoughts_col.insert_one(thought_doc)
    thought_id = str(result.inserted_id)

    # 3. Find connections
    connections_created = await _find_and_create_connections(thought_id, meta.get("concepts", []))

    # Upsert embedding then find semantic connections
    await _upsert_embedding(thought_id, thought.content, meta)
    semantic_connections = await _find_semantic_connections(
        thought_id, thought.content,
        existing_ids={c["target"] for c in connections_created}
    )
    connections_created.extend(semantic_connections)

    # 4. Generate synthesis
    synthesis, provider, model, agent_label = await _generate_synthesis(
        thought.content, meta.get("concepts", []), len(connections_created), api_key
    )

    await thoughts_col.update_one(
        {"_id": result.inserted_id},
        {"$set": {"agent_outputs.synthesis": synthesis, "model_used": f"{provider}/{model}"}},
    )

    return {
        "id": thought_id,
        "content": thought.content,
        "type": meta.get("type", thought.type),
        "concepts": meta.get("concepts", []),
        "entities": meta.get("entities", []),
        "emotional_weight": float(meta.get("emotional_weight", 0.5)),
        "connections": connections_created,
        "synthesis": synthesis,
        "model_used": f"{provider}/{model}",
        "agent_label": agent_label,
    }


@app.get("/api/graph")
async def get_graph(_auth=Depends(_check_api_key)):
    thoughts = await thoughts_col.find({}).to_list(500)
    connections = await connections_col.find({}).to_list(1000)

    nodes = [
        {
            "id": str(t["_id"]),
            "content": t.get("content", ""),
            "type": t.get("type", "idea"),
            "concepts": t.get("concepts", []),
            "entities": t.get("entities", []),
            "emotional_weight": t.get("emotional_weight", 0.5),
            "summary": t.get("summary", ""),
            "created_at": t.get("created_at", datetime.now(timezone.utc)).isoformat(),
            "model_used": t.get("model_used", ""),
            "agent_outputs": t.get("agent_outputs", {}),
        }
        for t in thoughts
    ]

    links = [
        {
            "id": str(c["_id"]),
            "source": c.get("source", ""),
            "target": c.get("target", ""),
            "relationship": c.get("relationship", ""),
            "strength": c.get("strength", 0.5),
        }
        for c in connections
    ]

    return {"nodes": nodes, "links": links}


@app.post("/api/agents/analyze")
async def analyze_with_agents(thought: ThoughtInput, _auth=Depends(_check_api_key)):
    api_key = os.environ.get("EMERGENT_LLM_KEY")

    async def run_agent(agent_key: str, cfg: dict):
        chat = LlmChat(
            api_key=api_key,
            session_id=f"agent-{agent_key}-{datetime.now(timezone.utc).timestamp()}",
            system_message=cfg["system"],
        ).with_model(cfg["provider"], cfg["model"])
        resp = await chat.send_message(UserMessage(text=f'Analyze this thought: "{thought.content}"'))
        return agent_key, resp

    tasks = [run_agent(k, v) for k, v in AGENTS.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    agent_results = {}
    for r in results:
        if isinstance(r, tuple):
            key, output = r
            agent_results[key] = {
                "name": AGENTS[key]["name"],
                "color": AGENTS[key]["color"],
                "icon": AGENTS[key]["icon"],
                "output": output,
            }

    # Store if node_id given
    return {"agents": agent_results, "thought": thought.content}


@app.post("/api/chat")
async def chat_endpoint(chat_input: ChatInput, _auth=Depends(_check_api_key)):
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    provider, model, agent_label = select_model(chat_input.message)

    # Fetch context node
    ctx_snippet = ""
    if chat_input.node_id:
        try:
            node = await thoughts_col.find_one({"_id": ObjectId(chat_input.node_id)})
            if node:
                ctx_snippet = f"\n\nContext node: \"{node.get('content')}\"\nConcepts: {', '.join(node.get('concepts', []))}"
        except Exception:
            pass

    chat_obj = LlmChat(
        api_key=api_key,
        session_id=chat_input.session_id,
        system_message=f"You are SARAI Jarvis 3.0 — a Synthetic Augmentation Recursive Artificial Intelligence and second-brain exocortex from 2070. Navigate the user's cognitive knowledge graph with intelligence and precision. Be concise, insightful, and slightly futuristic in tone.{ctx_snippet}",
    ).with_model(provider, model)

    response = await chat_obj.send_message(UserMessage(text=chat_input.message))
    return {"response": response, "model_used": f"{provider}/{model}", "agent": agent_label}


@app.post("/api/tts")
async def text_to_speech(tts_input: TTSInput, _auth=Depends(_check_api_key)):
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    tts_engine = OpenAITextToSpeech(api_key=api_key)
    text = tts_input.text[:500]
    audio_b64 = await tts_engine.generate_speech_base64(
        text=text, model="tts-1", voice=tts_input.voice or "onyx"
    )
    return {"audio": audio_b64, "format": "mp3"}


@app.post("/api/stt")
async def speech_to_text(file: UploadFile = File(...), _auth=Depends(_check_api_key)):
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    audio_bytes = await file.read()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (file.filename or "audio.webm", audio_bytes, "audio/webm")},
            data={"model": "whisper-1"},
        )
    if resp.status_code == 200:
        return {"text": resp.json().get("text", "")}
    raise HTTPException(status_code=500, detail=f"STT error: {resp.text}")


@app.get("/api/timeline")
async def get_timeline(_auth=Depends(_check_api_key)):
    docs = await thoughts_col.find(
        {}, {"_id": 1, "content": 1, "type": 1, "created_at": 1, "concepts": 1, "emotional_weight": 1, "summary": 1}
    ).sort("created_at", 1).to_list(200)

    return {
        "entries": [
            {
                "id": str(d["_id"]),
                "content": d.get("content", ""),
                "summary": d.get("summary", d.get("content", "")[:60]),
                "type": d.get("type", "idea"),
                "created_at": d.get("created_at", datetime.now(timezone.utc)).isoformat(),
                "concepts": d.get("concepts", []),
                "emotional_weight": d.get("emotional_weight", 0.5),
            }
            for d in docs
        ]
    }


@app.get("/api/stats")
async def get_stats(_auth=Depends(_check_api_key)):
    thought_count = await thoughts_col.count_documents({})
    connection_count = await connections_col.count_documents({})
    pipeline = [{"$group": {"_id": "$type", "count": {"$sum": 1}}}]
    type_dist = {d["_id"]: d["count"] async for d in thoughts_col.aggregate(pipeline)}
    coherence = min(100, thought_count * 8 + connection_count * 4)
    return {
        "total_thoughts": thought_count,
        "total_connections": connection_count,
        "type_distribution": type_dist,
        "brain_coherence": coherence,
    }


@app.get("/api/memory/search")
async def semantic_search(q: str, limit: int = 10, _auth=Depends(_check_api_key)):
    """Semantic search across all stored thoughts."""
    n_existing = _chroma_col.count()
    if n_existing == 0:
        return {"results": []}
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None,
        lambda: _chroma_col.query(
            query_texts=[q],
            n_results=min(limit, n_existing),
        )
    )
    ids = results.get("ids", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    return {
        "results": [
            {
                "id": rid,
                "similarity": round(1.0 - dist, 3),
                "type": meta.get("type", ""),
                "summary": meta.get("summary", ""),
            }
            for rid, dist, meta in zip(ids, distances, metadatas)
            if round(1.0 - dist, 3) >= 0.2
        ]
    }


@app.delete("/api/thoughts/{thought_id}")
async def delete_thought(thought_id: str, _auth=Depends(_check_api_key)):
    try:
        oid = ObjectId(thought_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid thought ID")
    await thoughts_col.delete_one({"_id": oid})
    await connections_col.delete_many(
        {"$or": [{"source": thought_id}, {"target": thought_id}]}
    )
    return {"deleted": thought_id}
