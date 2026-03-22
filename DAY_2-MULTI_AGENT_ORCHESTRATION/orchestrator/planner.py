"""
Orchestrator / Planner Agent
============================
Deliverable: /orchestrator/planner.py

DAY 2 Topics Covered
---------------------
✔  Planner–Executor architecture   — OrchestratorAgent separates planning from execution
✔  DAG-based execution             — ExecutionPlan holds a directed acyclic graph of Tasks
✔  Task graph generation           — _build_dag() creates nodes + dependency edges
✔  Agent registry pattern          — AgentRegistry maps type strings to factory functions

DAG Topology (fixed for this exercise)
----------------------------------------
    task_1 (WORKER/researcher) ──┐
    task_2 (WORKER/analyst)    ──┼──► task_4 (REFLECTION) ──► task_5 (VALIDATOR)
    task_3 (WORKER/processor)  ──┘

    Tier 0 — 3 parallel WORKER tasks   (no dependencies → READY at start)
    Tier 1 — 1 REFLECTION task          (depends on all workers)
    Tier 2 — 1 VALIDATOR task           (depends on reflection)
"""
from __future__ import annotations

# ── Path fix ──────────────────────────────────────────────────────────────────
# Ensures the PROJECT ROOT is always on sys.path so  'from agents.x import Y'
# finds YOUR local agents/ folder — not any installed 'agents' package.
# Works when run as:
#   python main.py                    (cwd = project root)  ← recommended
#   python orchestrator/planner.py   (cwd = project root)
#   python planner.py                (cwd = orchestrator/)
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
# ─────────────────────────────────────────────────────────────────────────────

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# ══════════════════════════════════════════════════════════════════════════
# Task status
# ══════════════════════════════════════════════════════════════════════════

class TaskStatus(str, Enum):
    WAITING   = "WAITING"    # blocked — dependencies not yet complete
    READY     = "READY"      # all deps done, can be executed immediately
    RUNNING   = "RUNNING"    # currently executing
    COMPLETED = "COMPLETED"  # finished successfully
    FAILED    = "FAILED"     # all retries exhausted


# ══════════════════════════════════════════════════════════════════════════
# Task node  (one vertex in the DAG)
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class Task:
    """
    A single node in the execution DAG.

    Fields
    ------
    task_id      : unique identifier (e.g. "task_1")
    agent_type   : which registry entry handles this ("WORKER" | "REFLECTION" | "VALIDATOR")
    description  : human-readable description of what this task does
    dependencies : list of task_ids that MUST complete before this task runs
    status       : current TaskStatus
    result       : output text (set after COMPLETED)
    error        : error message (set after FAILED)
    meta         : arbitrary extra data passed to the agent at runtime
    """
    task_id:      str
    agent_type:   str
    description:  str
    dependencies: List[str]          = field(default_factory=list)
    status:       TaskStatus         = TaskStatus.WAITING
    result:       Optional[str]      = None
    error:        Optional[str]      = None
    meta:         Dict[str, Any]     = field(default_factory=dict)

    def is_ready(self, completed_ids: set) -> bool:
        """True when every dependency has been completed."""
        return all(dep in completed_ids for dep in self.dependencies)

    def status_icon(self) -> str:
        return {
            TaskStatus.WAITING:   "⏳",
            TaskStatus.READY:     "🟡",
            TaskStatus.RUNNING:   "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED:    "❌",
        }.get(self.status, "❓")


# ══════════════════════════════════════════════════════════════════════════
# Execution Plan  (the DAG)
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class ExecutionPlan:
    """
    The full directed acyclic graph for one user query.

    Contains an ordered list of Task nodes.  Edges are expressed as
    Task.dependencies lists (pull model — each task declares what it
    needs, not what it produces).
    """
    plan_id: str
    query:   str
    tasks:   List[Task] = field(default_factory=list)

    # ── Look-ups ──────────────────────────────────────────────────────────

    def get(self, task_id: str) -> Optional[Task]:
        return next((t for t in self.tasks if t.task_id == task_id), None)

    def by_type(self, agent_type: str) -> List[Task]:
        return [t for t in self.tasks if t.agent_type == agent_type]

    def worker_tasks(self) -> List[Task]:
        return self.by_type("WORKER")

    # ── ASCII execution tree ──────────────────────────────────────────────

    def visualise(self) -> str:
        """
        Render the DAG as an ASCII execution tree showing:
          - Agent type and task ID for each node
          - Current status with icon
          - Dependency relationships
          - Result preview (first 80 chars) once completed
        """
        sep = "=" * 62
        lines = [sep, "  EXECUTION TREE (DAG)", sep]

        # Group tasks by dependency tier for indented tree display
        tiers: List[List[Task]] = []
        placed: set = set()

        while len(placed) < len(self.tasks):
            tier = [
                t for t in self.tasks
                if t.task_id not in placed
                and all(d in placed for d in t.dependencies)
            ]
            if not tier:
                break
            tiers.append(tier)
            placed.update(t.task_id for t in tier)

        for tier_idx, tier in enumerate(tiers):
            indent = "  " * tier_idx
            connector = "├─" if len(tier) > 1 else "└─"

            for i, task in enumerate(tier):
                is_last = (i == len(tier) - 1)
                conn = "└─" if is_last else "├─"

                lines.append(
                    f"{indent}{conn} {task.status_icon()}  "
                    f"[{task.agent_type}]  {task.task_id}"
                )
                lines.append(
                    f"{indent}{'  ' if is_last else '│ '}    "
                    f"desc : {task.description[:55]}{'…' if len(task.description)>55 else ''}"
                )

                if task.dependencies:
                    lines.append(
                        f"{indent}{'  ' if is_last else '│ '}    "
                        f"deps : {', '.join(task.dependencies)}"
                    )

                if task.result:
                    preview = task.result[:80].replace("\n", " ")
                    lines.append(
                        f"{indent}{'  ' if is_last else '│ '}    "
                        f"out  : {preview}…"
                    )

                if task.error:
                    lines.append(
                        f"{indent}{'  ' if is_last else '│ '}    "
                        f"err  : {task.error[:80]}"
                    )

                # Arrow pointing down to next tier
                if tier_idx < len(tiers) - 1 and is_last and len(tier) > 1:
                    lines.append(f"{indent}  ↓  (all complete → next tier)")
                elif tier_idx < len(tiers) - 1 and len(tier) == 1:
                    lines.append(f"{indent}  ↓")

        lines.append(sep)
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════
# Agent Registry  (registry pattern)
# ══════════════════════════════════════════════════════════════════════════

class AgentRegistry:
    """
    Maps agent-type strings to factory callables.

    Registry pattern benefits:
      - New agent types can be added without modifying the planner
      - Factories can inject configuration at creation time
      - The planner remains decoupled from concrete agent classes
      - Easy to mock agents for testing

    Usage
    -----
        registry = AgentRegistry()
        registry.register("WORKER", lambda worker_id=1: WorkerAgent(worker_id=worker_id))
        agent = registry.create("WORKER", worker_id=2)
    """

    def __init__(self):
        self._registry: Dict[str, Callable[..., Any]] = {}

    def register(self, agent_type: str, factory: Callable[..., Any]) -> None:
        """Register a factory function for an agent type."""
        self._registry[agent_type] = factory

    def create(self, agent_type: str, **kwargs) -> Any:
        """Instantiate an agent by type, passing kwargs to its factory."""
        if agent_type not in self._registry:
            raise KeyError(
                f"Unknown agent type '{agent_type}'. "
                f"Registered: {list(self._registry.keys())}"
            )
        return self._registry[agent_type](**kwargs)

    def registered_types(self) -> List[str]:
        return list(self._registry.keys())

    def __repr__(self) -> str:
        return f"AgentRegistry(types={self.registered_types()})"


# ══════════════════════════════════════════════════════════════════════════
# Orchestrator / Planner
# ══════════════════════════════════════════════════════════════════════════

class OrchestratorAgent:
    """
    Planner that builds the execution DAG and owns the AgentRegistry.

    Responsibilities
    ----------------
    1. Accept a user query
    2. Decompose it into a fixed-topology DAG of sub-tasks
    3. Assign each task an agent_type via the AgentRegistry
    4. Set initial statuses (READY for tier-0 workers, WAITING for the rest)
    5. Expose the plan to the ExecutionEngine via current_plan

    The topology is intentionally fixed for this exercise so the
    structure is clear and easy to reason about.  In a production
    system the planner would call an LLM to dynamically decompose
    the query into an arbitrary graph.
    """

    def __init__(self, num_workers: int = 3):
        self.num_workers = num_workers
        self.registry    = self._build_registry()
        self.current_plan: Optional[ExecutionPlan] = None

    # ── Registry construction ─────────────────────────────────────────────

    @staticmethod
    def _build_registry() -> AgentRegistry:
        """
        Register all known agent types.
        Imported lazily to avoid circular imports.
        """
        from agents.worker_agent     import WorkerAgent
        from agents.reflection_agent import ReflectionAgent
        from agents.validator        import ValidatorAgent

        registry = AgentRegistry()
        registry.register("WORKER",     lambda worker_id=1: WorkerAgent(worker_id=worker_id))
        registry.register("REFLECTION", lambda: ReflectionAgent())
        registry.register("VALIDATOR",  lambda: ValidatorAgent())
        return registry

    # ── Public interface ──────────────────────────────────────────────────

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build the execution plan for a user query."""
        query = input_data.get("query", "")
        self.current_plan = self._build_dag(query)
        return {
            "status":  "success",
            "plan_id": self.current_plan.plan_id,
            "tasks":   len(self.current_plan.tasks),
            "tiers":   3,
        }

    def visualise_plan(self) -> str:
        if self.current_plan is None:
            return "No plan built yet — call process() first."
        return self.current_plan.visualise()

    # ── DAG construction ──────────────────────────────────────────────────

    def _build_dag(self, query: str) -> ExecutionPlan:
        """
        Construct the 3-tier DAG:

        Tier 0  task_1, task_2, task_3   WORKER   (READY — no deps)
                    │         │         │
                    └────┬────┴─────────┘
                         ↓
        Tier 1        task_4             REFLECTION  (WAITING — needs all workers)
                         │
                         ↓
        Tier 2        task_5             VALIDATOR   (WAITING — needs reflection)
        """
        plan_id = str(uuid.uuid4())[:8]
        tasks:   List[Task] = []

        # ── Tier 0: worker tasks ─────────────────────────────────────────
        worker_descriptions = [
            f"Research and gather comprehensive factual information about: {query}",
            f"Analyse aspects, patterns, trade-offs and implications of: {query}",
            f"Extract practical details, code examples and applications of: {query}",
        ]
        worker_ids: List[str] = []

        for i in range(self.num_workers):
            tid = f"task_{i + 1}"
            tasks.append(Task(
                task_id      = tid,
                agent_type   = "WORKER",
                description  = worker_descriptions[i % len(worker_descriptions)],
                dependencies = [],                   # no deps → READY immediately
                status       = TaskStatus.READY,
                meta         = {"worker_id": i + 1},
            ))
            worker_ids.append(tid)

        # ── Tier 1: reflection ────────────────────────────────────────────
        reflection_id = f"task_{self.num_workers + 1}"
        tasks.append(Task(
            task_id      = reflection_id,
            agent_type   = "REFLECTION",
            description  = f"Synthesise all worker outputs into one coherent answer for: {query}",
            dependencies = worker_ids,              # blocked until all workers done
            status       = TaskStatus.WAITING,
        ))

        # ── Tier 2: validator ─────────────────────────────────────────────
        tasks.append(Task(
            task_id      = f"task_{self.num_workers + 2}",
            agent_type   = "VALIDATOR",
            description  = f"Validate quality and correctness of the final answer for: {query}",
            dependencies = [reflection_id],         # blocked until reflection done
            status       = TaskStatus.WAITING,
        ))

        return ExecutionPlan(plan_id=plan_id, query=query, tasks=tasks)

    def __repr__(self) -> str:
        return (
            f"OrchestratorAgent("
            f"workers={self.num_workers}, "
            f"registry={self.registry})"
        )