"""
SweetyAI General Intelligence Orchestrator V2
Systems that reason, learn, and solve problems across any domain like a human.

Architecture:
- Multi-Agent Reasoning System with Reflective Learning
- Cross-Domain Knowledge Integration
- Meta-Learning & Self-Improvement Loop
- Chain-of-Thought Reasoning with Verification
- Memory Consolidation & Pattern Recognition
"""

import os
import sys
import re
import json
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from app.memory import get_recent_history, add_message
from rag import search_knowledge_base
from app.tools import AVAILABLE_TOOLS
from app.graph.knowledge_graph import get_knowledge_graph
from app.graph.conflict_detector import ConflictDetector
from app.graph.hybrid_retriever import HybridRetriever
from app.sandbox.self_healing_agent import SelfHealingAgent
from app.sandbox.sandbox_engine import SandboxEngine
from app.legal.clause_triager import ClauseTriager
from app.legal.statute_verifier import StatuteVerifier
from app.legal.brief_synthesizer import BriefSynthesizer
from app.ambient.context_prefetcher import ContextPrefetcher
from app.ambient.anomaly_detector import AnomalyDetector
from app.adaptive.dry_run_patcher import DryRunPatcher

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Try importing DSPy optimization
try:
    from app.optimizer import SweetyLegalOptimizer
    dspy_legal_optimizer = SweetyLegalOptimizer()
    dspy_legal_optimizer.load("app/compiled_models/optimized_legal_agent.json")
    DSPY_AVAILABLE = True
    print("[Orchestrator V2] Loaded DSPy optimized pipeline.")
except Exception:
    DSPY_AVAILABLE = False

# Enhanced State with Learning & Reasoning Chains
class GeneralIntelligenceState(TypedDict):
    # Input
    user_message: str
    timestamp: str
    session_id: str

    # Reasoning Chain
    intent: str
    domain: str
    complexity_score: float
    reasoning_chain: List[Dict[str, Any]]

    # Knowledge Integration
    tool_output: str
    rag_context: str
    web_context: str
    chat_history: str

    # Learning & Memory
    learned_patterns: List[Dict[str, Any]]
    confidence_score: float
    uncertainty_areas: List[str]

    # Output
    draft_response: str
    final_response: str
    metadata: Dict[str, Any]


class ReasoningEngine:
    """Advanced reasoning engine with chain-of-thought and verification."""

    @staticmethod
    def analyze_complexity(message: str) -> float:
        """Analyze task complexity (0.0 = simple, 1.0 = highly complex)."""
        complexity = 0.0

        # Multiple questions increase complexity
        questions = message.count('?')
        complexity += min(questions * 0.15, 0.3)

        # Technical terms increase complexity
        technical_keywords = [
            'algorithm', 'implement', 'design', 'architecture', 'optimize',
            'calculate', 'analyze', 'compare', 'evaluate', 'synthesize'
        ]
        tech_count = sum(1 for kw in technical_keywords if kw in message.lower())
        complexity += min(tech_count * 0.1, 0.3)

        # Length and structure
        word_count = len(message.split())
        if word_count > 50:
            complexity += 0.2
        elif word_count > 100:
            complexity += 0.3

        # Conditional/logical structures
        logical_words = ['if', 'then', 'because', 'therefore', 'however', 'although']
        logic_count = sum(1 for lw in logical_words if lw in message.lower())
        complexity += min(logic_count * 0.05, 0.2)

        return min(complexity, 1.0)

    @staticmethod
    def identify_domain(message: str) -> str:
        """Identify the primary domain of the query."""
        msg = message.lower()

        # Domain patterns
        domains = {
            'legal': ['law', 'legal', 'statute', 'case', 'court', 'section', 'ipc', 'crpc', 'bns', 'contract', 'clause', 'indemnity', 'arbitration', 'agreement', 'redline', 'playbook'],
            'technical': ['code', 'programming', 'algorithm', 'software', 'debug', 'api', 'sandbox', 'heal', 'fix error', 'traceback', 'exception', 'python', 'function', 'class', 'patch', 'diff'],
            'graph': ['knowledge graph', 'subgraph', 'entity relationship', 'precedent chain', 'overruled'],
            'ambient': ['active window', 'screen anomaly', 'foreground app', 'screen context', 'ocr text'],
            'scientific': ['research', 'experiment', 'hypothesis', 'theory', 'data', 'analysis'],
            'mathematical': ['calculate', 'equation', 'formula', 'solve', 'proof', 'theorem'],
            'creative': ['design', 'create', 'write', 'story', 'poem', 'art', 'music'],
            'business': ['market', 'strategy', 'finance', 'revenue', 'business', 'economics'],
            'medical': ['health', 'medical', 'symptom', 'diagnosis', 'treatment', 'disease'],
            'general': []  # default fallback
        }

        for domain, keywords in domains.items():
            if any(kw in msg for kw in keywords):
                return domain

        return 'general'

    @staticmethod
    def generate_reasoning_chain(message: str, domain: str, complexity: float) -> List[Dict[str, Any]]:
        """Generate a chain-of-thought reasoning plan."""
        chain = []

        # Step 1: Understanding
        chain.append({
            'step': 'understanding',
            'description': 'Parse and understand the user query',
            'status': 'pending'
        })

        # Step 2: Knowledge Retrieval (if complex enough)
        if complexity > 0.3:
            chain.append({
                'step': 'knowledge_retrieval',
                'description': 'Gather relevant context from knowledge base, graph, and tools',
                'status': 'pending'
            })

        # Step 3: Reasoning (domain-specific)
        if domain == 'mathematical':
            chain.append({
                'step': 'calculation',
                'description': 'Perform mathematical operations and verify results',
                'status': 'pending'
            })
        elif domain == 'legal':
            chain.append({
                'step': 'legal_analysis',
                'description': 'Analyze statutory provisions, playbook rules, and precedents',
                'status': 'pending'
            })
        elif domain == 'technical':
            chain.append({
                'step': 'code_analysis_and_sandbox',
                'description': 'Analyze code logic, AST safety bounds, and sandbox execution',
                'status': 'pending'
            })
        elif domain == 'graph':
            chain.append({
                'step': 'graph_traversal',
                'description': 'Traverse entity subgraphs and cross-reference citations',
                'status': 'pending'
            })
        elif domain == 'ambient':
            chain.append({
                'step': 'ambient_screen_reasoning',
                'description': 'Analyze active window context and screen OCR anomalies',
                'status': 'pending'
            })
        else:
            chain.append({
                'step': 'reasoning',
                'description': 'Apply domain knowledge and logical reasoning',
                'status': 'pending'
            })

        # Step 4: Verification (for complex tasks)
        if complexity > 0.5:
            chain.append({
                'step': 'verification',
                'description': 'Verify reasoning and check for errors',
                'status': 'pending'
            })

        # Step 5: Synthesis
        chain.append({
            'step': 'synthesis',
            'description': 'Synthesize final response',
            'status': 'pending'
        })

        return chain


class LearningEngine:
    """Meta-learning engine that improves over time."""

    def __init__(self):
        self.learning_db_path = "app/memory/learned_patterns.json"
        self.patterns = self.load_patterns()

    def load_patterns(self) -> List[Dict[str, Any]]:
        """Load learned patterns from disk."""
        try:
            if os.path.exists(self.learning_db_path):
                with open(self.learning_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[Learning Engine] Could not load patterns: {e}")
        return []

    def save_patterns(self):
        """Persist learned patterns to disk."""
        try:
            os.makedirs(os.path.dirname(self.learning_db_path), exist_ok=True)
            with open(self.learning_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Learning Engine] Could not save patterns: {e}")

    def learn_from_interaction(self, state: GeneralIntelligenceState):
        """Extract patterns from successful interactions."""
        pattern = {
            'timestamp': state.get('timestamp'),
            'domain': state.get('domain'),
            'complexity': state.get('complexity_score'),
            'intent': state.get('intent'),
            'confidence': state.get('confidence_score', 0.0),
            'query_pattern': self._extract_pattern(state.get('user_message', '')),
            'successful': state.get('confidence_score', 0) > 0.7
        }

        self.patterns.append(pattern)

        # Keep only recent patterns (last 1000)
        if len(self.patterns) > 1000:
            self.patterns = self.patterns[-1000:]

        self.save_patterns()

    def _extract_pattern(self, message: str) -> str:
        """Extract reusable pattern from message."""
        # Simplify to pattern by removing specifics
        pattern = message.lower()
        pattern = re.sub(r'\d+', '<NUM>', pattern)
        pattern = re.sub(r'\b[A-Z][a-z]+\b', '<NAME>', pattern)
        return pattern[:200]  # Limit length

    def get_similar_patterns(self, message: str, domain: str) -> List[Dict[str, Any]]:
        """Find similar successful patterns."""
        pattern = self._extract_pattern(message)
        similar = []

        for p in self.patterns:
            if p['domain'] == domain and p['successful']:
                # Simple similarity check
                if any(word in p['query_pattern'] for word in pattern.split()[:5]):
                    similar.append(p)

        return similar[:5]  # Top 5 similar patterns


# Global learning engine
learning_engine = LearningEngine()


def clean_response_text(text: str) -> str:
    """Removes internal thinking tokens and meta artifacts."""
    if not text:
        return ""
    text = re.sub(r'<think>[\s\S]*?</think>', '', text)
    text = re.sub(r'\[.*?Thought.*?\]:[\s\S]*?(?=\[Answer\]|AI:|$)', '', text, flags=re.IGNORECASE)
    for prefix in ["Verified Final Answer:", "Final Answer:", "Draft Output:", "[Answer]:", "AI:", "Assistant:", "SweetyAI:"]:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
        text = text.replace(f"\n{prefix}", "\n").strip()
    return text.strip()


def execute_direct_tools(message: str) -> str:
    """Execute matching local tools directly."""
    msg = message.lower().strip()

    # System Metrics
    if any(k in msg for k in ["system info", "cpu usage", "ram usage", "memory", "disk space"]):
        return AVAILABLE_TOOLS["get_system_info"]()

    # Time & Date
    if any(k in msg for k in ["what time", "current time", "what date", "today"]):
        return f"Current Time & Date: {AVAILABLE_TOOLS['get_current_time']()}"

    # Launch Apps
    app_match = re.search(r'(?:open|launch|start)\s+(notepad|calculator|explorer|code|chrome|edge)', msg)
    if app_match:
        return AVAILABLE_TOOLS["open_application"](app_match.group(1))

    # Clipboard
    if any(k in msg for k in ["read clipboard", "clipboard content", "paste"]):
        return f"Clipboard: {AVAILABLE_TOOLS['read_clipboard_text']()}"

    # Calculator
    calc_match = re.search(r'(?:calculate|compute|what is)\s+([0-9\.\s\+\-\*\/\(\)]+)', msg)
    if calc_match:
        expr = calc_match.group(1).strip()
        if any(op in expr for op in ["+", "-", "*", "/"]):
            return f"Result: {AVAILABLE_TOOLS['calculator'](expr)}"

    return ""


# =============================================================================
# MULTI-AGENT NODES WITH GENERAL INTELLIGENCE
# =============================================================================

def meta_planner_node(state: GeneralIntelligenceState) -> dict:
    """Meta-planning node: analyzes task and generates reasoning plan."""
    user_msg = state.get("user_message", "")

    # Generate reasoning metadata
    complexity = ReasoningEngine.analyze_complexity(user_msg)
    domain = ReasoningEngine.identify_domain(user_msg)
    reasoning_chain = ReasoningEngine.generate_reasoning_chain(user_msg, domain, complexity)

    # Check for direct tool execution
    tool_output = execute_direct_tools(user_msg)

    # Determine intent/routing
    msg_lower = user_msg.lower()
    if tool_output:
        intent = "direct_execution"
    elif any(k in msg_lower for k in ["heal code", "self heal", "fix code", "run sandbox", "debug code", "traceback"]) or (domain == "technical" and "```" in user_msg):
        intent = "self_healing_code"
    elif domain == "graph" or any(k in msg_lower for k in ["knowledge graph", "subgraph", "precedent chain", "overruled precedent"]):
        intent = "graph_reasoning"
    elif domain == "ambient" or any(k in msg_lower for k in ["active window", "screen anomaly", "prefetch context"]):
        intent = "ambient_context"
    elif domain == "legal" or any(k in msg_lower for k in ["clause", "contract", "statute", "redline", "playbook", "brief", "legal"]):
        intent = "legal_research"
    elif any(k in msg_lower for k in ["search", "latest", "news", "web", "online"]):
        intent = "web_research"
    elif domain == "mathematical":
        intent = "mathematical_reasoning"
    elif complexity > 0.6:
        intent = "complex_reasoning"
    else:
        intent = "general_reasoning"

    print(f"[Meta-Planner] Domain: {domain} | Complexity: {complexity:.2f} | Intent: {intent}")

    return {
        "intent": intent,
        "domain": domain,
        "complexity_score": complexity,
        "reasoning_chain": reasoning_chain,
        "tool_output": tool_output,
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "planning_complete": True,
            "reasoning_steps": len(reasoning_chain)
        }
    }


def legal_research_agent_node(state: GeneralIntelligenceState, agent) -> dict:
    """Specialized Legal Copilot with playbook triage, zero-hallucination statute verification, and conflict detection."""
    print("[Legal Agent] Analyzing legal query with statutory verification & playbook engine...")
    query = state.get("user_message", "")
    chain = state.get("reasoning_chain", [])

    for step in chain:
        if step.get('step') in ('legal_analysis', 'knowledge_retrieval'):
            step['status'] = 'in_progress'

    # Step A: Deterministic Statute Verification
    statute_verifier = StatuteVerifier()
    statute_matches = statute_verifier.scan_text(query)
    statute_notes = []
    for s_res in statute_matches:
        status_tag = "VALID" if s_res.is_valid else f"FLAGGED ({s_res.status})"
        statute_notes.append(f"• Section {s_res.section} of {s_res.correct_title}: {status_tag}. {s_res.notes}")

    # Step B: Playbook Contract Triage (if contract text or clauses detected)
    triage_summary = ""
    if any(k in query.lower() for k in ["clause", "indemnity", "liability", "confidentiality", "arbitration", "jurisdiction", "termination", "agreement", "party"]):
        try:
            triager = ClauseTriager()
            triage_report = triager.triage_contract(query)
            if triage_report.clauses:
                triage_summary = (
                    f"\n\n[Playbook Clause Triage]:\n"
                    f"{triage_report.executive_summary}\n"
                    f"Risk Rating: {triage_report.risk_level} ({triage_report.overall_risk_score}/100) | "
                    f"Red: {triage_report.red_count}, Amber: {triage_report.amber_count}, Green: {triage_report.green_count}"
                )
        except Exception as e:
            print(f"[Legal Agent] Triage warning: {e}")

    # Step C: Precedent Conflict Detection
    conflict_notes = ""
    try:
        conflict_detector = ConflictDetector()
        case_mentions = re.findall(r'([A-Z][a-zA-Z\s\.\&]+v[\.\s]+[A-Z][a-zA-Z\s\.\&]+)', query)
        if case_mentions:
            overruled = conflict_detector.detect_overruled_precedents(case_mentions)
            if overruled:
                conflict_notes = "\n\n[Precedent Alerts]:\n" + "\n".join(
                    f"⚠️ {o['precedent']} is OVERRULED by {o['overruled_by']} ({o['details']})" for o in overruled
                )
    except Exception as e:
        print(f"[Legal Agent] Conflict check warning: {e}")

    # Step D: Vector + Graph Retrieval
    rag_context = search_knowledge_base(query, n_results=4)
    statute_context_str = "\n".join(statute_notes) if statute_notes else "No specific statutory citation scan matches."

    enriched_context = (
        f"Context from Knowledge Base:\n{rag_context}\n\n"
        f"Statutory Audit:\n{statute_context_str}"
        f"{triage_summary}"
        f"{conflict_notes}"
    )

    if DSPY_AVAILABLE:
        try:
            prediction = dspy_legal_optimizer(
                input_text=query + "\n\nEnriched Context:\n" + enriched_context,
                jurisdiction_context="Indian Legal Framework & Statutes"
            )
            draft = (
                f"Legal Analysis:\n"
                f"• Issues: {prediction.legal_issues}\n"
                f"• Provisions: {prediction.statutory_provisions}\n"
                f"• Summary: {prediction.audited_summary}\n\n"
                f"{statute_context_str}{triage_summary}{conflict_notes}"
            )
            confidence = 0.90
        except Exception as e:
            print(f"[Legal Agent] DSPy fallback: {e}")
            prompt = f"Analyze this legal query using the verified legal context below:\n\n{enriched_context}\n\nQuery: {query}"
            draft = agent.chat(prompt)
            confidence = 0.80
    else:
        prompt = f"Analyze this legal query using the verified legal context below:\n\n{enriched_context}\n\nQuery: {query}"
        draft = agent.chat(prompt)
        confidence = 0.80

    for step in chain:
        if step.get('step') == 'legal_analysis':
            step['status'] = 'complete'

    return {
        "rag_context": draft,
        "confidence_score": confidence,
        "reasoning_chain": chain
    }


def self_healing_code_agent_node(state: GeneralIntelligenceState, agent) -> dict:
    """Self-healing sandbox code specialist with AST safety bounds and iterative repair."""
    print("[Self-Healing Code Agent] Executing sandbox healing workflow...")
    query = state.get("user_message", "")
    chain = state.get("reasoning_chain", [])

    # Extract code snippet if present
    code_match = re.search(r'```(?:python)?\s*([\s\S]*?)```', query)
    code_to_heal = code_match.group(1).strip() if code_match else ""

    if code_to_heal:
        healing_agent = SelfHealingAgent()
        heal_res = healing_agent.heal(code_to_heal, goal=query)
        if heal_res.success:
            draft = (
                f"✅ Code Execution & Self-Healing Succeeded (Iterations: {heal_res.iterations_count})!\n\n"
                f"**Summary:** {heal_res.summary}\n\n"
                f"**Fixed Code:**\n```python\n{heal_res.final_code}\n```"
            )
            if heal_res.diff_preview:
                draft += f"\n\n**Unified Diff:**\n```diff\n{heal_res.diff_preview}\n```"
            confidence = 0.95
        else:
            draft = (
                f"⚠️ Self-Healing Completed with Unresolved Error:\n"
                f"**Summary:** {heal_res.summary}\n\n"
                f"**Current Code:**\n```python\n{heal_res.final_code}\n```\n\n"
                f"**Execution Error:** {heal_res.final_execution.error if heal_res.final_execution else 'Unknown'}"
            )
            confidence = 0.70
    else:
        prompt = (
            f"You are the SweetyAI Technical & Code Copilot. Analyze, write, or debug this code request safely:\n\n"
            f"{query}\n\n"
            f"Provide clean, production-grade, secure code with explanations."
        )
        draft = agent.chat(prompt)
        confidence = 0.80

    return {
        "draft_response": draft,
        "confidence_score": confidence,
        "reasoning_chain": chain
    }


def graph_reasoning_agent_node(state: GeneralIntelligenceState, agent) -> dict:
    """Graph reasoning specialist using Reciprocal Rank Fusion over subgraphs and vector chunks."""
    print("[Graph Reasoning Agent] Traversing knowledge graph & computing hybrid RRF context...")
    query = state.get("user_message", "")
    chain = state.get("reasoning_chain", [])

    retriever = HybridRetriever()
    hybrid_res = retriever.retrieve(query, n_results=4, include_graph_subgraph=True)

    items_text = []
    for item in hybrid_res.get("items", []):
        items_text.append(f"[{item['type'].upper()}] {item['content']} (RRF: {item['rrf_score']:.4f})")

    graph_context = "\n".join(items_text) if items_text else "No relevant graph connections found."
    prompt = (
        f"You are SweetyAI's Deep Knowledge Graph engine. Synthesize an answer cross-referencing relationships, "
        f"statutes, and precedents from the graph below:\n\n"
        f"Graph & Semantic Context:\n{graph_context}\n\n"
        f"User Query: {query}"
    )
    draft = agent.chat(prompt)

    return {
        "rag_context": draft,
        "confidence_score": 0.85,
        "reasoning_chain": chain
    }


def ambient_context_agent_node(state: GeneralIntelligenceState, agent) -> dict:
    """Ambient intelligence agent detecting screen anomalies and staging proactive suggestions."""
    print("[Ambient Intelligence Agent] Analyzing active screen context & pre-fetching...")
    query = state.get("user_message", "")
    chain = state.get("reasoning_chain", [])

    prefetcher = ContextPrefetcher()
    detector = AnomalyDetector()

    staged = prefetcher.stage_from_context(query)
    anomalies = detector.detect_anomalies(query)

    anomaly_text = "\n".join(f"• [{a.severity}] {a.title}: {a.description}" for a in anomalies) if anomalies else "No screen anomalies detected."
    staged_text = "\n".join(f"• [{c.type}] {c.title}: {c.summary}" for c in staged.cards) if staged.cards else "No proactive cards staged."

    prompt = (
        f"You are SweetyAI's Ambient Screen Copilot. Address the active context, anomalies, and suggestions:\n\n"
        f"Active Context / OCR Text: {query}\n\n"
        f"Detected Anomalies:\n{anomaly_text}\n\n"
        f"Staged Intelligence:\n{staged_text}\n\n"
        f"Provide a proactive, helpful assistance response."
    )
    draft = agent.chat(prompt)

    return {
        "draft_response": draft,
        "confidence_score": 0.85,
        "reasoning_chain": chain
    }


def web_research_agent_node(state: GeneralIntelligenceState, agent) -> dict:
    """Web research specialist for current information."""
    print("[Web Agent] Searching web...")
    query = state.get("user_message", "")

    search_fn = AVAILABLE_TOOLS.get("search_searxng") or AVAILABLE_TOOLS.get("web_search")
    if search_fn:
        try:
            web_results = search_fn(query)
        except Exception as e:
            web_results = f"Search error: {e}"
    else:
        web_results = "Web search not available"

    prompt = f"Summarize these web findings:\n\n{web_results}\n\nQuery: {query}"
    draft = agent.chat(prompt)

    return {
        "web_context": web_results,
        "draft_response": draft,
        "confidence_score": 0.75
    }


def mathematical_reasoning_agent_node(state: GeneralIntelligenceState, agent) -> dict:
    """Mathematical reasoning specialist with step-by-step solving."""
    print("[Math Agent] Solving mathematical problem...")
    query = state.get("user_message", "")

    # Try calculator for simple expressions
    tool_result = state.get("tool_output", "")

    prompt = (
        f"Solve this mathematical problem step by step:\n\n"
        f"{query}\n\n"
        f"Show your work and explain each step clearly."
    )

    if tool_result:
        prompt += f"\n\nCalculation result: {tool_result}"

    draft = agent.chat(prompt)

    return {
        "draft_response": draft,
        "confidence_score": 0.9
    }


def complex_reasoning_agent_node(state: GeneralIntelligenceState, agent) -> dict:
    """Advanced reasoning for complex multi-step problems."""
    print("[Complex Reasoning Agent] Analyzing complex problem...")
    query = state.get("user_message", "")
    history = get_recent_history(limit=3)
    domain = state.get("domain", "general")

    # Retrieve similar successful patterns
    similar_patterns = learning_engine.get_similar_patterns(query, domain)
    pattern_context = ""
    if similar_patterns:
        pattern_context = "\n\n[Past successful approaches for similar queries]:\n"
        for i, p in enumerate(similar_patterns, 1):
            pattern_context += f"{i}. Complexity: {p['complexity']:.2f}, Confidence: {p['confidence']:.2f}\n"

    prompt = (
        f"You are SweetyAI, an advanced general intelligence system. "
        f"Solve this complex problem using systematic reasoning:\n\n"
        f"Domain: {domain}\n"
        f"Query: {query}\n"
    )

    if history:
        prompt += f"\n\nConversation History:\n{history}"

    if pattern_context:
        prompt += pattern_context

    prompt += "\n\nThink step by step and provide a comprehensive answer."

    draft = agent.chat(prompt)

    return {
        "draft_response": draft,
        "learned_patterns": similar_patterns,
        "confidence_score": 0.8
    }


def general_reasoning_agent_node(state: GeneralIntelligenceState, agent) -> dict:
    """General conversation and reasoning agent."""
    user_msg = state.get("user_message", "")
    tool_out = state.get("tool_output", "")
    rag_ctx = state.get("rag_context", "")
    history = get_recent_history(limit=2)

    if tool_out and not rag_ctx and not history:
        # Direct tool result
        draft = tool_out
        confidence = 1.0
    elif not tool_out and not rag_ctx and not history:
        # Simple chat
        draft = agent.chat(user_msg)
        confidence = 0.7
    else:
        # Integrated response
        prompt_parts = []
        if history:
            prompt_parts.append(f"History:\n{history}")
        if tool_out:
            prompt_parts.append(f"Tool Result:\n{tool_out}")
        if rag_ctx:
            prompt_parts.append(f"Context:\n{rag_ctx}")
        prompt_parts.append(f"User: {user_msg}")

        draft = agent.chat("\n\n".join(prompt_parts))
        confidence = 0.75

    return {
        "draft_response": draft,
        "confidence_score": confidence
    }


def meta_evaluator_node(state: GeneralIntelligenceState, agent) -> dict:
    """Final evaluation, learning, and response synthesis."""
    print("[Meta-Evaluator] Synthesizing final response...")

    user_msg = state.get("user_message", "")
    raw_response = (
        state.get("draft_response") or
        state.get("rag_context") or
        state.get("web_context") or
        state.get("tool_output") or
        ""
    )

    # Clean response
    final = clean_response_text(raw_response)

    # Save to chat history
    try:
        add_message("user", user_msg)
        add_message("assistant", final)
    except Exception as e:
        print(f"[Meta-Evaluator] History save warning: {e}")

    # Learn from this interaction
    learning_engine.learn_from_interaction(state)

    # Compile metadata
    metadata = state.get("metadata", {})
    metadata.update({
        "domain": state.get("domain"),
        "complexity": state.get("complexity_score"),
        "confidence": state.get("confidence_score", 0.7),
        "reasoning_steps": len(state.get("reasoning_chain", [])),
        "timestamp": datetime.now().isoformat()
    })

    return {
        "final_response": final,
        "metadata": metadata
    }


def build_general_intelligence_graph(agent):
    """Compile the general intelligence multi-agent orchestration graph."""
    workflow = StateGraph(GeneralIntelligenceState)

    # Add nodes
    workflow.add_node("meta_planner", meta_planner_node)
    workflow.add_node("legal_agent", lambda s: legal_research_agent_node(s, agent))
    workflow.add_node("code_healing_agent", lambda s: self_healing_code_agent_node(s, agent))
    workflow.add_node("graph_agent", lambda s: graph_reasoning_agent_node(s, agent))
    workflow.add_node("ambient_agent", lambda s: ambient_context_agent_node(s, agent))
    workflow.add_node("web_agent", lambda s: web_research_agent_node(s, agent))
    workflow.add_node("math_agent", lambda s: mathematical_reasoning_agent_node(s, agent))
    workflow.add_node("complex_agent", lambda s: complex_reasoning_agent_node(s, agent))
    workflow.add_node("general_agent", lambda s: general_reasoning_agent_node(s, agent))
    workflow.add_node("meta_evaluator", lambda s: meta_evaluator_node(s, agent))

    # Start with meta-planner
    workflow.add_edge(START, "meta_planner")

    # Conditional routing based on intent
    workflow.add_conditional_edges(
        "meta_planner",
        lambda state: state["intent"],
        {
            "direct_execution": "general_agent",
            "legal_research": "legal_agent",
            "self_healing_code": "code_healing_agent",
            "graph_reasoning": "graph_agent",
            "ambient_context": "ambient_agent",
            "web_research": "web_agent",
            "mathematical_reasoning": "math_agent",
            "complex_reasoning": "complex_agent",
            "general_reasoning": "general_agent"
        }
    )

    # All agents flow to meta-evaluator
    workflow.add_edge("legal_agent", "meta_evaluator")
    workflow.add_edge("code_healing_agent", "meta_evaluator")
    workflow.add_edge("graph_agent", "meta_evaluator")
    workflow.add_edge("ambient_agent", "meta_evaluator")
    workflow.add_edge("web_agent", "meta_evaluator")
    workflow.add_edge("math_agent", "meta_evaluator")
    workflow.add_edge("complex_agent", "meta_evaluator")
    workflow.add_edge("general_agent", "meta_evaluator")
    workflow.add_edge("meta_evaluator", END)

    print("[Orchestrator V2] General Intelligence Graph compiled successfully!")
    return workflow.compile()
