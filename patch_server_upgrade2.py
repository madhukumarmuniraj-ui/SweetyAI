import os
import sys
import time
import subprocess
import requests

with open("server.py", "r") as f:
    code = f.read()

is_fastapi = "FastAPI" in code

gateway_helpers = '''
# === SweetyAI Unified 8-Capability HTTP Agent Gateway ===
import json as _ gw_json
import os as _gw_os

def _execute_agent_gateway_status():
    state = {}
    if _gw_os.path.exists("sweety_daemon_state.json"):
        try:
            with open("sweety_daemon_state.json", "r") as f:
                state = _gw_json.load(f)
        except Exception:
            pass
    return {
        "status": "online",
        "capabilities": [
            "1_8_headless_devtools_autopatch",
            "2_realtime_vision_screen_awareness",
            "3_4_24x7_proactive_daemon",
            "5_multi_app_orchestrator",
            "6_operational_seo_lead_content_pipeline",
            "7_multi_agent_swarm_sdk",
            "legal_rag_bns_bnss_bsa",
        ],
        "daemon_state": state,
    }

def _execute_agent_gateway_dispatch(payload):
    agent_type = payload.get("agent", "swarm")
    target = payload.get("target", "Section 35 BNSS and Section 61 BNS Safeguards")
    if agent_type == "swarm":
        from sweety_sdk import SwarmOrchestrator
        ctx = SwarmOrchestrator().run_swarm(target)
        return {
            "agent": "swarm",
            "objective": ctx.objective,
            "sources": ctx.sources,
            "audit_log": ctx.audit_log,
            "verification": ctx.artifacts.get("verification_report"),
        }
    elif agent_type == "orchestrate":
        from orchestrator_agent import orchestrate_command
        orchestrate_command(target)
        return {"agent": "orchestrate", "command": target, "artifacts_dir": "workspace_orchestrations"}
    elif agent_type == "pipeline":
        from pipeline_agent import run_operational_pipeline
        run_operational_pipeline(target)
        return {"agent": "pipeline", "niche": target, "artifacts_dir": "operational_pipelines"}
    elif agent_type == "devtools":
        from devtools_agent import audit_and_patch
        audit_and_patch(target, auto_patch=bool(payload.get("patch", False)))
        return {"agent": "devtools", "target": target}
    elif agent_type == "vision":
        from vision_agent import analyze_screen
        analyze_screen(target)
        return {"agent": "vision", "question": target}
    return {"error": f"Unknown agent '{agent_type}'"}
'''

gateway_helpers = gateway_helpers.replace("import json as _ gw_json", "import json as _gw_json")

if is_fastapi:
    routes_code = gateway_helpers + '''
@app.get("/agents/status")
def api_agents_status():
    return _execute_agent_gateway_status()

@app.post("/agents/dispatch")
def api_agents_dispatch(payload: dict):
    return _execute_agent_gateway_dispatch(payload)
'''
else:
    routes_code = gateway_helpers + '''
@app.route("/agents/status", methods=["GET"])
def api_agents_status():
    from flask import jsonify
    return jsonify(_execute_agent_gateway_status())

@app.route("/agents/dispatch", methods=["POST"])
def api_agents_dispatch():
    from flask import request, jsonify
    payload = request.get_json(force=True) or {}
    return jsonify(_execute_agent_gateway_dispatch(payload))
'''

if "/agents/status" not in code:
    if 'if __name__' in code:
        parts = code.split('if __name__')
        new_code = parts[0] + "\n" + routes_code + "\nif __name__" + parts[1]
    else:
        new_code = code + "\n" + routes_code
    with open("server.py", "w") as f:
        f.write(new_code)
    print("[Upgrade 2] Injected /agents/status and /agents/dispatch into server.py!")
else:
    print("[Upgrade 2] Endpoints already present in server.py.")

# Restart server.py cleanly so new routes take effect
subprocess.run(["pkill", "-f", "server.py"], stderr=subprocess.DEVNULL)
time.sleep(1)
py_bin = "./venv/bin/python3" if os.path.exists("./venv/bin/python3") else sys.executable
subprocess.Popen(
    f"nohup {py_bin} server.py >> sweety_server.log 2>&1 &",
    shell=True,
    preexec_fn=os.setsid,
)
time.sleep(3)

print("\n=== Testing Live HTTP Agent Gateway on 127.0.0.1:8765 ===")
r_stat = requests.get("http://127.0.0.1:8765/agents/status", timeout=5)
print("[GET /agents/status] Response:")
print(json.dumps(r_stat.json(), indent=2) if "json" in dir() else r_stat.text)

r_disp = requests.post(
    "http://127.0.0.1:8765/agents/dispatch",
    json={
        "agent": "swarm",
        "target": "Compare IPC 120A/420 and CrPC 41A/438/482 with BNS 61/318 and BNSS 35/482/528 under Bhajan Lal and Satender Kumar Antil",
    },
    timeout=10,
)
print("\n[POST /agents/dispatch (Swarm)] Response:")
import json
print(json.dumps(r_disp.json(), indent=2))
print("=========================================================\n")
