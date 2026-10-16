from __future__ import annotations

import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.ambient.ambient_monitor import WindowContext
from app.ambient.anomaly_detector import AnomalyDetector
from app.graph.hybrid_retriever import HybridRetriever
from app.legal.statute_verifier import StatuteVerifier

logger = logging.getLogger(__name__)


@dataclass
class StagedContextItem:
    source: str  # "knowledge_graph", "vector_store", "anomaly", "playbook"
    title: str
    summary: str
    relevance_score: float = 0.8
    details: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "summary": self.summary,
            "relevance_score": round(self.relevance_score, 2),
            "details": self.details,
            "timestamp": self.timestamp,
        }


class ContextPrefetcher:
    """
    Proactively stages relevant legal precedents, statutory summaries,
    and code context into the companion card queue before the user asks.
    """

    def __init__(
        self,
        hybrid_retriever: Optional[HybridRetriever] = None,
        anomaly_detector: Optional[AnomalyDetector] = None,
        statute_verifier: Optional[StatuteVerifier] = None,
        max_staged: int = 15,
    ):
        self.retriever = hybrid_retriever or HybridRetriever()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        self.verifier = statute_verifier or StatuteVerifier()
        self.max_staged = max_staged
        self._staged_items: List[StagedContextItem] = []
        self._lock = threading.RLock()

    def stage_from_context(
        self,
        text: str,
        window_ctx: Optional[WindowContext] = None,
    ) -> List[StagedContextItem]:
        if not text or len(text.strip()) < 10:
            return []

        staged_new: List[StagedContextItem] = []

        # 1. Statutory citation extraction and verification
        citations = self.verifier.scan_text(text)
        for cit in citations:
            staged_new.append(
                StagedContextItem(
                    source="statute_verifier",
                    title=f"Statute Ground: {cit.correct_title} ({cit.section})",
                    summary=cit.notes,
                    relevance_score=0.98 if cit.is_valid else 0.85,
                    details=cit.to_dict(),
                )
            )

        # 2. Anomaly check
        anomalies = self.anomaly_detector.detect_anomalies(text, window_ctx, broadcast_alert=False)
        for an in anomalies:
            staged_new.append(
                StagedContextItem(
                    source="anomaly",
                    title=an.title,
                    summary=an.description,
                    relevance_score=0.95,
                    details=an.to_dict(),
                )
            )

        # 3. Extract keywords and query HybridRetriever
        clean_query = text[:200].replace("\n", " ").strip()
        retrieval_res = self.retriever.retrieve(clean_query, n_results=3)

        for res in retrieval_res.get("results", []):
            if res["source"] == "knowledge_graph":
                title = f"{res['node_type']}: {res['node_id']}"
                props = res.get("properties", {})
                summary = props.get("title") or props.get("act_name") or str(props)
                staged_new.append(
                    StagedContextItem(
                        source="knowledge_graph",
                        title=title,
                        summary=summary,
                        relevance_score=res.get("rrf_score", 0.7),
                        details=res,
                    )
                )
            elif res["source"] == "vector_store":
                staged_new.append(
                    StagedContextItem(
                        source="vector_store",
                        title="Document Memory Excerpt",
                        summary=res["content"][:150] + "...",
                        relevance_score=res.get("rrf_score", 0.6),
                        details=res,
                    )
                )

        # Enqueue thread-safely
        with self._lock:
            for item in staged_new:
                # Avoid duplicate titles
                if not any(it.title == item.title for it in self._staged_items):
                    self._staged_items.insert(0, item)
            self._staged_items = self._staged_items[: self.max_staged]

        return staged_new

    def get_staged_queue(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [it.to_dict() for it in self._staged_items]

    def clear_queue(self) -> None:
        with self._lock:
            self._staged_items.clear()


_GLOBAL_PREFETCHER: Optional[ContextPrefetcher] = None


def get_context_prefetcher() -> ContextPrefetcher:
    global _GLOBAL_PREFETCHER
    if _GLOBAL_PREFETCHER is None:
        _GLOBAL_PREFETCHER = ContextPrefetcher()
    return _GLOBAL_PREFETCHER
