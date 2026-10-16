import pytest
from app.orchestrator import intent_router_node, build_sweety_graph, SweetyAgentState

class MockAgent:
    def chat(self, prompt: str) -> str:
        return f"[Mock Answer for query in prompt]"

def test_intent_router_node():
    state1 = {"user_message": "What is the latest news about AI?", "intent": "", "tool_output": "", "rag_context": "", "chat_history": "", "draft_response": "", "final_response": ""}
    assert intent_router_node(state1)["intent"] == "web_search_agent"

    state2 = {"user_message": "Explain Article 21 Indian Constitution statute", "intent": "", "tool_output": "", "rag_context": "", "chat_history": "", "draft_response": "", "final_response": ""}
    assert intent_router_node(state2)["intent"] == "legal_research_agent"

    state3 = {"user_message": "Hello Sweety how are you?", "intent": "", "tool_output": "", "rag_context": "", "chat_history": "", "draft_response": "", "final_response": ""}
    assert intent_router_node(state3)["intent"] == "general_reasoning_agent"

def test_build_sweety_graph():
    mock_agent = MockAgent()
    graph = build_sweety_graph(mock_agent)
    assert graph is not None

    initial_state = {
        "user_message": "Write a quick test greeting",
        "intent": "",
        "tool_output": "",
        "rag_context": "",
        "chat_history": "",
        "draft_response": "",
        "final_response": ""
    }
    result = graph.invoke(initial_state)
    assert "final_response" in result
    assert len(result["final_response"]) > 0
