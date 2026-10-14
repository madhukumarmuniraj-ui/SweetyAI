import sys
import os

print("--- STARTING SWEETY-AI ORCHESTRATOR DIAGNOSTIC ---")

try:
    from app.main import load_model
    from app.agent.agent import Agent
    from app.orchestrator import build_sweety_graph
    print("1. Successfully imported core architecture modules.")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

try:
    print("2. Loading Qwen model weights...")
    tokenizer, model = load_model()
    agent = Agent(model=model, tokenizer=tokenizer)
    print("✅ Model loaded successfully.")
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    sys.exit(1)

try:
    print("3. Compiling LangGraph State Orchestrator...")
    sweety_app = build_sweety_graph(agent)
    print("✅ Orchestrator graph compiled successfully.")
except Exception as e:
    print(f"❌ Graph compilation failed: {e}")
    sys.exit(1)

# Test invocation
print("4. Testing orchestrator execution with a sample legal query...")
initial_state = {
    "user_message": "What is Article 21 of the Constitution of India?",
    "intent": "legal_research",
    "tool_output": "",
    "rag_context": "Article 21: Protection of life and personal liberty.",
    "chat_history": "",
    "draft_response": "",
    "final_response": ""
}

try:
    result = sweety_app.invoke(initial_state)
    print("\n✨ ORCHESTRATOR EXECUTION SUCCESSFUL!")
    print("--- Final Response Output ---")
    print(result.get("final_response", "No final response found in state."))
except Exception as e:
    print(f"❌ Orchestrator execution failed during invoke: {e}")