"""Backend tests for SARAI Jarvis 3.0"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API_KEY = os.environ.get("API_KEY", "")
AUTH_HEADERS = {"X-API-Key": API_KEY}


class TestHealth:
    def test_health(self):
        r = requests.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "online"


class TestStats:
    def test_get_stats(self):
        r = requests.get(f"{BASE_URL}/api/stats", headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "total_thoughts" in data
        assert "total_connections" in data
        assert "brain_coherence" in data


class TestGraph:
    def test_get_graph(self):
        r = requests.get(f"{BASE_URL}/api/graph", headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "nodes" in data
        assert "links" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["links"], list)


class TestTimeline:
    def test_get_timeline(self):
        r = requests.get(f"{BASE_URL}/api/timeline", headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "entries" in data
        assert isinstance(data["entries"], list)


class TestThoughts:
    created_id = None

    def test_post_thought(self):
        r = requests.post(f"{BASE_URL}/api/thoughts", json={"content": "TEST_ artificial intelligence and machine learning"}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "id" in data
        assert "concepts" in data
        assert "synthesis" in data
        TestThoughts.created_id = data["id"]
        print(f"Created thought id: {data['id']}")

    def test_graph_has_new_node(self):
        if not TestThoughts.created_id:
            pytest.skip("No created_id")
        r = requests.get(f"{BASE_URL}/api/graph", headers=AUTH_HEADERS)
        data = r.json()
        ids = [n["id"] for n in data["nodes"]]
        assert TestThoughts.created_id in ids

    def test_delete_thought(self):
        if not TestThoughts.created_id:
            pytest.skip("No created_id")
        r = requests.delete(f"{BASE_URL}/api/thoughts/{TestThoughts.created_id}", headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert data["deleted"] == TestThoughts.created_id

    def test_delete_removes_from_graph(self):
        if not TestThoughts.created_id:
            pytest.skip("No created_id")
        r = requests.get(f"{BASE_URL}/api/graph", headers=AUTH_HEADERS)
        ids = [n["id"] for n in r.json()["nodes"]]
        assert TestThoughts.created_id not in ids


class TestChat:
    def test_chat(self):
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": "Hello SARAI, what are you?"}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "response" in data
        assert len(data["response"]) > 0


class TestAgentAnalyze:
    def test_analyze(self):
        r = requests.post(f"{BASE_URL}/api/agents/analyze", json={"content": "Consciousness and its relationship to AI"}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "agents" in data
        assert len(data["agents"]) > 0


class TestSemanticSearch:
    def test_semantic_search(self):
        r = requests.get(f"{BASE_URL}/api/memory/search", params={"q": "intelligence"}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_semantic_search_returns_similarity(self):
        r = requests.get(f"{BASE_URL}/api/memory/search", params={"q": "consciousness", "limit": 5}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        for result in r.json()["results"]:
            assert "id" in result
            assert "similarity" in result
            assert 0 <= result["similarity"] <= 1


class TestNewAgents:
    def test_analyze_includes_identity_stabilizer(self):
        r = requests.post(
            f"{BASE_URL}/api/agents/analyze",
            json={"content": "Maintaining core values under pressure"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert "identity_stabilizer" in data["agents"]
        assert "execution" in data["agents"]
