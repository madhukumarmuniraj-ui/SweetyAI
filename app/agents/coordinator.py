"""
SweetyAI - Multi-Agent Coordination System
Autonomous multi-step execution, agent communication, task delegation, result aggregation
"""

import uuid
import time
import threading
import queue
from typing import Dict, Any, Optional, List, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentCapability:
    name: str
    description: str
    handler: Callable
    cost: float = 1.0


@dataclass
class AgentMessage:
    sender_id: str
    receiver_id: str
    content: Any
    message_type: str = "data"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])


@dataclass
class AgentTask:
    task_id: str
    name: str
    description: str
    input_data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    result: Any = None
    error: Optional[str] = None
    parent_task_id: Optional[str] = None
    subtask_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    requires_approval: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assigned_agent": self.assigned_agent,
            "result": self.result,
            "error": self.error,
            "parent_task_id": self.parent_task_id,
            "subtask_ids": self.subtask_ids,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


# =============================================================================
# AGENT
# =============================================================================

class Agent:
    """Individual agent with capabilities and message handling."""

    def __init__(self, agent_id: str, name: str, agent_type: str = "general"):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        self.capabilities: Dict[str, AgentCapability] = {}
        self.inbox: queue.Queue = queue.Queue()
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []
        self.lock = threading.Lock()

    def register_capability(self, name: str, description: str, handler: Callable, cost: float = 1.0):
        self.capabilities[name] = AgentCapability(name, description, handler, cost)

    def can_handle(self, capability_name: str) -> bool:
        return capability_name in self.capabilities

    def execute_task(self, task: AgentTask) -> Any:
        with self.lock:
            self.status = AgentStatus.BUSY
            self.current_task = task
            task.status = TaskStatus.IN_PROGRESS

        try:
            capability_name = task.input_data.get("capability")
            if capability_name and capability_name in self.capabilities:
                result = self.capabilities[capability_name].handler(task.input_data)
            else:
                result = self._default_handler(task)

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()

        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            self.status = AgentStatus.ERROR

        finally:
            with self.lock:
                self.task_history.append(task)
                self.current_task = None
                if self.status != AgentStatus.ERROR:
                    self.status = AgentStatus.IDLE

        return task.result

    def _default_handler(self, task: AgentTask) -> Any:
        return {"status": "completed", "task": task.name, "agent": self.name}

    def send_message(self, message: AgentMessage):
        self.inbox.put(message)

    def receive_message(self, timeout: float = 1.0) -> Optional[AgentMessage]:
        try:
            return self.inbox.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_info(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "status": self.status.value,
            "capabilities": list(self.capabilities.keys()),
            "tasks_completed": len(self.task_history),
        }


# =============================================================================
# TASK PLANNER — decomposes complex goals into sub-tasks
# =============================================================================

class TaskPlanner:
    """Decompose complex goals into executable sub-tasks."""

    def __init__(self):
        self.decomposition_rules: Dict[str, Callable] = {}

    def register_rule(self, task_type: str, decomposer: Callable):
        self.decomposition_rules[task_type] = decomposer

    def decompose(self, goal: str, context: Dict[str, Any]) -> List[AgentTask]:
        """Break a high-level goal into ordered sub-tasks."""
        task_type = context.get("type", "general")
        decomposer = self.decomposition_rules.get(task_type, self._default_decompose)
        return decomposer(goal, context)

    def _default_decompose(self, goal: str, context: Dict[str, Any]) -> List[AgentTask]:
        steps = context.get("steps", [])
        if not steps:
            steps = [{"name": goal, "input": context}]

        tasks = []
        parent_id = uuid.uuid4().hex[:12]

        for i, step in enumerate(steps):
            task = AgentTask(
                task_id=f"{parent_id}_step{i}",
                name=step.get("name", f"Step {i+1}"),
                description=step.get("description", ""),
                input_data=step.get("input", {}),
                priority=TaskPriority(step.get("priority", 1)),
                parent_task_id=parent_id,
                requires_approval=step.get("requires_approval", False),
            )
            tasks.append(task)

        return tasks


# =============================================================================
# RESULT AGGREGATOR
# =============================================================================

class ResultAggregator:
    """Aggregate results from multiple agents/tasks."""

    def __init__(self):
        self.strategies: Dict[str, Callable] = {
            "merge": self._merge_results,
            "chain": self._chain_results,
            "vote": self._vote_results,
            "first": self._first_result,
            "best": self._best_result,
        }

    def aggregate(self, results: List[Any], strategy: str = "merge") -> Any:
        aggregator = self.strategies.get(strategy, self._merge_results)
        return aggregator(results)

    def _merge_results(self, results: List[Any]) -> Dict[str, Any]:
        merged = {}
        for r in results:
            if isinstance(r, dict):
                merged.update(r)
        return merged if merged else {"results": results}

    def _chain_results(self, results: List[Any]) -> List[Any]:
        return results

    def _vote_results(self, results: List[Any]) -> Any:
        if not results:
            return None
        counts = defaultdict(int)
        for r in results:
            key = json.dumps(r, default=str) if isinstance(r, (dict, list)) else str(r)
            counts[key] += 1
        winner = max(counts, key=counts.get)
        return json.loads(winner) if winner.startswith(("{", "[")) else winner

    def _first_result(self, results: List[Any]) -> Any:
        return results[0] if results else None

    def _best_result(self, results: List[Any]) -> Any:
        scored = []
        for r in results:
            score = r.get("confidence", 0) if isinstance(r, dict) else 0
            scored.append((score, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else None


# =============================================================================
# COORDINATOR — the central orchestrator
# =============================================================================

class AgentCoordinator:
    """Central coordinator for multi-agent task execution."""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.tasks: Dict[str, AgentTask] = {}
        self.planner = TaskPlanner()
        self.aggregator = ResultAggregator()
        self.approval_queue: Dict[str, AgentTask] = {}
        self.event_listeners: Dict[str, List[Callable]] = defaultdict(list)
        self.lock = threading.Lock()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None

    # ---- agent management ----

    def register_agent(self, agent: Agent):
        with self.lock:
            self.agents[agent.agent_id] = agent
        self._emit("agent_registered", {"agent": agent.get_info()})

    def unregister_agent(self, agent_id: str):
        with self.lock:
            self.agents.pop(agent_id, None)

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, Any]]:
        return [a.get_info() for a in self.agents.values()]

    # ---- task submission ----

    def submit_goal(
        self,
        goal: str,
        context: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> str:
        """Submit a high-level goal; the planner decomposes it into sub-tasks."""
        context = context or {}
        sub_tasks = self.planner.decompose(goal, context)

        goal_id = uuid.uuid4().hex[:12]
        for task in sub_tasks:
            task.priority = priority
            self._enqueue_task(task)

        self._emit("goal_submitted", {"goal_id": goal_id, "subtasks": len(sub_tasks)})
        return goal_id

    def submit_task(self, task: AgentTask) -> str:
        self._enqueue_task(task)
        return task.task_id

    def _enqueue_task(self, task: AgentTask):
        with self.lock:
            self.tasks[task.task_id] = task
        # PriorityQueue sorts ascending; negate priority so CRITICAL runs first
        self.task_queue.put((-task.priority.value, time.time(), task))
        self._emit("task_queued", {"task_id": task.task_id})

    # ---- execution loop ----

    def start(self):
        """Start the background task-processing loop."""
        self._running = True
        self._worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self._worker_thread.start()

    def stop(self):
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)

    def _run_loop(self):
        while self._running:
            try:
                _, _, task = self.task_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if task.requires_approval:
                task.status = TaskStatus.AWAITING_APPROVAL
                self.approval_queue[task.task_id] = task
                self._emit("approval_required", {"task": task.to_dict()})
                continue

            agent = self._select_agent(task)
            if not agent:
                task.status = TaskStatus.FAILED
                task.error = "No suitable agent available"
                self._emit("task_failed", {"task_id": task.task_id, "error": task.error})
                continue

            task.assigned_agent = agent.agent_id
            task.status = TaskStatus.ASSIGNED
            self._emit("task_assigned", {"task_id": task.task_id, "agent": agent.agent_id})

            # Execute (could be threaded for true parallelism)
            result = agent.execute_task(task)
            self._emit(
                "task_completed" if task.status == TaskStatus.COMPLETED else "task_failed",
                {"task_id": task.task_id, "result": result},
            )

    def _select_agent(self, task: AgentTask) -> Optional[Agent]:
        """Pick the best idle agent that can handle the task."""
        capability = task.input_data.get("capability", "")

        candidates = [
            a for a in self.agents.values()
            if a.status == AgentStatus.IDLE and (not capability or a.can_handle(capability))
        ]

        if not candidates:
            # Fall back to any idle agent
            candidates = [a for a in self.agents.values() if a.status == AgentStatus.IDLE]

        if not candidates:
            return None

        # Prefer agent with fewest completed tasks (load balance)
        candidates.sort(key=lambda a: len(a.task_history))
        return candidates[0]

    # ---- HITL approval ----

    def approve_task(self, task_id: str) -> str:
        task = self.approval_queue.pop(task_id, None)
        if not task:
            return f"Task {task_id} not in approval queue"
        task.requires_approval = False
        self._enqueue_task(task)
        self._emit("task_approved", {"task_id": task_id})
        return f"Task {task_id} approved and re-queued"

    def reject_task(self, task_id: str, reason: str = "") -> str:
        task = self.approval_queue.pop(task_id, None)
        if not task:
            return f"Task {task_id} not in approval queue"
        task.status = TaskStatus.CANCELLED
        task.error = reason or "Rejected by user"
        self._emit("task_rejected", {"task_id": task_id, "reason": task.error})
        return f"Task {task_id} rejected"

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.approval_queue.values()]

    # ---- messaging ----

    def send_message(self, sender_id: str, receiver_id: str, content: Any, msg_type: str = "data"):
        agent = self.agents.get(receiver_id)
        if not agent:
            return
        msg = AgentMessage(sender_id=sender_id, receiver_id=receiver_id, content=content, message_type=msg_type)
        agent.send_message(msg)
        self._emit("message_sent", {"from": sender_id, "to": receiver_id})

    def broadcast(self, sender_id: str, content: Any, msg_type: str = "broadcast"):
        for agent_id in self.agents:
            if agent_id != sender_id:
                self.send_message(sender_id, agent_id, content, msg_type)

    # ---- parallel execution helpers ----

    def execute_parallel(
        self,
        tasks: List[AgentTask],
        aggregation_strategy: str = "merge",
    ) -> Any:
        """Execute multiple tasks in parallel and aggregate results."""
        threads: List[threading.Thread] = []
        results: List[Any] = [None] * len(tasks)

        def _run(index: int, task: AgentTask):
            agent = self._select_agent(task)
            if agent:
                task.assigned_agent = agent.agent_id
                results[index] = agent.execute_task(task)

        for i, task in enumerate(tasks):
            t = threading.Thread(target=_run, args=(i, task))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return self.aggregator.aggregate([r for r in results if r is not None], aggregation_strategy)

    def execute_pipeline(self, tasks: List[AgentTask]) -> Any:
        """Execute tasks sequentially, piping each result into the next."""
        previous_result = None

        for task in tasks:
            if previous_result is not None:
                task.input_data["previous_result"] = previous_result

            agent = self._select_agent(task)
            if not agent:
                return {"error": f"No agent for task {task.name}"}

            task.assigned_agent = agent.agent_id
            previous_result = agent.execute_task(task)

        return previous_result

    # ---- event system ----

    def on(self, event: str, listener: Callable):
        self.event_listeners[event].append(listener)

    def _emit(self, event: str, data: Dict[str, Any]):
        for listener in self.event_listeners.get(event, []):
            try:
                listener(data)
            except Exception:
                pass

    # ---- status ----

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "agents": len(self.agents),
            "idle_agents": sum(1 for a in self.agents.values() if a.status == AgentStatus.IDLE),
            "queued_tasks": self.task_queue.qsize(),
            "pending_approvals": len(self.approval_queue),
            "total_tasks": len(self.tasks),
            "completed_tasks": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
        }


# =============================================================================
# CONVENIENCE — pre-built specialist agents
# =============================================================================

def create_researcher_agent() -> Agent:
    agent = Agent(uuid.uuid4().hex[:8], "Researcher", "research")
    agent.register_capability("web_search", "Search the web", lambda d: {"search_results": f"Results for: {d.get('query', '')}"})
    agent.register_capability("summarize", "Summarize text", lambda d: {"summary": d.get("text", "")[:200] + "..."})
    return agent


def create_coder_agent() -> Agent:
    agent = Agent(uuid.uuid4().hex[:8], "Coder", "coding")
    agent.register_capability("write_code", "Write code", lambda d: {"code": f"# Code for: {d.get('task', '')}"})
    agent.register_capability("review_code", "Review code", lambda d: {"review": "LGTM"})
    return agent


def create_writer_agent() -> Agent:
    agent = Agent(uuid.uuid4().hex[:8], "Writer", "writing")
    agent.register_capability("draft_report", "Draft a report", lambda d: {"report": f"Report: {d.get('topic', '')}"})
    agent.register_capability("edit_text", "Edit text", lambda d: {"edited": d.get("text", "")})
    return agent


def create_analyst_agent() -> Agent:
    agent = Agent(uuid.uuid4().hex[:8], "Analyst", "analysis")
    agent.register_capability("analyze_data", "Analyze data", lambda d: {"analysis": f"Analysis of {d.get('dataset', 'data')}"})
    agent.register_capability("generate_chart", "Generate chart", lambda d: {"chart": "chart.png"})
    return agent


# =============================================================================
# GLOBAL COORDINATOR
# =============================================================================

coordinator = AgentCoordinator()


__all__ = [
    "Agent",
    "AgentCoordinator",
    "AgentTask",
    "AgentMessage",
    "AgentCapability",
    "AgentStatus",
    "TaskStatus",
    "TaskPriority",
    "TaskPlanner",
    "ResultAggregator",
    "coordinator",
    "create_researcher_agent",
    "create_coder_agent",
    "create_writer_agent",
    "create_analyst_agent",
]
