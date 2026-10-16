from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from app.graph.local_graph import Edge, LocalSemanticGraph, Node

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """
    Unified Knowledge Graph facade for SweetyAI.
    Provides dual-mode operation:
    - High-performance in-memory LocalSemanticGraph with JSON persistence.
    - Automatic Neo4j synchronization when a live Neo4j instance is configured.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.local_graph = LocalSemanticGraph(storage_path)
        self.neo4j_client = None
        self._init_neo4j()

    def _init_neo4j(self) -> None:
        try:
            from app.tools.database_connectors import Neo4jClient

            neo_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
            neo_user = os.environ.get("NEO4J_USER", "neo4j")
            neo_pass = os.environ.get("NEO4J_PASSWORD", "password")
            client = Neo4jClient(uri=neo_uri, user=neo_user, password=neo_pass)
            if client.driver is not None:
                self.neo4j_client = client
                logger.info("[KnowledgeGraph] Connected to Neo4j successfully.")
            else:
                self.neo4j_client = None
        except Exception as e:
            logger.debug(f"[KnowledgeGraph] Neo4j not available ({e}), using LocalSemanticGraph.")
            self.neo4j_client = None

    @property
    def is_neo4j_active(self) -> bool:
        return self.neo4j_client is not None and self.neo4j_client.driver is not None

    def add_node(
        self,
        node_id: str,
        node_type: str = "Entity",
        properties: Optional[Dict[str, Any]] = None,
    ) -> Node:
        return self.local_graph.add_node(node_id, node_type, properties or {})

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: str = "RELATED_TO",
        properties: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
    ) -> Optional[Edge]:
        return self.link_entities(source, target, edge_type, properties, weight)

    def add_statute(
        self,
        statute_id: str,
        act_name: str,
        section: str,
        text: str = "",
        jurisdiction: str = "India",
        status: str = "active",
        properties: Optional[Dict[str, Any]] = None,
    ) -> Node:
        props = {
            "act_name": act_name,
            "section": section,
            "text": text,
            "jurisdiction": jurisdiction,
            "status": status,
            **(properties or {}),
        }
        node = self.local_graph.add_node(statute_id, "Statute", props)
        if self.is_neo4j_active:
            try:
                cypher = """
                MERGE (s:Statute {id: $id})
                SET s.act_name = $act_name, s.section = $section, s.text = $text,
                    s.jurisdiction = $jurisdiction, s.status = $status
                """
                self.neo4j_client.execute_query(cypher, {"id": statute_id, **props})
            except Exception as e:
                logger.warning(f"[KnowledgeGraph] Neo4j write failed: {e}")
        return node

    def add_precedent(
        self,
        case_id: str,
        title: str,
        citation: str,
        court: str = "Supreme Court of India",
        year: Optional[int] = None,
        ratio: str = "",
        principles: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Node:
        props = {
            "title": title,
            "citation": citation,
            "court": court,
            "year": year,
            "ratio": ratio,
            "principles": principles or [],
            **(properties or {}),
        }
        node = self.local_graph.add_node(case_id, "Precedent", props)
        if self.is_neo4j_active:
            try:
                cypher = """
                MERGE (p:Precedent {id: $id})
                SET p.title = $title, p.citation = $citation, p.court = $court,
                    p.year = $year, p.ratio = $ratio
                """
                self.neo4j_client.execute_query(cypher, {"id": case_id, **props})
            except Exception as e:
                logger.warning(f"[KnowledgeGraph] Neo4j write failed: {e}")
        return node

    def add_clause(
        self,
        clause_id: str,
        title: str,
        category: str,
        text: str,
        risk_tier: str = "AMBER",
        properties: Optional[Dict[str, Any]] = None,
    ) -> Node:
        props = {
            "title": title,
            "category": category,
            "text": text,
            "risk_tier": risk_tier,
            **(properties or {}),
        }
        node = self.local_graph.add_node(clause_id, "ContractClause", props)
        if self.is_neo4j_active:
            try:
                cypher = """
                MERGE (c:ContractClause {id: $id})
                SET c.title = $title, c.category = $category, c.text = $text, c.risk_tier = $risk_tier
                """
                self.neo4j_client.execute_query(cypher, {"id": clause_id, **props})
            except Exception as e:
                logger.warning(f"[KnowledgeGraph] Neo4j write failed: {e}")
        return node

    def add_project_file(
        self,
        file_path: str,
        language: str = "python",
        summary: str = "",
        dependencies: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Node:
        props = {
            "file_path": file_path,
            "language": language,
            "summary": summary,
            "dependencies": dependencies or [],
            **(properties or {}),
        }
        node = self.local_graph.add_node(file_path, "ProjectFile", props)
        for dep in dependencies or []:
            self.local_graph.add_edge(file_path, dep, "DEPENDS_ON")
        return node

    def link_entities(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
    ) -> Edge:
        edge = self.local_graph.add_edge(
            source=source_id,
            target=target_id,
            type=relation_type,
            properties=properties,
            weight=weight,
        )
        if self.is_neo4j_active:
            try:
                cypher = f"""
                MATCH (a {{id: $source}}), (b {{id: $target}})
                MERGE (a)-[r:{relation_type}]->(b)
                SET r += $props
                """
                self.neo4j_client.execute_query(
                    cypher,
                    {"source": source_id, "target": target_id, "props": properties or {}},
                )
            except Exception as e:
                logger.warning(f"[KnowledgeGraph] Neo4j link failed: {e}")
        return edge

    def link_precedent_to_statute(
        self, case_id: str, statute_id: str, details: Optional[str] = None
    ) -> Edge:
        return self.link_entities(case_id, statute_id, "CITES", {"details": details or ""})

    def link_overrules(
        self, overruling_case_id: str, overruled_case_id: str, reason: Optional[str] = None
    ) -> Edge:
        return self.link_entities(
            overruling_case_id, overruled_case_id, "OVERRULES", {"reason": reason or ""}
        )

    def link_clause_conflicts(
        self, clause_id: str, target_id: str, reason: Optional[str] = None
    ) -> Edge:
        return self.link_entities(
            clause_id, target_id, "CONFLICTS_WITH", {"reason": reason or ""}
        )

    def query_context_subgraph(
        self, entity_id: str, max_depth: int = 2, edge_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Returns 2-hop neighborhood of related entities and citations."""
        return self.local_graph.traverse_subgraph(entity_id, max_depth, edge_types)

    def find_precedents_for_statute(self, statute_id: str) -> List[Dict[str, Any]]:
        """Finds all court precedents that cite a specific statute section."""
        edges = self.local_graph.get_edges(target=statute_id, edge_type="CITES")
        precedents = []
        for e in edges:
            node = self.local_graph.get_node(e.source)
            if node and node.type == "Precedent":
                precedents.append({**node.to_dict(), "citation_details": e.properties})
        return precedents

    def find_statutes_for_clause(self, clause_id: str) -> List[Dict[str, Any]]:
        """Finds statutory provisions governed or cited by a contract clause."""
        edges = self.local_graph.get_edges(source=clause_id, edge_type="CITES")
        statutes = []
        for e in edges:
            node = self.local_graph.get_node(e.target)
            if node and node.type == "Statute":
                statutes.append(node.to_dict())
        return statutes

    def search(self, query: str, node_type: Optional[str] = None) -> List[Dict[str, Any]]:
        nodes = self.local_graph.search_nodes(query, node_type)
        return [n.to_dict() for n in nodes]

    def save(self, filepath: Optional[str] = None) -> bool:
        return self.local_graph.save_to_json(filepath)

    def get_stats(self) -> Dict[str, Any]:
        stats = self.local_graph.stats()
        stats["neo4j_active"] = self.is_neo4j_active
        return stats


_GLOBAL_GRAPH: Optional[KnowledgeGraph] = None


def get_knowledge_graph() -> KnowledgeGraph:
    global _GLOBAL_GRAPH
    if _GLOBAL_GRAPH is None:
        _GLOBAL_GRAPH = KnowledgeGraph()
    return _GLOBAL_GRAPH
