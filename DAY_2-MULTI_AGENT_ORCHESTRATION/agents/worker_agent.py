"""
Worker Agent
============
Deliverable: /agents/worker_agent.py

DAY 2 Exercise requirement:
  ✔  Parallel workers — 3 instances run simultaneously via asyncio.gather()
  ✔  Each worker has a distinct role so outputs are complementary, not redundant:
       Worker-1  researcher  — theory, math, derivations, history
       Worker-2  analyst     — trade-offs, hyperparameters, benchmarks
       Worker-3  processor   — working code, implementation, practical usage

The executor calls asyncio.gather(*[worker.process(task) for worker in workers])
so all three run truly in parallel — not sequentially.
"""
from __future__ import annotations

# ── Path fix ──────────────────────────────────────────────────────────────────
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
# ─────────────────────────────────────────────────────────────────────────────
from typing import Any, Dict

import config
from agents.base_agent import BaseAgent


# ══════════════════════════════════════════════════════════════════════════
# Role definitions
# ══════════════════════════════════════════════════════════════════════════

# Each worker gets a distinct system prompt so the three parallel outputs
# cover different aspects of the query — the Reflection Agent then
# synthesises them into one complete answer.

_ROLE_PROMPTS: Dict[str, str] = {

    "researcher": (
        "You are a meticulous research specialist and subject-matter expert.\n"
        "Produce a COMPREHENSIVE, DEEP response that includes:\n"
        "  • Core concepts with precise definitions\n"
        "  • Mathematical formulations, equations, or derivations where relevant\n"
        "  • Key algorithms described step-by-step\n"
        "  • Historical context and how the field evolved\n"
        "  • Concrete examples with specific data or numbers\n"
        "  • Important papers or milestones where applicable\n\n"
        "Format with ## markdown headings.\n"
        "Be exhaustive — depth and accuracy matter more than brevity.\n"
        "Never write 'As an AI…' — answer directly as an expert."
    ),

    "analyst": (
        "You are a sharp analytical thinker and technical expert.\n"
        "Produce a DEEP ANALYTICAL response that includes:\n"
        "  • Critical comparison of approaches and architectures\n"
        "  • Hyperparameter analysis — what parameters exist, how to tune them,\n"
        "    and what effect each has on performance\n"
        "  • Trade-offs, limitations, and known failure modes\n"
        "  • Performance benchmarks or complexity analysis (time/space/compute)\n"
        "  • Best practices for model selection — when to use which variant\n"
        "  • Common pitfalls and how to diagnose/fix them\n\n"
        "Format with ## markdown headings.\n"
        "Be specific — vague generalities are not acceptable.\n"
        "Never write 'As an AI…' — answer directly as an expert."
    ),

    "processor": (
        "You are a practical engineer and implementation specialist.\n"
        "Produce a DETAILED PRACTICAL response that includes:\n"
        "  • Working Python code (not pseudocode) with proper imports,\n"
        "    complete logic, and inline comments explaining each step\n"
        "  • Step-by-step implementation walkthrough\n"
        "  • Real-world use cases with concrete scenarios\n"
        "  • Production considerations: scaling, edge cases, efficiency\n"
        "  • Libraries and frameworks used in practice\n"
        "  • How to verify correctness and debug common issues\n\n"
        "Format with ## markdown headings and ```python code blocks.\n"
        "Code must be realistic and runnable, not toy examples.\n"
        "Never write 'As an AI…' — answer directly as an expert."
    ),
}

_WORKER_ROLES = ["researcher", "analyst", "processor"]


# ══════════════════════════════════════════════════════════════════════════
# WorkerAgent
# ══════════════════════════════════════════════════════════════════════════

class WorkerAgent(BaseAgent):
    """
    Parallel task executor.

    Three instances run simultaneously (via asyncio.gather in the executor).
    Each instance is assigned a different role based on worker_id so the
    parallel outputs are complementary rather than redundant:

        Worker-1  →  researcher   (theory, math, derivations)
        Worker-2  →  analyst      (trade-offs, hyperparameters, benchmarks)
        Worker-3  →  processor    (code, implementation, practical usage)

    The ExecutionEngine creates these via:
        asyncio.gather(worker1.process(t1), worker2.process(t2), worker3.process(t3))
    """

    def __init__(self, name: str = "Worker", worker_id: int = 1):
        super().__init__(name=f"{name}-{worker_id}", role="worker")
        self.worker_id   = worker_id
        self.worker_role = _WORKER_ROLES[(worker_id - 1) % len(_WORKER_ROLES)]

    # ── Public interface ──────────────────────────────────────────────────

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute one sub-task and return the LLM output.

        Called by ExecutionEngine inside asyncio.gather() so this method
        runs concurrently with the other two worker instances.
        """
        task_id     = task.get("task_id",     "unknown")
        query       = task.get("query",       "")
        description = task.get("description", query)

        self.logger.info(
            f"Worker-{self.worker_id} [{self.worker_role}] → task {task_id}"
        )
        self.add_to_memory({"action": "started", "task_id": task_id})

        output = await self._run(query, description)

        self.add_to_memory({"action": "completed", "task_id": task_id})
        self.execution_count += 1

        return {
            "status":      "success",
            "task_id":     task_id,
            "worker_id":   self.worker_id,
            "worker_role": self.worker_role,
            "result":      output,
            "agent":       self.to_dict(),
        }

    # ── Private ───────────────────────────────────────────────────────────

    async def _run(self, query: str, description: str) -> str:
        """Build the prompt and call the LLM."""
        system = _ROLE_PROMPTS[self.worker_role]
        user   = (
            f"Task: {description}\n\n"
            f"Original question: {query}\n\n"
            f"Provide a thorough, expert-level {self.worker_role} response.\n"
            "Include mathematical details, hyperparameter guidance, and working "
            "code examples where relevant to this topic.\n"
            "Do not summarise — give the full depth expected of a senior specialist."
        )
        try:
            return await self.call_llm(
                system      = system,
                user        = user,
                model       = config.WORKER_MODEL,
                max_tokens  = config.WORKER_MAX_TOKENS,
                temperature = config.WORKER_TEMPERATURE,
            )
        except Exception as exc:
            self.logger.error(f"Worker-{self.worker_id} LLM call failed: {exc}")
            raise

    def __repr__(self) -> str:
        return (
            f"WorkerAgent("
            f"id={self.worker_id}, "
            f"role='{self.worker_role}', "
            f"name='{self.name}')"
        )