"""Backend tests for SARAI Jarvis 3.0"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


class TestHealth:
    def test_health(self):
        r = requests.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "online"


class TestStats:
    def test_get_stats(self):
        r = requests.get(f"{BASE_URL}/api/stats")
        assert r.status_code == 200
        data = r.json()
        assert "total_thoughts" in data
        assert "total_connections" in data
        assert "brain_coherence" in data


class TestGraph:
    def test_get_graph(self):
        r = requests.get(f"{BASE_URL}/api/graph")
        assert r.status_code == 200
        data = r.json()
        assert "nodes" in data
        assert "links" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["links"], list)


class TestTimeline:
    def test_get_timeline(self):
        r = requests.get(f"{BASE_URL}/api/timeline")
        assert r.status_code == 200
        data = r.json()
        assert "entries" in data
        assert isinstance(data["entries"], list)


class TestThoughts:
    created_id = None

    def test_post_thought(self):
        r = requests.post(f"{BASE_URL}/api/thoughts", json={"content": "TEST_ artificial intelligence and machine learning"})
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
        r = requests.get(f"{BASE_URL}/api/graph")
        data = r.json()
        ids = [n["id"] for n in data["nodes"]]
        assert TestThoughts.created_id in ids

    def test_delete_thought(self):
        if not TestThoughts.created_id:
            pytest.skip("No created_id")
        r = requests.delete(f"{BASE_URL}/api/thoughts/{TestThoughts.created_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["deleted"] == TestThoughts.created_id

    def test_delete_removes_from_graph(self):
        if not TestThoughts.created_id:
            pytest.skip("No created_id")
        r = requests.get(f"{BASE_URL}/api/graph")
        ids = [n["id"] for n in r.json()["nodes"]]
        assert TestThoughts.created_id not in ids


class TestChat:
    def test_chat(self):
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": "Hello SARAI, what are you?"})
        assert r.status_code == 200
        data = r.json()
        assert "response" in data
        assert len(data["response"]) > 0


class TestAgentAnalyze:
    def test_analyze(self):
        r = requests.post(f"{BASE_URL}/api/agents/analyze", json={"content": "Consciousness and its relationship to AI"})
        assert r.status_code == 200
        data = r.json()
        assert "agents" in data
        assert len(data["agents"]) > 0
