"""Minimal langgraph-compatible execution shim for SweetyAI.

Provides just enough of the `langgraph.graph` API (StateGraph, START, END) to
run the SweetyAI orchestrators sequentially when the real `langgraph` package
is not installed. Supports:

  - add_node(name, fn)
  - add_edge(source, target)
  - add_conditional_edges(node, router_fn, mapping)
  - compile() -> object with .invoke(state)

Execution model: start from the node connected to START, merge each node's
returned dict into the running state, follow the fixed or conditional edge,
and stop when END is reached.
"""

from typing import Any, Callable, Dict, Optional

START = "__start__"
END = "__end__"

_MAX_STEPS = 200  # Safety valve against accidental cyclic graphs


class StateGraph:
    """Sequential stand-in for langgraph.graph.StateGraph."""

    def __init__(self, state_schema=None):
        self.state_schema = state_schema
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, str] = {}
        self.conditional: Dict[str, tuple] = {}

    def add_node(self, name: str, fn: Callable) -> "StateGraph":
        self.nodes[name] = fn
        return self

    def add_edge(self, source: str, target: str) -> "StateGraph":
        self.edges[source] = target
        return self

    def add_conditional_edges(self, node: str, router: Callable, mapping: Dict[str, str]) -> "StateGraph":
        self.conditional[node] = (router, mapping)
        return self

    def compile(self):
        return CompiledGraph(self)


class CompiledGraph:
    def __init__(self, graph: StateGraph):
        self.graph = graph

    def _next_node(self, current: str, state: Dict[str, Any]) -> Optional[str]:
        if current in self.graph.conditional:
            router, mapping = self.graph.conditional[current]
            key = router(state)
            if key not in mapping:
                raise ValueError(
                    f"Conditional edge from '{current}' has no route for value '{key}'. "
                    f"Available routes: {sorted(mapping)}"
                )
            return mapping[key]
        return self.graph.edges.get(current)

    def invoke(self, state: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        running_state = dict(state)

        current = self.graph.edges.get(START)
        if current is None:
            raise ValueError("Graph has no edge from START; define add_edge(START, <entry node>).")

        steps = 0
        while current != END:
            steps += 1
            if steps > _MAX_STEPS:
                raise RuntimeError(f"Graph execution exceeded {_MAX_STEPS} steps; possible loop.")

            fn = self.graph.nodes.get(current)
            if fn is None:
                raise ValueError(f"Referenced node '{current}' is not registered via add_node().")

            result = fn(running_state)
            if isinstance(result, dict):
                running_state.update(result)

            nxt = self._next_node(current, running_state)
            if nxt is None:
                raise ValueError(f"Node '{current}' has no outgoing edge; connect it to another node or END.")
            current = nxt

        return running_state
