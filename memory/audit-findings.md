# Security Audit Findings & Fixes

**Date:** 2026-05-29  
**Scope:** backend/server.py, frontend/src/App.js, frontend/src/components/ThoughtInput.js, frontend/src/hooks/useGraphData.js

## Issues Fixed

### Backend (server.py)

1. **Wildcard CORS** — Changed `allow_origins=["*"]` to read from `FRONTEND_URL` env var (default `http://localhost:3000`).

2. **No authentication** — Added `_check_api_key` dependency (reads `API_KEY` env var, checks `X-API-Key` request header). Applied via `Depends(_check_api_key)` to all endpoints except `/api/health`.

3. **No rate limiting** — Added `slowapi` limiter; `POST /api/thoughts` is capped at 30 requests/minute per IP. Limiter and exception handler registered on the app.

4. **Input validation** — `ThoughtInput.content` now has `max_length=2000`; `ChatInput.message` now has `max_length=4000` (both use `pydantic.Field`).

5. **ObjectId validation** — `delete_thought` now wraps `ObjectId(thought_id)` in try/except and raises HTTP 400 on invalid IDs. `chat_endpoint` already had a silent try/except around `ObjectId(chat_input.node_id)` which is acceptable (treats invalid IDs as no-context rather than erroring).

6. **Invalid model name** — Replaced all occurrences of `claude-4-sonnet-20250514` with `claude-sonnet-4-5` (affects `select_model`, `AGENTS["strategist"]`, `AGENTS["emotional"]`).

### Frontend

7. **Missing API key header** — Added `API_HEADERS = { "X-API-Key": process.env.REACT_APP_API_KEY || "" }` constant in all three files. Applied to every `fetch` call:
   - `App.js`: TTS call, agents/analyze call, delete thought call
   - `ThoughtInput.js`: thought submission call, STT call
   - `hooks/useGraphData.js`: fetchGraph, fetchStats, fetchTimeline calls

## Required Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `FRONTEND_URL` | backend | Allowed CORS origin (e.g. `https://your-app.com`) |
| `API_KEY` | backend | Secret key checked against `X-API-Key` header |
| `REACT_APP_API_KEY` | frontend | Must match backend `API_KEY` |
