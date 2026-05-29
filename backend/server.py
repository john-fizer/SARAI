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
import networkx as nx
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


async def _recursive_reflect(
    thought_id: str,
    content: str,
    synthesis: str,
    concepts: list,
    api_key: str,
) -> dict:
    """Self-evaluation loop: score, detect contradictions, optionally revise."""
    # Find semantically close existing thoughts for contradiction detection
    similar_summaries = []
    try:
        n_existing = _chroma_col.count()
        if n_existing >= 2:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: _chroma_col.query(
                    query_texts=[content],
                    n_results=min(5, n_existing),
                )
            )
            ids = results.get("ids", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]
            for rid, meta, dist in zip(ids, metas, dists):
                if rid != thought_id and (1.0 - dist) >= 0.5:
                    similar_summaries.append(meta.get("summary", ""))
    except Exception:
        pass

    context = ""
    if similar_summaries:
        context = "\n\nRelated existing thoughts:\n" + "\n".join(f"- {s}" for s in similar_summaries if s)

    reflector = LlmChat(
        api_key=api_key,
        session_id=f"reflect-{datetime.now(timezone.utc).timestamp()}",
        system_message="You are SARAI's internal self-evaluation engine. Analyze the thought and its synthesis critically. Return ONLY valid JSON with no markdown.",
    ).with_model("openai", "gpt-4.1-mini")

    prompt = f"""Evaluate this thought and its synthesis.

Thought: "{content}"
Synthesis: "{synthesis}"{context}

Return ONLY this JSON (no markdown):
{{
  "confidence": 0.85,
  "contradictions": ["brief description if any, else empty list"],
  "revision": "improved synthesis if confidence < 0.7, else empty string",
  "evaluation": "one sentence meta-assessment"
}}"""

    raw = await reflector.send_message(UserMessage(text=prompt))
    try:
        clean = re.sub(r"```json\n?|```\n?", "", raw.strip())
        result = json.loads(clean)
        return {
            "confidence": float(result.get("confidence", 0.8)),
            "contradictions": result.get("contradictions", []),
            "revision": result.get("revision", ""),
            "evaluation": result.get("evaluation", ""),
        }
    except Exception:
        return {"confidence": 0.8, "contradictions": [], "revision": "", "evaluation": ""}


async def _run_consensus(content: str, agent_results: dict, api_key: str) -> dict:
    """Run a meta-synthesis over all agent outputs to produce a consensus verdict."""
    summaries = "\n".join(
        f"- {v['name']}: {v['output'][:200]}"
        for v in agent_results.values()
        if isinstance(v, dict) and v.get("output")
    )
    chat = LlmChat(
        api_key=api_key,
        session_id=f"consensus-{datetime.now(timezone.utc).timestamp()}",
        system_message="You are a meta-cognitive consensus engine. Given multiple agent perspectives on a thought, synthesize a final verdict. Return ONLY valid JSON with no markdown.",
    ).with_model("openai", "gpt-4.1-mini")
    prompt = f"""Thought: "{content}"

Agent perspectives:
{summaries}

Return ONLY this JSON:
{{
  "consensus": "2-3 sentence unified synthesis",
  "confidence": 0.85,
  "dominant_frame": "analyst|strategist|emotional|skeptic|memory_curator|identity_stabilizer|execution",
  "dissent": "brief note on the most conflicting perspective, or null"
}}"""
    raw = await chat.send_message(UserMessage(text=prompt))
    try:
        clean = re.sub(r"```json\n?|```\n?", "", raw.strip())
        return json.loads(clean)
    except Exception:
        return {"consensus": raw[:300], "confidence": 0.5, "dominant_frame": "analyst", "dissent": None}


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

    # Recursive reflection — self-evaluate the synthesis
    reflection = await _recursive_reflect(
        thought_id, thought.content, synthesis, meta.get("concepts", []), api_key
    )
    final_synthesis = reflection.get("revision") or synthesis
    await thoughts_col.update_one(
        {"_id": result.inserted_id},
        {"$set": {
            "reflection": reflection,
            "agent_outputs.synthesis": final_synthesis,
        }},
    )

    return {
        "id": thought_id,
        "content": thought.content,
        "type": meta.get("type", thought.type),
        "concepts": meta.get("concepts", []),
        "entities": meta.get("entities", []),
        "emotional_weight": float(meta.get("emotional_weight", 0.5)),
        "connections": connections_created,
        "synthesis": final_synthesis,
        "reflection": reflection,
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
            "reflection": t.get("reflection", {}),
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

    # Semantic memory retrieval — pull top relevant memories from ChromaDB
    memory_context = ""
    try:
        n_existing = _chroma_col.count()
        if n_existing > 0:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: _chroma_col.query(
                    query_texts=[chat_input.message],
                    n_results=min(5, n_existing),
                )
            )
            ids = results.get("ids", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]
            relevant = [
                m.get("summary", "") for rid, m, d in zip(ids, metas, dists)
                if (1.0 - d) >= 0.3 and m.get("summary")
            ]
            if relevant:
                memory_context = "\n\nRelevant memories from your knowledge graph:\n" + "\n".join(
                    f"- {s}" for s in relevant
                )
    except Exception:
        pass

    # Explicit node context (if provided) appended after memory
    node_context = ""
    if chat_input.node_id:
        try:
            node = await thoughts_col.find_one({"_id": ObjectId(chat_input.node_id)})
            if node:
                node_context = f"\n\nFocused node: \"{node.get('content')}\"\nConcepts: {', '.join(node.get('concepts', []))}"
        except Exception:
            pass

    chat_obj = LlmChat(
        api_key=api_key,
        session_id=chat_input.session_id,
        system_message=(
            "You are SARAI Jarvis 3.0 — a Synthetic Augmentation Recursive Artificial Intelligence "
            "and second-brain exocortex from 2070. Navigate the user's cognitive knowledge graph with "
            f"intelligence and precision. Be concise, insightful, and slightly futuristic in tone."
            f"{memory_context}{node_context}"
        ),
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


@app.post("/api/agents/consensus")
async def agents_consensus(thought: ThoughtInput, _auth=Depends(_check_api_key)):
    """Run all agents then produce a consensus synthesis."""
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
                "output": output,
            }

    consensus = await _run_consensus(thought.content, agent_results, api_key)
    return {"agents": agent_results, "consensus": consensus, "thought": thought.content}


@app.post("/api/simulate")
async def simulate(thought: ThoughtInput, _auth=Depends(_check_api_key)):
    """Project 3 probable future scenarios from the current knowledge state."""
    api_key = os.environ.get("EMERGENT_LLM_KEY")

    # Pull top semantic neighbours for context
    context_nodes = []
    try:
        n_existing = _chroma_col.count()
        if n_existing > 0:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: _chroma_col.query(query_texts=[thought.content], n_results=min(6, n_existing))
            )
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]
            context_nodes = [
                m.get("summary", "") for m, d in zip(metas, dists)
                if (1.0 - d) >= 0.3 and m.get("summary")
            ]
    except Exception:
        pass

    context_str = "\n".join(f"- {s}" for s in context_nodes) if context_nodes else "No prior context."

    chat = LlmChat(
        api_key=api_key,
        session_id=f"simulate-{datetime.now(timezone.utc).timestamp()}",
        system_message="You are SARAI's simulation engine — a probabilistic future-state projector. Given a thought and its knowledge context, generate 3 distinct probable future scenarios. Return ONLY valid JSON with no markdown.",
    ).with_model("anthropic", "claude-sonnet-4-5")

    prompt = f"""Current thought: "{thought.content}"

Related knowledge context:
{context_str}

Project 3 distinct future scenarios. Return ONLY this JSON:
{{
  "scenarios": [
    {{
      "title": "short title",
      "description": "2-3 sentence scenario description",
      "probability": 0.6,
      "timeframe": "short-term|medium-term|long-term",
      "key_driver": "the main factor driving this outcome"
    }}
  ]
}}"""

    raw = await chat.send_message(UserMessage(text=prompt))
    try:
        clean = re.sub(r"```json\n?|```\n?", "", raw.strip())
        data = json.loads(clean)
        return {"scenarios": data.get("scenarios", []), "thought": thought.content}
    except Exception:
        return {"scenarios": [], "thought": thought.content, "error": "parse error"}


@app.get("/api/graph/path")
async def graph_path(from_id: str, to_id: str, _auth=Depends(_check_api_key)):
    """Find the conceptual path between two thoughts in the knowledge graph."""
    # Validate IDs
    for nid in (from_id, to_id):
        try:
            ObjectId(nid)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid id: {nid}")

    connections = await connections_col.find({}, {"source": 1, "target": 1, "relationship": 1, "strength": 1}).to_list(2000)

    G = nx.Graph()
    for c in connections:
        G.add_edge(c["source"], c["target"], relationship=c.get("relationship", ""), strength=c.get("strength", 0.5))

    if not G.has_node(from_id) or not G.has_node(to_id):
        return {"path": [], "found": False, "message": "One or both nodes have no connections"}

    try:
        path = nx.shortest_path(G, source=from_id, target=to_id)
    except nx.NetworkXNoPath:
        return {"path": [], "found": False, "message": "No path exists between these nodes"}

    # Enrich path with thought content
    path_nodes = []
    for nid in path:
        try:
            doc = await thoughts_col.find_one({"_id": ObjectId(nid)}, {"content": 1, "type": 1, "concepts": 1})
            if doc:
                path_nodes.append({
                    "id": nid,
                    "content": doc.get("content", ""),
                    "type": doc.get("type", "idea"),
                    "concepts": doc.get("concepts", []),
                })
        except Exception:
            path_nodes.append({"id": nid, "content": "", "type": "idea", "concepts": []})

    return {"path": path_nodes, "found": True, "length": len(path) - 1}


@app.get("/api/export")
async def export_knowledge(_auth=Depends(_check_api_key)):
    """Export the full knowledge graph as structured JSON."""
    thoughts = await thoughts_col.find({}).to_list(1000)
    connections = await connections_col.find({}).to_list(5000)
    return {
        "version": "1.0",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "nodes": [
            {
                "id": str(t["_id"]),
                "content": t.get("content", ""),
                "type": t.get("type", "idea"),
                "concepts": t.get("concepts", []),
                "entities": t.get("entities", []),
                "emotional_weight": t.get("emotional_weight", 0.5),
                "summary": t.get("summary", ""),
                "created_at": t.get("created_at", datetime.now(timezone.utc)).isoformat(),
                "reflection": t.get("reflection", {}),
            }
            for t in thoughts
        ],
        "edges": [
            {
                "id": str(c["_id"]),
                "source": c.get("source", ""),
                "target": c.get("target", ""),
                "relationship": c.get("relationship", ""),
                "strength": c.get("strength", 0.5),
            }
            for c in connections
        ],
        "stats": {
            "total_nodes": len(thoughts),
            "total_edges": len(connections),
        },
    }


@app.get("/api/search")
async def search_thoughts(q: str, limit: int = 20, _auth=Depends(_check_api_key)):
    """Unified search: combines semantic (ChromaDB) and keyword (MongoDB regex) results."""
    results = []
    seen_ids = set()

    # Semantic search via ChromaDB
    try:
        n_existing = _chroma_col.count()
        if n_existing > 0:
            loop = asyncio.get_event_loop()
            chroma_results = await loop.run_in_executor(
                None,
                lambda: _chroma_col.query(query_texts=[q], n_results=min(10, n_existing))
            )
            ids = chroma_results.get("ids", [[]])[0]
            distances = chroma_results.get("distances", [[]])[0]
            for rid, dist in zip(ids, distances):
                similarity = round(1.0 - dist, 3)
                if similarity >= 0.25 and rid not in seen_ids:
                    seen_ids.add(rid)
                    results.append({"id": rid, "score": similarity, "match_type": "semantic"})
    except Exception:
        pass

    # Keyword search via MongoDB regex
    try:
        regex = {"$regex": q, "$options": "i"}
        cursor = thoughts_col.find(
            {"$or": [{"content": regex}, {"concepts": regex}, {"summary": regex}]},
            {"_id": 1, "content": 1, "summary": 1, "type": 1, "concepts": 1}
        ).limit(limit)
        async for doc in cursor:
            doc_id = str(doc["_id"])
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                results.append({
                    "id": doc_id,
                    "content": doc.get("content", ""),
                    "summary": doc.get("summary", ""),
                    "type": doc.get("type", "idea"),
                    "concepts": doc.get("concepts", []),
                    "score": 0.5,
                    "match_type": "keyword",
                })
    except Exception:
        pass

    # Enrich semantic results with MongoDB data
    enriched = []
    for r in results[:limit]:
        if r.get("match_type") == "semantic" and "content" not in r:
            try:
                from bson import ObjectId as ObjId
                doc = await thoughts_col.find_one({"_id": ObjId(r["id"])})
                if doc:
                    r.update({
                        "content": doc.get("content", ""),
                        "summary": doc.get("summary", ""),
                        "type": doc.get("type", "idea"),
                        "concepts": doc.get("concepts", []),
                    })
            except Exception:
                pass
        enriched.append(r)

    enriched.sort(key=lambda x: x.get("score", 0), reverse=True)
    return {"results": enriched[:limit], "query": q}


@app.get("/api/graph/clusters")
async def get_graph_clusters(_auth=Depends(_check_api_key)):
    """Detect communities in the knowledge graph using NetworkX."""
    connections = await connections_col.find({}, {"source": 1, "target": 1, "strength": 1}).to_list(5000)
    if not connections:
        return {"clusters": {}, "cluster_count": 0}

    G = nx.Graph()
    for c in connections:
        src, tgt = c.get("source"), c.get("target")
        if src and tgt:
            G.add_edge(src, tgt, weight=c.get("strength", 0.5))

    # Greedy modularity community detection
    try:
        from networkx.algorithms.community import greedy_modularity_communities
        communities = list(greedy_modularity_communities(G))
        cluster_map = {}
        for i, community in enumerate(communities):
            for node_id in community:
                cluster_map[node_id] = i
        # Nodes with no connections get cluster -1
        all_thoughts = await thoughts_col.find({}, {"_id": 1}).to_list(1000)
        for t in all_thoughts:
            tid = str(t["_id"])
            if tid not in cluster_map:
                cluster_map[tid] = -1
        return {
            "clusters": cluster_map,
            "cluster_count": len(communities),
        }
    except Exception:
        return {"clusters": {}, "cluster_count": 0}


@app.post("/api/agents/debate")
async def debate_agents(thought: ThoughtInput, _auth=Depends(_check_api_key)):
    """
    Multi-agent debate: agents see each other's initial positions and write
    a follow-up response challenging or building on the other agents' views.
    Returns initial positions + follow-up rebuttals.
    """
    api_key = os.environ.get("EMERGENT_LLM_KEY")

    # Round 1 — each agent states their initial position
    async def initial_position(agent_key: str, cfg: dict) -> tuple:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"debate-r1-{agent_key}-{datetime.now(timezone.utc).timestamp()}",
            system_message=cfg["system"],
        ).with_model(cfg["provider"], cfg["model"])
        resp = await chat.send_message(
            UserMessage(text=f'State your position on: "{thought.content}" in 1-2 sentences.')
        )
        return agent_key, resp

    round1_tasks = [initial_position(k, v) for k, v in AGENTS.items()]
    round1_results = await asyncio.gather(*round1_tasks, return_exceptions=True)

    positions = {}
    for r in round1_results:
        if isinstance(r, tuple):
            key, output = r
            positions[key] = output

    # Build the debate context (all other agents' positions)
    def build_context(exclude_key: str) -> str:
        others = [
            f"- {AGENTS[k]['name']}: {v}"
            for k, v in positions.items()
            if k != exclude_key and v
        ]
        return "\n".join(others)

    # Round 2 — each agent responds to the others
    async def rebuttal(agent_key: str, cfg: dict) -> tuple:
        context = build_context(agent_key)
        chat = LlmChat(
            api_key=api_key,
            session_id=f"debate-r2-{agent_key}-{datetime.now(timezone.utc).timestamp()}",
            system_message=cfg["system"],
        ).with_model(cfg["provider"], cfg["model"])
        prompt = (
            f'The topic is: "{thought.content}"\n\n'
            f'Other agents said:\n{context}\n\n'
            f'In 1-2 sentences, challenge or build on their views from your perspective.'
        )
        resp = await chat.send_message(UserMessage(text=prompt))
        return agent_key, resp

    round2_tasks = [rebuttal(k, v) for k, v in AGENTS.items()]
    round2_results = await asyncio.gather(*round2_tasks, return_exceptions=True)

    rebuttals = {}
    for r in round2_results:
        if isinstance(r, tuple):
            key, output = r
            rebuttals[key] = output

    # Compile debate output
    debate = {
        key: {
            "name": AGENTS[key]["name"],
            "color": AGENTS[key]["color"],
            "position": positions.get(key, ""),
            "rebuttal": rebuttals.get(key, ""),
        }
        for key in AGENTS
        if positions.get(key) or rebuttals.get(key)
    }

    return {"debate": debate, "thought": thought.content, "rounds": 2}


@app.post("/api/plan")
async def autonomous_plan(thought: ThoughtInput, _auth=Depends(_check_api_key)):
    """
    Autonomous planning: given a goal/thought, generate a multi-step action
    plan with dependencies, estimated effort, and success metrics.
    """
    api_key = os.environ.get("EMERGENT_LLM_KEY")

    # Pull semantic context from memory
    memory_context = ""
    try:
        n_existing = _chroma_col.count()
        if n_existing > 0:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: _chroma_col.query(query_texts=[thought.content], n_results=min(6, n_existing))
            )
            summaries = [
                m.get("summary", "") for m, d in zip(
                    results.get("metadatas", [[]])[0],
                    results.get("distances", [[]])[0]
                ) if (1.0 - d) >= 0.3 and m.get("summary")
            ]
            if summaries:
                memory_context = "\n\nRelevant knowledge:\n" + "\n".join(f"- {s}" for s in summaries)
    except Exception:
        pass

    planner = LlmChat(
        api_key=api_key,
        session_id=f"plan-{datetime.now(timezone.utc).timestamp()}",
        system_message=(
            "You are the Strategic Planning Engine of SARAI. Generate precise, actionable plans. "
            "Return ONLY valid JSON with no markdown."
        ),
    ).with_model("anthropic", "claude-sonnet-4-5")

    prompt = f"""Goal: "{thought.content}"{memory_context}

Generate a strategic action plan. Return ONLY this JSON:
{{
  "goal": "refined goal statement",
  "steps": [
    {{
      "id": 1,
      "action": "specific action",
      "depends_on": [],
      "effort": "low|medium|high",
      "timeframe": "immediate|short-term|long-term",
      "success_metric": "how to measure completion"
    }}
  ],
  "risks": ["risk1", "risk2"],
  "first_move": "the single most important first action"
}}
Include 3-6 steps. Ensure depends_on references valid step ids."""

    raw = await planner.send_message(UserMessage(text=prompt))
    try:
        clean = re.sub(r"```json\n?|```\n?", "", raw.strip())
        plan = json.loads(clean)
    except Exception:
        plan = {"goal": thought.content, "steps": [], "risks": [], "first_move": raw[:200]}

    return {"plan": plan, "thought": thought.content}


@app.get("/api/reflect/improve")
async def self_improve(_auth=Depends(_check_api_key)):
    """
    Analyze patterns across all stored reflections to surface system-level
    insights and improvement recommendations.
    """
    api_key = os.environ.get("EMERGENT_LLM_KEY")

    # Sample recent thoughts with reflections
    thoughts = await thoughts_col.find(
        {"reflection": {"$exists": True, "$ne": {}}},
        {"content": 1, "reflection": 1, "concepts": 1, "type": 1}
    ).sort("created_at", -1).limit(20).to_list(20)

    if not thoughts:
        return {"insights": [], "patterns": [], "recommendation": "Not enough reflection data yet."}

    # Build reflection summary
    reflection_data = []
    for t in thoughts:
        r = t.get("reflection", {})
        if r.get("confidence") is not None:
            reflection_data.append({
                "content_summary": t.get("content", "")[:100],
                "confidence": r.get("confidence"),
                "contradictions": r.get("contradictions", [])[:2],
                "evaluation": r.get("evaluation", "")[:100],
            })

    analyst = LlmChat(
        api_key=api_key,
        session_id=f"improve-{datetime.now(timezone.utc).timestamp()}",
        system_message="You are SARAI's self-improvement engine. Analyze reflection patterns and identify systemic insights. Return ONLY valid JSON.",
    ).with_model("anthropic", "claude-sonnet-4-5")

    prompt = f"""Analyze these {len(reflection_data)} thought reflections from a cognitive OS:

{json.dumps(reflection_data[:10], indent=2)}

Return ONLY this JSON:
{{
  "avg_confidence": 0.0,
  "patterns": ["pattern1", "pattern2"],
  "recurring_contradictions": ["theme1"],
  "insights": ["insight1", "insight2", "insight3"],
  "recommendation": "single most important improvement suggestion",
  "cognitive_health": "assessment of overall reasoning quality"
}}"""

    raw = await analyst.send_message(UserMessage(text=prompt))
    try:
        clean = re.sub(r"```json\n?|```\n?", "", raw.strip())
        return json.loads(clean)
    except Exception:
        return {"insights": [raw[:300]], "patterns": [], "recommendation": "", "cognitive_health": ""}


@app.post("/api/predict")
async def predict_future(thought: ThoughtInput, _auth=Depends(_check_api_key)):
    """
    Temporal prediction: uses knowledge graph patterns and concept
    trajectories to forecast likely developments.
    """
    api_key = os.environ.get("EMERGENT_LLM_KEY")

    # Get temporal sequence of related thoughts
    related_thoughts = []
    try:
        n_existing = _chroma_col.count()
        if n_existing > 0:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: _chroma_col.query(query_texts=[thought.content], n_results=min(8, n_existing))
            )
            ids = results.get("ids", [[]])[0]
            dists = results.get("distances", [[]])[0]
            relevant_ids = [rid for rid, d in zip(ids, dists) if (1.0 - d) >= 0.3]
            if relevant_ids:
                from bson import ObjectId as ObjId
                docs = await thoughts_col.find(
                    {"_id": {"$in": [ObjId(rid) for rid in relevant_ids if len(rid) == 24]}},
                    {"content": 1, "concepts": 1, "emotional_weight": 1, "created_at": 1}
                ).sort("created_at", 1).to_list(8)
                related_thoughts = [
                    {
                        "content": d.get("content", "")[:120],
                        "concepts": d.get("concepts", [])[:4],
                        "emotional_weight": d.get("emotional_weight", 0.5),
                    }
                    for d in docs
                ]
    except Exception:
        pass

    predictor = LlmChat(
        api_key=api_key,
        session_id=f"predict-{datetime.now(timezone.utc).timestamp()}",
        system_message="You are SARAI's Predictive Modeling Engine. Analyze trajectories and forecast developments. Return ONLY valid JSON.",
    ).with_model("anthropic", "claude-sonnet-4-5")

    context_str = json.dumps(related_thoughts, indent=2) if related_thoughts else "No related history."
    prompt = f"""Current thought: "{thought.content}"

Related thought trajectory:
{context_str}

Predict likely future developments. Return ONLY this JSON:
{{
  "predictions": [
    {{
      "outcome": "specific predicted outcome",
      "probability": 0.0,
      "timeframe": "days|weeks|months|years",
      "driving_force": "key factor enabling this",
      "early_signal": "what to watch for"
    }}
  ],
  "trajectory": "overall direction of thinking",
  "inflection_point": "the decision or event that will matter most",
  "blind_spot": "what is likely being overlooked"
}}
Include 3 predictions ordered by probability descending."""

    raw = await predictor.send_message(UserMessage(text=prompt))
    try:
        clean = re.sub(r"```json\n?|```\n?", "", raw.strip())
        result = json.loads(clean)
    except Exception:
        result = {"predictions": [], "trajectory": raw[:200], "inflection_point": "", "blind_spot": ""}

    return {**result, "thought": thought.content}


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
