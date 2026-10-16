"""
Knowledge Graph subsystem for SweetyAI.
Provides dual-mode graph database access (Neo4j with in-memory LocalSemanticGraph fallback),
conflict detection, and hybrid retrieval.
"""

from app.graph.local_graph import LocalSemanticGraph, Node, Edge
from app.graph.knowledge_graph import KnowledgeGraph, get_knowledge_graph
from app.graph.conflict_detector import ConflictDetector
from app.graph.hybrid_retriever import HybridRetriever

__all__ = [
    "LocalSemanticGraph",
    "Node",
    "Edge",
    "KnowledgeGraph",
    "get_knowledge_graph",
    "ConflictDetector",
    "HybridRetriever",
]
