import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb

app = FastAPI(title="SweetyAI Hybrid Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chroma_client = chromadb.PersistentClient(path="./sweetyai_legal_db")
collection = chroma_client.get_or_create_collection(name="legal_documents")

class ChatInput(BaseModel):
    message: str

class DocumentInput(BaseModel):
    doc_id: str
    text: str
    source: str

@app.post("/chat")
def chat(data: ChatInput):
    msg = data.message.lower()
    response = "How can I help? I have both quick response mode and deep thinking capabilities for research and analysis."
    if "section 302" in msg or "murder" in msg:
        response = "Section 302 of the Indian Penal Code, 1860 prescribes punishment for murder: death or imprisonment for life, and liability for a fine."
    return {"response": response, "status": "success"}

@app.post("/ingest")
def ingest_document(data: DocumentInput):
    try:
        collection.add(
            documents=[data.text],
            metadatas=[{"source": data.source}],
            ids=[data.doc_id]
        )
        return {"status": "success", "message": f"Document '{data.doc_id}' indexed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag-chat")
def rag_chat(data: ChatInput):
    try:
        results = collection.query(
            query_texts=[data.message],
            n_results=4
        )
        retrieved_docs = results.get("documents", [[]])[0]
        sources = results.get("metadatas", [[]])[0]
        
        context = "\n\n".join(retrieved_docs) if retrieved_docs else "No local legal context found."
        source_name = sources[0].get("source", "Local Legal Database") if sources else "General Knowledge"

        response_text = f"[RAG Mode via {source_name}] Based on your local files: {context}"
        return {
            "response": response_text,
            "sources": [s.get("source") for s in sources],
            "status": "success"
        }
    except Exception as e:
        return {"response": f"RAG execution error: {str(e)}", "status": "error"}



# === SweetyAI Unified 8-Capability HTTP Agent Gateway ===
import json as _gw_json
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

@app.get("/agents/status")
def api_agents_status():
    return _execute_agent_gateway_status()

@app.post("/agents/dispatch")
def api_agents_dispatch(payload: dict):
    return _execute_agent_gateway_dispatch(payload)

if __name__ == "__main__":
    print("[SweetyAI] Starting hybrid intelligence server on 127.0.0.1:8765")
    uvicorn.run(app, host="127.0.0.1", port=8765)
