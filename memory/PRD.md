# SARAI Jarvis 3.0 — Second Brain PRD

**Version**: 0.1  
**Date**: 2026-02-16  
**Author**: SARAI Genesis Project  
**Classification**: Cognitive Augmentation Infrastructure

---

## Problem Statement
Build a Jarvis 3.0 app implementing the "second brain" from the SARAI (Synthetic Augmentation Recursive Artificial Intelligence) GitHub repo. Interactive, motion graphics, 2070 vibes, visual neural networks, synapse firing, holographic morphing, parallax effect.

---

## Architecture

### Tech Stack
- **Frontend**: React 18 + D3.js v7 + Framer Motion + Lucide React
- **Backend**: FastAPI + Motor (async MongoDB)
- **AI**: emergentintegrations (OpenAI gpt-4.1, gpt-4.1-mini, Anthropic claude-4-sonnet-20250514)
- **TTS**: OpenAI TTS via emergentintegrations (voice: onyx)
- **STT**: OpenAI Whisper-1 via direct API call
- **Database**: MongoDB (sarai_brain)
- **Auth**: None (open access)

### Key Files
- `/app/backend/server.py` - FastAPI backend (406 lines)
- `/app/frontend/src/App.js` - Main layout + state
- `/app/frontend/src/components/NeuralGraph.js` - D3 Canvas neural graph
- `/app/frontend/src/components/ThoughtInput.js` - Text + voice input
- `/app/frontend/src/components/AgentChamber.js` - 5-agent SARAI chamber
- `/app/frontend/src/components/CognitiveTimeline.js` - Horizontal timeline
- `/app/frontend/src/components/NodeDetail.js` - Node inspection + per-node chat
- `/app/frontend/src/components/ParallaxBackground.js` - Canvas parallax stars
- `/app/frontend/src/components/JarvisVoice.js` - TTS audio playback

---

## What's Been Implemented (v0.1)

### Backend ✅
- POST /api/thoughts — Ingest thought, extract concepts via AI, find connections, generate synthesis
- GET /api/graph — Return full knowledge graph (nodes + links)
- POST /api/agents/analyze — Run all 5 SARAI agents in parallel (asyncio.gather)
- POST /api/chat — Context-aware chat with model routing
- POST /api/tts — OpenAI TTS (tts-1, voice: onyx)
- POST /api/stt — OpenAI Whisper-1 transcription
- GET /api/timeline — Chronological thought entries
- GET /api/stats — Node/synapse counts + brain coherence score
- DELETE /api/thoughts/{id} — Remove node + connections

### AI Model Routing (Context-Aware)
- Analysis/reflection queries → claude-4-sonnet-20250514
- Strategy/planning queries → claude-4-sonnet-20250514
- Emotional queries → claude-4-sonnet-20250514
- Short/simple inputs → gpt-4.1-mini
- Default → gpt-4.1

### Frontend ✅
- Parallax star field background (3 layers, mouse parallax, twinkling)
- D3.js Canvas neural graph with synapse particle animations
- Glassmorphic panels (backdrop-blur, neon borders)
- Agent Chamber showing 5 SARAI agents
- Cognitive Timeline (horizontal scroll, node type colors)
- NodeDetail panel with per-node chat
- Voice input (MediaRecorder → Whisper)
- TTS toggle (Jarvis voice)
- Real-time stats in top bar
- Scanline overlay for retro-futuristic feel
- Holographic gradient text

### Design
- Theme: Dark void (#030305)
- Fonts: Unbounded (headings), JetBrains Mono (body), Orbitron (accent)
- Colors: Cyan (#06B6D4), Blue (#3B82F6), Purple (#8B5CF6)
- Node types: idea=cyan, question=purple, insight=amber, memory=green

---

## Test Results (Iteration 1)
- Backend: 100% (10/10 tests passed)
- Frontend: 95% (all user flows working; D3 canvas Playwright limitation only)

---

## Prioritized Backlog

### P0 (Next Sprint)
- [ ] WebSocket real-time updates (replace polling)
- [ ] Semantic embeddings for smarter node connection detection
- [ ] Multi-user sessions with JWT auth

### P1 
- [ ] Simulation Engine (probabilistic future scenarios)
- [ ] Recursive reflection loop (system critiques its own outputs)
- [ ] Image/PDF ingestion for knowledge nodes
- [ ] Export knowledge graph as JSON/image

### P2 (Future)
- [ ] 3D neural graph (Three.js WebGL)
- [ ] ElevenLabs voice for more natural Jarvis TTS
- [ ] Browser extension for capturing thoughts from anywhere
- [ ] Mobile responsive layout
- [ ] Wearable device integration

---

## Environment
- Backend URL: https://35de459b-7ffd-486c-a674-1e2c5b6bba45.preview.emergentagent.com
- EMERGENT_LLM_KEY: sk-emergent-1C6A2F60993E6Ea5aF
