from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class Node:
    id: str
    type: str  # Statute, Precedent, ContractClause, ProjectFile, Concept, Note, Entity
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "properties": self.properties,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Node:
        return cls(
            id=data["id"],
            type=data.get("type", "Entity"),
            properties=data.get("properties", {}),
        )


@dataclass
class Edge:
    source: str
    target: str
    type: str  # CITES, OVERRULES, AMENDS, CONFLICTS_WITH, DEPENDS_ON, CONTAINS, RELATED_TO
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "properties": self.properties,
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Edge:
        return cls(
            source=data["source"],
            target=data["target"],
            type=data.get("type", "RELATED_TO"),
            properties=data.get("properties", {}),
            weight=float(data.get("weight", 1.0)),
        )


class LocalSemanticGraph:
    """
    In-memory semantic graph engine with adjacency list indexing,
    subgraph traversal, multi-hop path search, cycle detection,
    and atomic JSON persistence.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "semantic_graph.json"
        )
        self._nodes: Dict[str, Node] = {}
        self._out_edges: Dict[str, List[Edge]] = {}
        self._in_edges: Dict[str, List[Edge]] = {}
        self._type_index: Dict[str, Set[str]] = {}
        self._lock = threading.RLock()

        # Load existing graph if file exists
        if os.path.exists(self.storage_path):
            self.load_from_json(self.storage_path)

    def add_node(self, id: str, type: str, properties: Optional[Dict[str, Any]] = None) -> Node:
        with self._lock:
            node = Node(id=str(id), type=type, properties=properties or {})
            self._nodes[node.id] = node
            if node.id not in self._out_edges:
                self._out_edges[node.id] = []
            if node.id not in self._in_edges:
                self._in_edges[node.id] = []
            if type not in self._type_index:
                self._type_index[type] = set()
            self._type_index[type].add(node.id)
            return node

    def add_edge(
        self,
        source: str,
        target: str,
        type: str,
        properties: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
    ) -> Edge:
        with self._lock:
            # Ensure endpoints exist
            if source not in self._nodes:
                self.add_node(source, "Entity")
            if target not in self._nodes:
                self.add_node(target, "Entity")

            edge = Edge(
                source=str(source),
                target=str(target),
                type=type,
                properties=properties or {},
                weight=float(weight),
            )
            # Avoid duplicate edges
            existing_out = [
                e for e in self._out_edges[source] if e.target == target and e.type == type
            ]
            if existing_out:
                existing_out[0].properties.update(edge.properties)
                existing_out[0].weight = edge.weight
                return existing_out[0]

            self._out_edges[source].append(edge)
            self._in_edges[target].append(edge)
            return edge

    def get_node(self, id: str) -> Optional[Node]:
        with self._lock:
            return self._nodes.get(str(id))

    def get_nodes_by_type(self, node_type: str) -> List[Node]:
        with self._lock:
            ids = self._type_index.get(node_type, set())
            return [self._nodes[nid] for nid in ids if nid in self._nodes]

    def get_edges(
        self,
        source: Optional[str] = None,
        target: Optional[str] = None,
        edge_type: Optional[str] = None,
    ) -> List[Edge]:
        with self._lock:
            results: List[Edge] = []
            if source is not None:
                candidates = self._out_edges.get(source, [])
                for e in candidates:
                    if (target is None or e.target == target) and (
                        edge_type is None or e.type == edge_type
                    ):
                        results.append(e)
            elif target is not None:
                candidates = self._in_edges.get(target, [])
                for e in candidates:
                    if edge_type is None or e.type == edge_type:
                        results.append(e)
            else:
                for edges in self._out_edges.values():
                    for e in edges:
                        if edge_type is None or e.type == edge_type:
                            results.append(e)
            return results

    def get_neighbors(
        self,
        node_id: str,
        direction: str = "both",  # 'out', 'in', 'both'
        edge_type: Optional[str] = None,
    ) -> List[Tuple[Node, Edge]]:
        with self._lock:
            neighbors: List[Tuple[Node, Edge]] = []
            if direction in ("out", "both"):
                for e in self._out_edges.get(node_id, []):
                    if edge_type is None or e.type == edge_type:
                        target_node = self._nodes.get(e.target)
                        if target_node:
                            neighbors.append((target_node, e))
            if direction in ("in", "both"):
                for e in self._in_edges.get(node_id, []):
                    if edge_type is None or e.type == edge_type:
                        src_node = self._nodes.get(e.source)
                        if src_node:
                            neighbors.append((src_node, e))
            return neighbors

    def traverse_subgraph(
        self,
        start_node_id: str,
        max_depth: int = 2,
        edge_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        BFS 2-hop or N-hop traversal from start_node_id.
        Returns visited nodes and connecting edges.
        """
        with self._lock:
            if start_node_id not in self._nodes:
                return {"nodes": [], "edges": [], "depth_reached": 0}

            visited_nodes: Set[str] = {start_node_id}
            collected_edges: List[Edge] = []
            queue: List[Tuple[str, int]] = [(start_node_id, 0)]
            max_reached = 0

            while queue:
                current_id, depth = queue.pop(0)
                max_reached = max(max_reached, depth)
                if depth >= max_depth:
                    continue

                for e in self._out_edges.get(current_id, []):
                    if edge_types is None or e.type in edge_types:
                        collected_edges.append(e)
                        if e.target not in visited_nodes:
                            visited_nodes.add(e.target)
                            queue.append((e.target, depth + 1))

                for e in self._in_edges.get(current_id, []):
                    if edge_types is None or e.type in edge_types:
                        if e not in collected_edges:
                            collected_edges.append(e)
                        if e.source not in visited_nodes:
                            visited_nodes.add(e.source)
                            queue.append((e.source, depth + 1))

            nodes = [self._nodes[nid].to_dict() for nid in visited_nodes if nid in self._nodes]
            edges = [e.to_dict() for e in collected_edges]
            return {
                "start_node": start_node_id,
                "nodes": nodes,
                "edges": edges,
                "depth_reached": max_reached,
                "total_nodes": len(nodes),
                "total_edges": len(edges),
            }

    def find_paths(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 4,
    ) -> List[List[str]]:
        """Finds all simple paths between start_id and end_id up to max_depth."""
        with self._lock:
            if start_id not in self._nodes or end_id not in self._nodes:
                return []

            paths: List[List[str]] = []
            stack: List[Tuple[str, List[str]]] = [(start_id, [start_id])]

            while stack:
                current, path = stack.pop()
                if current == end_id and len(path) > 1:
                    paths.append(path)
                    continue

                if len(path) > max_depth:
                    continue

                for e in self._out_edges.get(current, []):
                    if e.target not in path:
                        stack.append((e.target, path + [e.target]))

            return paths

    def search_nodes(self, query: str, node_type: Optional[str] = None) -> List[Node]:
        """Keyword and substring search across node ids, types, and properties."""
        with self._lock:
            query_lower = query.lower()
            results: List[Node] = []
            candidate_ids = self._type_index.get(node_type, set()) if node_type else set(self._nodes.keys())

            for nid in candidate_ids:
                node = self._nodes.get(nid)
                if not node:
                    continue
                # Match in id or properties
                if query_lower in node.id.lower():
                    results.append(node)
                    continue
                for val in node.properties.values():
                    if query_lower in str(val).lower():
                        results.append(node)
                        break
            return results

    def find_cycles(self, edge_types: Optional[List[str]] = None) -> List[List[str]]:
        """Tarjan's algorithm / DFS cycle finder to detect circular relationships."""
        with self._lock:
            visited: Set[str] = set()
            recursion_stack: Set[str] = set()
            cycles: List[List[str]] = []
            current_path: List[str] = []

            def dfs(u: str):
                visited.add(u)
                recursion_stack.add(u)
                current_path.append(u)

                for edge in self._out_edges.get(u, []):
                    if edge_types is not None and edge.type not in edge_types:
                        continue
                    v = edge.target
                    if v not in visited:
                        dfs(v)
                    elif v in recursion_stack:
                        # Cycle detected
                        cycle_start_idx = current_path.index(v)
                        cycles.append(current_path[cycle_start_idx:] + [v])

                recursion_stack.remove(u)
                current_path.pop()

            for node_id in list(self._nodes.keys()):
                if node_id not in visited:
                    dfs(node_id)

            return cycles

    def save_to_json(self, filepath: Optional[str] = None) -> bool:
        with self._lock:
            target_path = filepath or self.storage_path
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            data = {
                "nodes": [n.to_dict() for n in self._nodes.values()],
                "edges": [
                    e.to_dict()
                    for edges in self._out_edges.values()
                    for e in edges
                ],
            }
            temp_path = f"{target_path}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if os.path.exists(target_path):
                os.remove(target_path)
            os.rename(temp_path, target_path)
            return True

    def load_from_json(self, filepath: Optional[str] = None) -> bool:
        with self._lock:
            src_path = filepath or self.storage_path
            if not os.path.exists(src_path):
                return False
            try:
                with open(src_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.clear()
                for n_data in data.get("nodes", []):
                    self.add_node(
                        id=n_data["id"],
                        type=n_data.get("type", "Entity"),
                        properties=n_data.get("properties", {}),
                    )
                for e_data in data.get("edges", []):
                    self.add_edge(
                        source=e_data["source"],
                        target=e_data["target"],
                        type=e_data.get("type", "RELATED_TO"),
                        properties=e_data.get("properties", {}),
                        weight=float(e_data.get("weight", 1.0)),
                    )
                return True
            except Exception as e:
                print(f"[LocalSemanticGraph] Failed to load {src_path}: {e}")
                return False

    def clear(self) -> None:
        with self._lock:
            self._nodes.clear()
            self._out_edges.clear()
            self._in_edges.clear()
            self._type_index.clear()

    def all_nodes(self) -> List[Node]:
        return list(self._nodes.values())

    def all_edges(self) -> List[Edge]:
        all_edges = []
        for edges in self._out_edges.values():
            all_edges.extend(edges)
        return all_edges

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            type_counts = {t: len(nodes) for t, nodes in self._type_index.items()}
            total_edges = sum(len(edges) for edges in self._out_edges.values())
            edge_type_counts: Dict[str, int] = {}
            for edges in self._out_edges.values():
                for e in edges:
                    edge_type_counts[e.type] = edge_type_counts.get(e.type, 0) + 1

            return {
                "total_nodes": len(self._nodes),
                "total_edges": total_edges,
                "node_types": type_counts,
                "edge_types": edge_type_counts,
            }
