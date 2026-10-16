from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.graph.knowledge_graph import KnowledgeGraph, get_knowledge_graph
from rag import search_knowledge_base

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid Retriever integrating Dense Vector Embeddings (ChromaDB)
    with Multi-Hop Graph Subgraphs (KnowledgeGraph) via Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, graph: Optional[KnowledgeGraph] = None, rrf_k: int = 60):
        self.graph = graph or get_knowledge_graph()
        self.rrf_k = rrf_k

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        include_graph_subgraph: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes dual-path retrieval:
        1. Dense Vector search over ChromaDB chunks.
        2. Keyword & semantic search over Knowledge Graph nodes + 2-hop traversals.
        Combines candidates using Reciprocal Rank Fusion.
        """
        # 1. Vector Search
        vector_text = search_knowledge_base(query, n_results=n_results)
        vector_docs = [chunk.strip() for chunk in vector_text.split("\n\n") if chunk.strip()] if vector_text else []

        # 2. Graph Search
        graph_nodes = self.graph.search(query)

        # 3. Reciprocal Rank Fusion
        scores: Dict[str, float] = {}
        item_data: Dict[str, Dict[str, Any]] = {}

        # Score vector results
        for rank, doc in enumerate(vector_docs):
            doc_key = f"vector_{rank}_{doc[:40]}"
            scores[doc_key] = scores.get(doc_key, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            item_data[doc_key] = {
                "source": "vector_store",
                "content": doc,
                "type": "document_chunk",
                "rank_vector": rank + 1,
            }

        # Score graph results
        for rank, node in enumerate(graph_nodes):
            node_key = f"graph_{node['id']}"
            scores[node_key] = scores.get(node_key, 0.0) + (1.0 / (self.rrf_k + rank + 1))

            subgraph = None
            if include_graph_subgraph:
                subgraph = self.graph.query_context_subgraph(node["id"], max_depth=2)

            item_data[node_key] = {
                "source": "knowledge_graph",
                "node_id": node["id"],
                "node_type": node["type"],
                "properties": node.get("properties", {}),
                "subgraph": subgraph,
                "rank_graph": rank + 1,
            }

        # Sort by merged RRF score
        sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[:n_results]
        ranked_results = []
        for k in sorted_keys:
            entry = item_data[k]
            entry["rrf_score"] = round(scores[k], 6)
            ranked_results.append(entry)

        # Formulate consolidated context string for LLM prompts
        context_blocks = []
        for item in ranked_results:
            if item["source"] == "vector_store":
                context_blocks.append(f"[Document Excerpt]:\n{item['content']}")
            elif item["source"] == "knowledge_graph":
                props_str = ", ".join(f"{k}: {v}" for k, v in item["properties"].items() if str(v).strip())
                block = f"[Knowledge Graph - {item['node_type']} ({item['node_id']})]: {props_str}"
                if item.get("subgraph") and item["subgraph"]["edges"]:
                    edge_summaries = [
                        f"{e['source']} -[{e['type']}]-> {e['target']}"
                        for e in item["subgraph"]["edges"][:4]
                    ]
                    block += f"\n  Connected Context: {'; '.join(edge_summaries)}"
                context_blocks.append(block)

        consolidated_context = "\n\n".join(context_blocks)

        return {
            "query": query,
            "results": ranked_results,
            "consolidated_context": consolidated_context,
            "total_candidates": len(ranked_results),
        }
