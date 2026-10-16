from app.tools.general_utils import list_directory, run_system_command
from app.tools.file_downloader import download_documents_from_url
from app.tools.web_downloader import download_legal_docs
from app.tools.statute_mapper import map_statute
import json
import os

from app.memory.memory import Memory
from app.agent.tool_registry import ToolRegistry

from app.tools.calculator import calculator
from app.tools.filesystem import list_files, read_file
from app.tools.web_search import web_search
from app.tools.webpage import read_webpage
from app.tools.write_file import write_file
from app.tools.search_project import search_project
from app.tools.desktop_automation import open_application, get_system_info
from app.tools.clipboard import read_clipboard_text, write_clipboard_text
from app.tools import (
    get_current_time,
    open_workspace_folder,
    list_knowledge_documents,
    search_local_files,
)
from app.doc_generator import generate_legal_document
from app.graph.knowledge_graph import get_knowledge_graph
from app.sandbox.self_healing_agent import SelfHealingAgent
from app.legal.clause_triager import ClauseTriager
from app.legal.statute_verifier import StatuteVerifier
from app.adaptive.dry_run_patcher import DryRunPatcher
from app.background.case_watcher import CaseWatcher

def search_legal_database(query: str, node_type=None, **kwargs) -> str:
    """
    Searches local legal statutes, case laws, and KSLU curriculum notes
    for precise legal rules, articles, and administrative provisions.
    """
    db_path = "legal_database.json"
    if not os.path.exists(db_path):
        sample_legal_data = {
            "administrative law": "Administrative law governs the activities of administrative agencies of government, including rule making, adjudication, and the enforcement of laws.",
            "competition law": "Competition law promotes or seeks to maintain market competition by regulating anti-competitive conduct by companies.",
            "constitutional law": "Constitutional law deals with the fundamental principles by which the government exercises its authority."
        }
        with open(db_path, "w") as f:
            json.dump(sample_legal_data, f, indent=2)

    with open(db_path, "r") as f:
        data = json.load(f)

    query_lower = query.lower()
    results = [f"[{k.upper()}]: {v}" for k, v in data.items() if k in query_lower or query_lower in k]

    if not results:
        return f"No direct statutory match found for '{query}'. Falling back to vector RAG memory."
    return "\n".join(results)


def query_knowledge_graph_tool(query: str, node_type: str = "") -> str:
    """Queries the Knowledge Graph for entity relationships, precedents, and statutes."""
    kg = get_knowledge_graph()
    results = kg.search(query, node_type=node_type if node_type else None)
    if not results:
        return f"No entities found in Knowledge Graph matching '{query}'."
    summaries = []
    for r in results[:4]:
        subgraph = kg.query_context_subgraph(r["id"], max_depth=1)
        edge_count = len(subgraph.get("edges", []))
        summaries.append(f"[{r['type']}]: {r['id']} (Connected edges: {edge_count}) - Properties: {r.get('properties', {})}")
    return "\n".join(summaries)


def self_heal_code_tool(code: str, goal: str = "Fix failing execution") -> str:
    """Executes code in isolated sandbox and iteratively self-heals any errors."""
    agent = SelfHealingAgent()
    res = agent.heal(code, goal=goal)
    if res.success:
        return f"Healing Succeeded in {res.iterations_count} iteration(s)!\nSummary: {res.summary}\nFinal Code:\n```python\n{res.final_code}\n```"
    return f"Healing Failed: {res.summary}\nLast Error: {res.final_execution.error if res.final_execution else 'Unknown'}"


def triage_contract_tool(contract_text: str) -> str:
    """Evaluates contract clauses against playbook rules, returning Red/Amber/Green risk triage."""
    triager = ClauseTriager()
    report = triager.triage_contract(contract_text)
    return report.executive_summary + f"\nRisk Score: {report.overall_risk_score}/100 ({report.risk_level})\nRed: {report.red_count}, Amber: {report.amber_count}, Green: {report.green_count}"


def verify_statute_citation_tool(section: str, act_name: str) -> str:
    """Zero-hallucination deterministic verification of statutory section and Act title."""
    verifier = StatuteVerifier()
    res = verifier.verify_citation(section, act_name)
    status_msg = "VALID & ACTIVE" if res.is_valid else f"INVALID/REPEALED ({res.status})"
    return f"Citation: Section {section} of {act_name}\nStatus: {status_msg}\nCanonical: {res.correct_title}\nNotes: {res.notes}"


def preview_file_patch_tool(filepath: str, new_content: str) -> str:
    """Generates a dry-run diff preview before writing files to disk."""
    patcher = DryRunPatcher()
    preview = patcher.preview_patch(filepath, new_content)
    return f"Dry-Run Diff for {filepath} ({preview.lines_changed} lines changed):\n{preview.diff.unified_diff}"


def create_tool_registry():
    registry = ToolRegistry()
    memory = Memory()

    # Calculator
    registry.register(
        name="calculator",
        description="Calculate a mathematical expression.",
        function=calculator,
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression, for example 25 * 100",
                }
            },
            "required": ["expression"],
        },
    )

    # List files
    registry.register(
        name="list_files",
        description="List files and directories inside the SweetyAI project.",
        function=list_files,
        parameters={
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Project-relative directory, for example '.' or 'app'",
                }
            },
            "required": [],
        },
    )

    # Read file
    registry.register(
        name="read_file",
        description="Read a text file inside the SweetyAI project.",
        function=read_file,
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Project-relative file path, for example 'app/main.py'",
                }
            },
            "required": ["path"],
        },
    )

    # Web search
    registry.register(
        name="web_search",
        description="Search the internet for current information. Use this when the user asks about recent, current, or online information.",
        function=web_search,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The web search query.",
                }
            },
            "required": ["query"],
        },
    )

    # Read webpage
    registry.register(
        name="read_webpage",
        description="Open and read the actual contents of a webpage.",
        function=read_webpage,
        parameters={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The complete URL of the webpage to read.",
                }
            },
            "required": ["url"],
        },
    )

    # Save memory
    registry.register(
        name="save_memory",
        description="Save an important fact about the user for future conversations.",
        function=memory.add,
        parameters={
            "type": "object",
            "properties": {
                "memory": {
                    "type": "string",
                    "description": "A concise fact worth remembering about the user.",
                }
            },
            "required": ["memory"],
        },
    )

    # Delete memory
    registry.register(
        name="delete_memory",
        description="Delete a specific saved memory when the user explicitly asks you to forget it.",
        function=memory.delete,
        parameters={
            "type": "object",
            "properties": {
                "memory": {
                    "type": "string",
                    "description": "The exact saved memory to delete.",
                }
            },
            "required": ["memory"],
        },
    )

    # Write file
    registry.register(
        name="write_file",
        description="Create, write, save, or modify a file inside the SweetyAI project.",
        function=write_file,
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Project-relative file path, for example 'tests/example.py'",
                },
                "content": {
                    "type": "string",
                    "description": "The complete text content to write into the file.",
                },
            },
            "required": ["path", "content"],
        },
    )

    # Search project
    registry.register(
        name="search_project",
        description="Search the SweetyAI project source files.",
        function=search_project,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Class name, function name, module name, text, or other code to search for.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["text", "definition", "usage", "import", "registration"],
                    "description": "Search mode.",
                },
            },
            "required": ["query"],
        },
    )

    # Legal Database Search Tool
    registry.register(
        name="search_legal_database",
        description="Search local legal statutes, case laws, and KSLU study notes for precise legal rules.",
        function=search_legal_database,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The legal topic, act, or concept to search for.",
                }
            },
            "required": ["query"],
        },
    )

    # Desktop Automation: Open Application
    registry.register(
        name="open_application",
        description="Launch an authorized desktop application (e.g., notepad, calc, explorer, vscode, cmd, powershell).",
        function=open_application,
        parameters={
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Name or executable alias of the desktop app to launch.",
                }
            },
            "required": ["app_name"],
        },
    )

    # Desktop Automation: System Info & Metrics
    registry.register(
        name="get_system_info",
        description="Retrieve real-time operating system metrics including CPU usage, RAM utilization, and disk space.",
        function=get_system_info,
        parameters={"type": "object", "properties": {}, "required": []},
    )

    # Clipboard Read
    registry.register(
        name="read_clipboard_text",
        description="Read current plain text from the system clipboard.",
        function=read_clipboard_text,
        parameters={"type": "object", "properties": {}, "required": []},
    )

    # Clipboard Write
    registry.register(
        name="write_clipboard_text",
        description="Copy text to the system clipboard.",
        function=write_clipboard_text,
        parameters={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The text content to copy to the clipboard.",
                }
            },
            "required": ["content"],
        },
    )

    # Current Time
    registry.register(
        name="get_current_time",
        description="Get current system date and time.",
        function=get_current_time,
        parameters={"type": "object", "properties": {}, "required": []},
    )

    # Workspace Folder
    registry.register(
        name="open_workspace_folder",
        description="Open the project workspace directory in the OS file explorer.",
        function=open_workspace_folder,
        parameters={"type": "object", "properties": {}, "required": []},
    )

    # Knowledge Documents Listing
    registry.register(
        name="list_knowledge_documents",
        description="List all available documents in the SweetyAI knowledge base.",
        function=list_knowledge_documents,
        parameters={"type": "object", "properties": {}, "required": []},
    )

    # Search Local Files
    registry.register(
        name="search_local_files",
        description="Search for filenames matching a pattern in the local project workspace.",
        function=search_local_files,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Filename search pattern or extension.",
                }
            },
            "required": ["query"],
        },
    )

    # Generate Legal Document
    registry.register(
        name="generate_legal_document",
        description="Generate formatted legal documents, notices, or contracts.",
        function=generate_legal_document,
        parameters={
            "type": "object",
            "properties": {
                "doc_type": {
                    "type": "string",
                    "description": "Type of legal document (e.g. 'legal_notice', 'nda', 'contract').",
                },
                "details": {
                    "type": "object",
                    "description": "Key-value details for document template variables.",
                }
            },
            "required": ["doc_type", "details"],
        },
    )

    # Knowledge Graph Query
    registry.register(
        name="query_knowledge_graph",
        description="Search entities, precedents, statutes, and relationship subgraphs in the Knowledge Graph.",
        function=query_knowledge_graph_tool,
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Entity name, statute section, or case keyword."},
                "node_type": {"type": "string", "description": "Optional node type filter (e.g. 'Statute', 'Precedent', 'ContractClause')."},
            },
            "required": ["query"],
        },
    )

    # Self-Healing Code Execution
    registry.register(
        name="self_heal_code",
        description="Execute Python code in isolated sandbox and iteratively auto-repair syntax and runtime errors.",
        function=self_heal_code_tool,
        parameters={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code snippet to execute and heal."},
                "goal": {"type": "string", "description": "The objective or intended behavior of the code."},
            },
            "required": ["code"],
        },
    )

    # Legal Playbook Contract Triage
    registry.register(
        name="triage_contract_clauses",
        description="Analyze contract clauses against enterprise legal playbook rules, rating risks as Red, Amber, or Green.",
        function=triage_contract_tool,
        parameters={
            "type": "object",
            "properties": {
                "contract_text": {"type": "string", "description": "Full contract text or clause to triage."},
            },
            "required": ["contract_text"],
        },
    )

    # Zero-Hallucination Statutory Citation Verifier
    registry.register(
        name="verify_statute_citation",
        description="Verify whether a legal section number and Act title are valid, active, repealed, or amended.",
        function=verify_statute_citation_tool,
        parameters={
            "type": "object",
            "properties": {
                "section": {"type": "string", "description": "Section number (e.g. '73', '34', '420')."},
                "act_name": {"type": "string", "description": "Statute name (e.g. 'Indian Contract Act', 'Arbitration Act')."},
            },
            "required": ["section", "act_name"],
        },
    )

    # Dry-Run Diff Preview
    registry.register(
        name="preview_file_patch",
        description="Generate a unified dry-run diff preview for file changes before applying writes to disk.",
        function=preview_file_patch_tool,
        parameters={
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Target workspace file path."},
                "new_content": {"type": "string", "description": "New updated file content."},
            },
            "required": ["filepath", "new_content"],
        },
    )

    return registry
