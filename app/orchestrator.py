import os
import sys
import re
from typing import TypedDict
try:
    from langgraph.graph import StateGraph, START, END
except ImportError:  # langgraph not installed — use the built-in sequential shim
    from app.langgraph_shim import StateGraph, START, END
from app.memory import get_recent_history, add_message
from rag import search_knowledge_base
from app.tools import AVAILABLE_TOOLS

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Try importing and loading the compiled DSPy legal optimization pipeline
try:
    from app.optimizer import SweetyLegalOptimizer
    dspy_legal_optimizer = SweetyLegalOptimizer()
    dspy_legal_optimizer.load("app/compiled_models/optimized_legal_agent.json")
    DSPY_AVAILABLE = True
    print("[Orchestrator] Loaded compiled DSPy optimized legal pipeline.")
except Exception:
    DSPY_AVAILABLE = False

class SweetyAgentState(TypedDict):
    user_message: str
    intent: str
    tool_output: str
    rag_context: str
    chat_history: str
    draft_response: str
    final_response: str

def clean_response_text(text: str) -> str:
    """Removes any internal thinking tokens, draft tags, or auditor meta artifacts."""
    if not text:
        return ""
    # Strip <think> tags
    text = re.sub(r'<think>[\s\S]*?</think>', '', text)
    # Strip thoughts
    text = re.sub(r'\[.*?Thought.*?\]:[\s\S]*?(?=\[Answer\]|AI:|$)', '', text, flags=re.IGNORECASE)
    # Strip meta prefixes
    for prefix in [
        "Verified Final Answer:",
        "Final Answer:",
        "Draft Output:",
        "[Answer]:",
        "AI:",
        "Assistant:",
        "SweetyAI:",
    ]:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
        text = text.replace(f"\n{prefix}", "\n").strip()
    return text.strip()

def execute_direct_tools(message: str) -> str:
    """Executes matching local tools directly to ensure 100% responsiveness."""
    msg = message.lower().strip()

    # System Metrics & Info
    if any(k in msg for k in ["system info", "system metric", "cpu usage", "ram usage", "memory usage", "disk space", "hardware status"]):
        return AVAILABLE_TOOLS["get_system_info"]()

    # Time & Date
    if any(k in msg for k in ["what time", "current time", "what date", "today's date", "current date", "what day is"]):
        return f"Current Time & Date: {AVAILABLE_TOOLS['get_current_time']()}"

    # Launch Desktop Apps
    app_match = re.search(r'(?:open|launch|start|run)\s+(notepad|calculator|calc|explorer|code|vscode|cmd|terminal|chrome|edge)', msg)
    if app_match:
        app_name = app_match.group(1)
        return AVAILABLE_TOOLS["open_application"](app_name)

    # Clipboard Read
    if any(k in msg for k in ["read clipboard", "what is in my clipboard", "show clipboard", "paste clipboard", "check clipboard"]):
        return f"Clipboard Content:\n{AVAILABLE_TOOLS['read_clipboard_text']()}"

    # Open Workspace Folder
    if any(k in msg for k in ["open workspace", "open folder", "open knowledge folder", "show workspace"]):
        return AVAILABLE_TOOLS["open_workspace_folder"]()

    # List Knowledge Documents
    if any(k in msg for k in ["list document", "list files in knowledge", "show indexed files", "what files are in knowledge"]):
        return AVAILABLE_TOOLS["list_knowledge_documents"]()

    # Calculator
    calc_match = re.search(r'(?:calculate|what is|compute)\s+([0-9\.\s\+\-\*\/\(\)\^\%]+)', msg)
    if calc_match:
        expr = calc_match.group(1).strip()
        if any(op in expr for op in ["+", "-", "*", "/", "%", "^"]):
            return f"Calculation Result for ({expr}): {AVAILABLE_TOOLS['calculator'](expr)}"

    return ""

def intent_router_node(state: SweetyAgentState) -> dict:
    """Manager node that determines which specialized sub-agent should handle the task."""
    msg = state.get("user_message", "").lower()

    # Check for direct local tool execution
    direct_tool_result = execute_direct_tools(state.get("user_message", ""))
    tool_out = state.get("tool_output", "")
    if direct_tool_result:
        tool_out = f"{tool_out}\n\n{direct_tool_result}".strip()

    if tool_out:
        intent = "general_reasoning_agent"
    elif any(k in msg for k in ["search", "latest", "news", "current", "web", "online"]):
        intent = "web_search_agent"
    elif any(k in msg for k in ["statute", "case law", "section ", "legal provision", "ipc ", "crpc ", "kslu", "bare act"]):
        intent = "legal_research_agent"
    else:
        intent = "general_reasoning_agent"

    print(f"[Multi-Agent Manager] Delegating task to sub-agent: [{intent}]")
    return {"intent": intent, "tool_output": tool_out}

def legal_research_agent_node(state: SweetyAgentState, agent) -> dict:
    """Specialized Sub-Agent for local legal statutes using the DSPy Optimization Loop."""
    print("[Legal Specialist] Interrogating knowledge base...")
    query = state.get("user_message", "")
    clipboard_data = state.get("tool_output", "")
    context = search_knowledge_base(query, n_results=4)

    input_text = clipboard_data or (query + "\n\n[Knowledge Base Context]:\n" + str(context))

    if DSPY_AVAILABLE:
        try:
            prediction = dspy_legal_optimizer(input_text=input_text, jurisdiction_context="Indian Legal Framework (KSLU)")
            draft = (
                f"Legal Analysis:\n"
                f"• Legal Issues: {prediction.legal_issues}\n"
                f"• Statutory Provisions: {prediction.statutory_provisions}\n"
                f"• Summary: {prediction.audited_summary}"
            )
        except Exception as e:
            print(f"[DSPy Fallback]: {e}")
            prompt = (
                f"You are the Legal Research Specialist for SweetyAI. "
                f"Analyze the following knowledge base context and answer the query clearly:\n\n"
                f"[Knowledge Base Context]:\n{context}\n\n"
                f"[Query]: {query}"
            )
            draft = agent.chat(prompt)
    else:
        prompt = (
            f"You are the Legal Research Specialist for SweetyAI. "
            f"Analyze the following knowledge base context and answer the query clearly:\n\n"
            f"[Knowledge Base Context]:\n{context}\n\n"
            f"[Query]: {query}"
        )
        draft = agent.chat(prompt)

    return {"rag_context": draft}

def web_research_agent_node(state: SweetyAgentState, agent) -> dict:
    """Specialized Sub-Agent for live web reconnaissance."""
    print("[Web Specialist] Querying web search...")
    tool_output = state.get("tool_output", "")
    query = state.get("user_message", "")
    if not tool_output:
        search_fn = AVAILABLE_TOOLS.get("search_searxng") or AVAILABLE_TOOLS.get("web_search")
        if search_fn:
            try:
                tool_output = search_fn(query)
            except Exception as e:
                tool_output = f"Web search error: {e}"

    prompt = (
        f"You are SweetyAI. Summarize the web findings below to answer the user's question directly and politely:\n\n"
        f"[Web Findings]:\n{tool_output}\n\n"
        f"[User Question]: {query}"
    )
    draft = agent.chat(prompt)
    return {"tool_output": draft}

def general_reasoning_agent_node(state: SweetyAgentState, agent) -> dict:
    """General task execution agent with natural conversational responses."""
    user_msg = state.get("user_message", "")
    tool_out = state.get("tool_output", "")
    rag_ctx = state.get("rag_context", "")
    history = get_recent_history(limit=2)

    # Clean direct chat for simple user messages
    if not tool_out and not rag_ctx and not history:
        draft = agent.chat(user_msg)
    else:
        prompt_parts = []
        if history:
            prompt_parts.append(f"[Conversation History]:\n{history}")
        if tool_out:
            prompt_parts.append(f"[Tool Execution Result]:\n{tool_out}")
        if rag_ctx:
            prompt_parts.append(f"[Knowledge Context]:\n{rag_ctx}")
        prompt_parts.append(f"User: {user_msg}")
        prompt = "\n\n".join(prompt_parts)
        draft = agent.chat(prompt)

    return {"draft_response": draft}

def evaluator_optimizer_node(state: SweetyAgentState, agent) -> dict:
    """Senior Auditor Node: Finalizes output cleanly without robotic meta-tags."""
    intent = state.get("intent", "general_reasoning_agent")
    user_msg = state.get("user_message", "")

    # For general chat, direct tool results, or sub-agent outputs, use the clean response directly
    raw_response = state.get("draft_response") or state.get("rag_context") or state.get("tool_output") or ""

    if state.get("tool_output") and any(k in state["tool_output"] for k in ["System Information:", "Current Time & Date:", "Calculation Result", "Launched", "Clipboard Content:"]):
        final = state["tool_output"]
    else:
        final = clean_response_text(raw_response)

    try:
        add_message("user", user_msg)
        add_message("assistant", final)
    except Exception as e:
        print(f"[Evaluator-Optimizer] Note: chat history log warning: {e}")

    return {"final_response": final}

def build_sweety_graph(agent):
    """Compiles the multi-agent orchestration graph."""
    workflow = StateGraph(SweetyAgentState)

    workflow.add_node("router", intent_router_node)
    workflow.add_node("legal_agent", lambda s: legal_research_agent_node(s, agent))
    workflow.add_node("web_agent", lambda s: web_research_agent_node(s, agent))
    workflow.add_node("general_agent", lambda s: general_reasoning_agent_node(s, agent))
    workflow.add_node("evaluator", lambda s: evaluator_optimizer_node(s, agent))

    workflow.add_edge(START, "router")

    workflow.add_conditional_edges(
        "router",
        lambda state: state["intent"],
        {
            "legal_research_agent": "legal_agent",
            "web_search_agent": "web_agent",
            "general_reasoning_agent": "general_agent"
        }
    )

    workflow.add_edge("legal_agent", "evaluator")
    workflow.add_edge("web_agent", "evaluator")
    workflow.add_edge("general_agent", "evaluator")
    workflow.add_edge("evaluator", END)

    return workflow.compile()
