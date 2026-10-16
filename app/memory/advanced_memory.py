"""
SweetyAI - Advanced Memory & Persona System
Episodic memory, semantic memory, dynamic personas, context optimization, cross-reference engine
"""

import os
import json
import time
import hashlib
import math
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import threading


# =============================================================================
# SEMANTIC MEMORY — long-lived facts about the user and world
# =============================================================================

@dataclass
class SemanticFact:
    fact_id: str
    category: str          # "user_preference", "world_knowledge", "tool_behaviour", ...
    subject: str
    content: str
    confidence: float      # 0.0-1.0
    source: str            # which conversation or tool produced this
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    tags: List[str] = field(default_factory=list)


class SemanticMemory:
    """Long-term factual memory that persists across conversations."""

    def __init__(self, store_path: str = "memory/semantic"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.facts: Dict[str, SemanticFact] = {}
        self.index: Dict[str, List[str]] = defaultdict(list)   # category -> [fact_id]
        self.lock = threading.Lock()
        self._load()

    def store(self, category: str, subject: str, content: str, confidence: float = 0.8,
              source: str = "conversation", tags: List[str] = None) -> str:
        fact_id = hashlib.sha256(f"{category}:{subject}:{content}".encode()).hexdigest()[:16]

        with self.lock:
            existing = self.facts.get(fact_id)
            if existing:
                # Reinforce — raise confidence, update timestamp
                existing.confidence = min(1.0, existing.confidence + 0.05)
                existing.last_accessed = datetime.now().isoformat()
                existing.access_count += 1
            else:
                fact = SemanticFact(
                    fact_id=fact_id, category=category, subject=subject,
                    content=content, confidence=confidence, source=source,
                    tags=tags or [],
                )
                self.facts[fact_id] = fact
                self.index[category].append(fact_id)

        self._save()
        return fact_id

    def recall(self, query: str, category: str = None, top_k: int = 5) -> List[SemanticFact]:
        """Retrieve facts relevant to a query using keyword matching."""
        query_lower = query.lower()
        scored: List[Tuple[float, SemanticFact]] = []

        with self.lock:
            pool = self.facts.values() if not category else [
                self.facts[fid] for fid in self.index.get(category, []) if fid in self.facts
            ]

        for fact in pool:
            score = self._relevance_score(query_lower, fact)
            if score > 0:
                scored.append((score, fact))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Update access stats
        results = []
        for _, fact in scored[:top_k]:
            fact.last_accessed = datetime.now().isoformat()
            fact.access_count += 1
            results.append(fact)

        return results

    def forget(self, fact_id: str) -> bool:
        with self.lock:
            fact = self.facts.pop(fact_id, None)
            if fact:
                cat_list = self.index.get(fact.category, [])
                if fact_id in cat_list:
                    cat_list.remove(fact_id)
                self._save()
                return True
        return False

    def decay(self, days_threshold: int = 30, min_confidence: float = 0.3):
        """Decay old, rarely-accessed facts."""
        cutoff = datetime.now() - timedelta(days=days_threshold)
        to_remove = []

        with self.lock:
            for fid, fact in self.facts.items():
                last = datetime.fromisoformat(fact.last_accessed)
                if last < cutoff and fact.confidence < min_confidence and fact.access_count < 3:
                    to_remove.append(fid)

        for fid in to_remove:
            self.forget(fid)

        return len(to_remove)

    def _relevance_score(self, query: str, fact: SemanticFact) -> float:
        text = f"{fact.subject} {fact.content} {' '.join(fact.tags)}".lower()
        words = query.split()
        hits = sum(1 for w in words if w in text)
        if not words:
            return 0
        return (hits / len(words)) * fact.confidence

    def _save(self):
        data = {fid: asdict(f) for fid, f in self.facts.items()}
        with open(self.store_path / "facts.json", "w") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        path = self.store_path / "facts.json"
        if not path.exists():
            return
        try:
            with open(path) as f:
                data = json.load(f)
            for fid, d in data.items():
                self.facts[fid] = SemanticFact(**d)
                self.index[d["category"]].append(fid)
        except Exception:
            pass

    def get_all(self, category: str = None) -> List[Dict[str, Any]]:
        with self.lock:
            if category:
                return [asdict(self.facts[fid]) for fid in self.index.get(category, []) if fid in self.facts]
            return [asdict(f) for f in self.facts.values()]


# =============================================================================
# EPISODIC MEMORY — conversation-level recollections
# =============================================================================

@dataclass
class Episode:
    episode_id: str
    timestamp: str
    summary: str
    key_topics: List[str]
    user_intent: str
    outcome: str       # "resolved", "partial", "failed"
    messages_count: int
    tool_calls: List[str]
    emotional_tone: str  # "positive", "neutral", "frustrated", ...
    facts_learned: List[str]


class EpisodicMemory:
    """Conversation-level memory — remembers what happened in past sessions."""

    def __init__(self, store_path: str = "memory/episodic"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.episodes: List[Episode] = []
        self.lock = threading.Lock()
        self._load()

    def record_episode(
        self,
        summary: str,
        key_topics: List[str],
        user_intent: str,
        outcome: str,
        messages_count: int,
        tool_calls: List[str] = None,
        emotional_tone: str = "neutral",
        facts_learned: List[str] = None,
    ) -> str:
        ep = Episode(
            episode_id=hashlib.sha256(f"{summary}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            timestamp=datetime.now().isoformat(),
            summary=summary,
            key_topics=key_topics,
            user_intent=user_intent,
            outcome=outcome,
            messages_count=messages_count,
            tool_calls=tool_calls or [],
            emotional_tone=emotional_tone,
            facts_learned=facts_learned or [],
        )
        with self.lock:
            self.episodes.append(ep)
        self._save()
        return ep.episode_id

    def recall_episodes(self, query: str = None, topic: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        with self.lock:
            pool = list(self.episodes)

        if topic:
            pool = [e for e in pool if topic.lower() in [t.lower() for t in e.key_topics]]

        if query:
            q = query.lower()
            pool = [e for e in pool if q in e.summary.lower() or q in e.user_intent.lower()]

        pool.sort(key=lambda e: e.timestamp, reverse=True)
        return [asdict(e) for e in pool[:limit]]

    def get_recent(self, count: int = 5) -> List[Dict[str, Any]]:
        with self.lock:
            return [asdict(e) for e in self.episodes[-count:]]

    def _save(self):
        with open(self.store_path / "episodes.json", "w") as f:
            json.dump([asdict(e) for e in self.episodes], f, indent=2)

    def _load(self):
        path = self.store_path / "episodes.json"
        if not path.exists():
            return
        try:
            with open(path) as f:
                data = json.load(f)
            self.episodes = [Episode(**d) for d in data]
        except Exception:
            pass


# =============================================================================
# DYNAMIC PERSONA SYSTEM
# =============================================================================

@dataclass
class Persona:
    name: str
    description: str
    tone: str                    # "formal", "casual", "friendly", "academic", ...
    expertise_level: str         # "beginner", "intermediate", "expert"
    personality_traits: List[str]
    response_style: str          # "concise", "detailed", "step-by-step"
    system_prompt_prefix: str


class PersonaManager:
    """Switch the AI's persona on-the-fly."""

    BUILT_IN_PERSONAS = {
        "default": Persona(
            name="SweetyAI",
            description="Helpful, friendly AI assistant",
            tone="friendly",
            expertise_level="expert",
            personality_traits=["helpful", "thorough", "patient"],
            response_style="detailed",
            system_prompt_prefix="You are SweetyAI, a helpful and friendly assistant.",
        ),
        "coding_mentor": Persona(
            name="Code Mentor",
            description="Strict but supportive coding teacher",
            tone="professional",
            expertise_level="expert",
            personality_traits=["precise", "educational", "encouraging"],
            response_style="step-by-step",
            system_prompt_prefix="You are a senior software engineer and coding mentor. Explain clearly, give examples.",
        ),
        "creative_partner": Persona(
            name="Creative Partner",
            description="Casual brainstorming buddy",
            tone="casual",
            expertise_level="intermediate",
            personality_traits=["creative", "playful", "open-minded"],
            response_style="concise",
            system_prompt_prefix="You are a creative brainstorming partner. Think outside the box, be fun.",
        ),
        "research_analyst": Persona(
            name="Research Analyst",
            description="Data-driven, formal analyst",
            tone="academic",
            expertise_level="expert",
            personality_traits=["analytical", "rigorous", "objective"],
            response_style="detailed",
            system_prompt_prefix="You are a research analyst providing data-backed, rigorous analysis.",
        ),
        "executive_assistant": Persona(
            name="Executive Assistant",
            description="Professional executive support",
            tone="formal",
            expertise_level="expert",
            personality_traits=["efficient", "proactive", "discrete"],
            response_style="concise",
            system_prompt_prefix="You are an executive assistant. Be concise, anticipate needs.",
        ),
    }

    def __init__(self, custom_path: str = "config/personas.json"):
        self.custom_path = Path(custom_path)
        self.custom_path.parent.mkdir(parents=True, exist_ok=True)
        self.personas: Dict[str, Persona] = dict(self.BUILT_IN_PERSONAS)
        self.active_persona: str = "default"
        self._load_custom()

    def set_persona(self, name: str) -> str:
        if name not in self.personas:
            return f"Unknown persona: {name}. Available: {', '.join(self.personas.keys())}"
        self.active_persona = name
        return f"Switched to persona: {self.personas[name].name}"

    def get_active(self) -> Persona:
        return self.personas[self.active_persona]

    def get_system_prompt(self) -> str:
        return self.get_active().system_prompt_prefix

    def create_persona(self, name: str, **kwargs) -> str:
        self.personas[name] = Persona(name=name, **kwargs)
        self._save_custom()
        return f"Persona '{name}' created"

    def list_personas(self) -> List[Dict[str, str]]:
        return [
            {"name": n, "description": p.description, "tone": p.tone, "active": n == self.active_persona}
            for n, p in self.personas.items()
        ]

    def _save_custom(self):
        custom = {
            k: asdict(v) for k, v in self.personas.items() if k not in self.BUILT_IN_PERSONAS
        }
        with open(self.custom_path, "w") as f:
            json.dump(custom, f, indent=2)

    def _load_custom(self):
        if not self.custom_path.exists():
            return
        try:
            with open(self.custom_path) as f:
                data = json.load(f)
            for name, d in data.items():
                self.personas[name] = Persona(**d)
        except Exception:
            pass


# =============================================================================
# CONTEXT OPTIMIZER — manage the context window intelligently
# =============================================================================

class ContextOptimizer:
    """Prioritise, compress, and manage the LLM context window."""

    def __init__(self, max_tokens: int = 8192):
        self.max_tokens = max_tokens

    def prioritize(self, messages: List[Dict[str, str]], system_context: str = "") -> List[Dict[str, str]]:
        """Keep the most relevant messages within the token budget."""
        estimated = self._estimate_tokens(system_context)
        budget = self.max_tokens - estimated - 512  # leave headroom

        # Always keep first (system) and last N user messages
        keep_tail = min(6, len(messages))
        tail = messages[-keep_tail:]
        rest = messages[:-keep_tail]

        tail_tokens = sum(self._estimate_tokens(m.get("content", "")) for m in tail)
        remaining = budget - tail_tokens

        # Score older messages by recency + role weight
        scored = []
        for i, m in enumerate(rest):
            recency = i / max(len(rest), 1)
            role_weight = 1.2 if m.get("role") == "user" else 1.0
            scored.append((recency * role_weight, m))

        scored.sort(key=lambda x: x[0], reverse=True)

        kept = []
        used = 0
        for _, m in scored:
            t = self._estimate_tokens(m.get("content", ""))
            if used + t <= remaining:
                kept.append(m)
                used += t

        # Re-order chronologically
        kept.sort(key=lambda m: messages.index(m))
        return kept + tail

    def compress_message(self, text: str, ratio: float = 0.5) -> str:
        """Simple extractive compression: keep the most information-dense sentences."""
        sentences = [s.strip() for s in text.replace("\n", ". ").split(".") if s.strip()]
        if not sentences:
            return text

        keep_count = max(1, int(len(sentences) * ratio))

        # Score by length (proxy for information content)
        scored = [(len(s.split()), s) for s in sentences]
        scored.sort(key=lambda x: x[0], reverse=True)

        kept = [s for _, s in scored[:keep_count]]
        # Preserve original order
        kept_ordered = [s for s in sentences if s in kept]
        return ". ".join(kept_ordered) + "."

    def summarize_history(self, messages: List[Dict[str, str]]) -> str:
        """Create a brief summary of conversation history."""
        user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
        assistant_msgs = [m["content"] for m in messages if m.get("role") == "assistant"]

        topics = set()
        for msg in user_msgs:
            words = msg.lower().split()
            # Extract likely topic words (longer words, not stop words)
            topics.update(w for w in words if len(w) > 4)

        summary_parts = [
            f"Conversation with {len(messages)} messages.",
            f"User asked about: {', '.join(list(topics)[:10])}.",
        ]
        return " ".join(summary_parts)

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return len(text) // 4


# =============================================================================
# CROSS-REFERENCE ENGINE
# =============================================================================

class CrossReferenceEngine:
    """Cross-reference data across multiple attached documents and data sources."""

    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None):
        with self.lock:
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            self.documents[doc_id] = {
                "content": content,
                "paragraphs": paragraphs,
                "metadata": metadata or {},
                "added_at": datetime.now().isoformat(),
            }

    def search_across(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search query across all loaded documents."""
        q_lower = query.lower()
        q_words = set(q_lower.split())
        results = []

        with self.lock:
            for doc_id, doc in self.documents.items():
                for i, para in enumerate(doc["paragraphs"]):
                    para_lower = para.lower()
                    para_words = set(para_lower.split())
                    overlap = len(q_words & para_words)
                    if overlap > 0:
                        score = overlap / max(len(q_words), 1)
                        results.append({
                            "doc_id": doc_id,
                            "paragraph_index": i,
                            "text": para[:500],
                            "score": score,
                        })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    def find_contradictions(self, topic: str) -> List[Dict[str, Any]]:
        """Find statements about the same topic that may conflict across documents."""
        matches = self.search_across(topic, top_k=20)

        # Very simple: flag pairs from different docs with low text similarity
        contradictions = []
        for i, a in enumerate(matches):
            for b in matches[i + 1:]:
                if a["doc_id"] != b["doc_id"]:
                    sim = self._jaccard(a["text"], b["text"])
                    if 0.05 < sim < 0.4:  # Same topic but different wording → possible contradiction
                        contradictions.append({
                            "doc_a": a["doc_id"],
                            "text_a": a["text"][:200],
                            "doc_b": b["doc_id"],
                            "text_b": b["text"][:200],
                            "similarity": round(sim, 3),
                        })
        return contradictions[:5]

    def remove_document(self, doc_id: str):
        with self.lock:
            self.documents.pop(doc_id, None)

    @staticmethod
    def _jaccard(a: str, b: str) -> float:
        sa, sb = set(a.lower().split()), set(b.lower().split())
        union = sa | sb
        if not union:
            return 0.0
        return len(sa & sb) / len(union)


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

semantic_memory = SemanticMemory()
episodic_memory = EpisodicMemory()
persona_manager = PersonaManager()
context_optimizer = ContextOptimizer()
cross_reference = CrossReferenceEngine()


__all__ = [
    "SemanticFact",
    "SemanticMemory",
    "Episode",
    "EpisodicMemory",
    "Persona",
    "PersonaManager",
    "ContextOptimizer",
    "CrossReferenceEngine",
    "semantic_memory",
    "episodic_memory",
    "persona_manager",
    "context_optimizer",
    "cross_reference",
]
