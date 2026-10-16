import json
import pytest
import threading
import urllib.request
import urllib.parse
from http.server import ThreadingHTTPServer
import tempfile
import os
import time

from server import Handler
from app.graph.knowledge_graph import get_knowledge_graph
from app.sandbox.sandbox_engine import SandboxEngine
from app.legal.clause_triager import ClauseTriager
from app.legal.statute_verifier import StatuteVerifier
from app.adaptive.dry_run_patcher import DryRunPatcher


@pytest.fixture(scope="module")
def api_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    yield base_url
    server.shutdown()
    server.server_close()


def test_graph_endpoints(api_server):
    kg = get_knowledge_graph()
    kg.add_node("TEST_STATUTE_API", "Statute", {"title": "Test Arbitration Statute"})

    # Test /graph/stats
    with urllib.request.urlopen(f"{api_server}/graph/stats") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["ok"] is True
        assert data["node_count"] >= 1

    # Test /graph/search
    with urllib.request.urlopen(f"{api_server}/graph/search?q=Arbitration") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["ok"] is True
        assert len(data["results"]) >= 1


def test_legal_endpoints(api_server):
    # Test /legal/verify-statute
    payload = json.dumps({"section": "73", "act_name": "Indian Contract Act"}).encode("utf-8")
    req = urllib.request.Request(
        f"{api_server}/legal/verify-statute",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["ok"] is True
        assert data["verification"]["is_valid"] is True

    # Test /legal/triage
    contract_text = "The consultant agrees to infinite indemnification liability for any loss."
    payload = json.dumps({"contract_text": contract_text}).encode("utf-8")
    req = urllib.request.Request(
        f"{api_server}/legal/triage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["ok"] is True
        assert data["report"]["red_count"] >= 1


def test_sandbox_and_patch_endpoints(api_server):
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "code.py")
        with open(test_file, "w") as f:
            f.write("def foo():\n    return 42\n")

        # Preview patch
        new_code = "def foo():\n    return 100\n"
        payload = json.dumps({"filepath": test_file, "new_content": new_code}).encode("utf-8")
        req = urllib.request.Request(
            f"{api_server}/patch/preview",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True
            assert data["preview"]["lines_changed"] >= 1

        # Apply patch
        req = urllib.request.Request(
            f"{api_server}/patch/apply",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True
            assert data["checkpoint_id"] is not None

        # Verify disk
        with open(test_file, "r") as f:
            content = f.read()
        assert content == new_code


def test_adaptive_cadence_and_persona_endpoints(api_server):
    events = [
        {"key": "a", "timestamp": 1000.0},
        {"key": "b", "timestamp": 1100.0},
        {"key": "c", "timestamp": 1200.0},
        {"key": "d", "timestamp": 1300.0},
    ]
    payload = json.dumps({"events": events, "duration_ms": 300.0}).encode("utf-8")
    req = urllib.request.Request(
        f"{api_server}/adaptive/cadence",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["ok"] is True
        assert data["metrics"]["cognitive_state"] in ("FOCUSED_FLOW", "URGENT_BURST", "BALANCED")
        assert "persona" in data
