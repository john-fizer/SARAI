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


class TestExport:
    def test_export_returns_structure(self):
        r = requests.get(f"{BASE_URL}/api/export", headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "nodes" in data
        assert "edges" in data
        assert "stats" in data
        assert "version" in data
        assert "exported_at" in data

    def test_export_stats_match(self):
        r = requests.get(f"{BASE_URL}/api/export", headers=AUTH_HEADERS)
        data = r.json()
        assert data["stats"]["total_nodes"] == len(data["nodes"])
        assert data["stats"]["total_edges"] == len(data["edges"])


class TestSearch:
    def test_search_returns_results(self):
        r = requests.get(f"{BASE_URL}/api/search", params={"q": "intelligence"}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "results" in data
        assert "query" in data
        assert isinstance(data["results"], list)

    def test_search_result_fields(self):
        r = requests.get(f"{BASE_URL}/api/search", params={"q": "test", "limit": 5}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        for result in r.json()["results"]:
            assert "id" in result
            assert "score" in result
            assert "match_type" in result

    def test_search_requires_query(self):
        r = requests.get(f"{BASE_URL}/api/search", headers=AUTH_HEADERS)
        assert r.status_code == 422


class TestGraphClusters:
    def test_clusters_returns_structure(self):
        r = requests.get(f"{BASE_URL}/api/graph/clusters", headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "clusters" in data
        assert "cluster_count" in data
        assert isinstance(data["clusters"], dict)
        assert isinstance(data["cluster_count"], int)


class TestGraphPath:
    def test_path_with_invalid_ids(self):
        r = requests.get(
            f"{BASE_URL}/api/graph/path",
            params={"from_id": "nonexistent1", "to_id": "nonexistent2"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert "found" in data
        assert data["found"] is False

    def test_path_requires_params(self):
        r = requests.get(f"{BASE_URL}/api/graph/path", headers=AUTH_HEADERS)
        assert r.status_code == 422


class TestConsensus:
    def test_consensus_returns_structure(self):
        r = requests.post(
            f"{BASE_URL}/api/agents/consensus",
            json={"content": "The nature of consciousness and self-awareness"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert "consensus" in data
        assert "agents" in data
        assert isinstance(data["agents"], dict)

    def test_consensus_has_all_agents(self):
        r = requests.post(
            f"{BASE_URL}/api/agents/consensus",
            json={"content": "Memory and learning"},
            headers=AUTH_HEADERS,
        )
        data = r.json()
        expected_agents = {"analyst", "strategist", "memory_curator", "skeptic", "emotional", "identity_stabilizer", "execution"}
        assert expected_agents.issubset(set(data["agents"].keys()))


class TestSimulate:
    def test_simulate_returns_scenarios(self):
        r = requests.post(
            f"{BASE_URL}/api/simulate",
            json={"content": "Building a second brain system"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert "scenarios" in data
        assert isinstance(data["scenarios"], list)
        assert len(data["scenarios"]) > 0

    def test_simulate_scenario_fields(self):
        r = requests.post(
            f"{BASE_URL}/api/simulate",
            json={"content": "AI and cognition"},
            headers=AUTH_HEADERS,
        )
        for scenario in r.json()["scenarios"]:
            assert "title" in scenario
            assert "probability" in scenario
            assert "description" in scenario


class TestDebate:
    def test_debate_returns_structure(self):
        r = requests.post(
            f"{BASE_URL}/api/agents/debate",
            json={"content": "Is AI capable of genuine creativity?"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert "debate" in data
        assert "thought" in data
        assert "rounds" in data
        assert data["rounds"] == 2

    def test_debate_agents_have_positions(self):
        r = requests.post(
            f"{BASE_URL}/api/agents/debate",
            json={"content": "The role of emotion in decision making"},
            headers=AUTH_HEADERS,
        )
        for agent_key, entry in r.json()["debate"].items():
            assert "position" in entry or "rebuttal" in entry


class TestPlan:
    def test_plan_returns_steps(self):
        r = requests.post(
            f"{BASE_URL}/api/plan",
            json={"content": "Build a personal knowledge management system"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert "steps" in data or "plan" in data or "first_move" in data

    def test_plan_requires_content(self):
        r = requests.post(f"{BASE_URL}/api/plan", json={}, headers=AUTH_HEADERS)
        assert r.status_code == 422


class TestPredict:
    def test_predict_returns_forecasts(self):
        r = requests.post(
            f"{BASE_URL}/api/predict",
            json={"content": "Advances in neural interfaces"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert "predictions" in data or "forecasts" in data or "scenarios" in data


class TestSelfImprove:
    def test_self_improve_returns_analysis(self):
        r = requests.get(f"{BASE_URL}/api/reflect/improve", headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        # Returns analysis dict or message when no reflection data yet
        assert isinstance(data, dict)
