"""
nexus_ai/main.py
NEXUS AI — Entry point
PROJECT: NEXUS AI — Autonomous Multi-Agent AI System
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nexus_ai.agents.orchestrator import OrchestratorAgent
from nexus_ai.config import PROJECT_NAME, PROJECT_VERSION, EXAMPLE_TASKS
from nexus_ai.logger import get_logger

log = get_logger("main")

BANNER = f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          🤖  {PROJECT_NAME} v{PROJECT_VERSION}                       ║
║          Autonomous Multi-Agent AI System                ║
║                                                          ║
║  Agents: Orchestrator · Planner · Researcher · Coder    ║
║          Analyst · Critic · Optimizer · Validator        ║
║          Reporter                                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""


def run_task(task: str) -> dict:
    """Run a single task through the full NEXUS AI pipeline."""
    log.info(f"Task started | task={task}")
    print(BANNER)
    print(f"  Task: {task}\n")
    orchestrator = OrchestratorAgent()
    result       = orchestrator.run(task)
    log.info(
        f"Task complete | task_id={result['task_id']} | "
        f"score={result['score']:.2f} | saved={result['saved_path']}"
    )
    return result


def run_all_example_tasks():
    """Run all 4 example tasks from the Day 5 spec."""
    print(BANNER)
    print("  Running all 4 example tasks...\n")

    results = []
    for i, task in enumerate(EXAMPLE_TASKS, 1):
        print(f"\n{'─'*60}")
        print(f"  TASK {i}/{len(EXAMPLE_TASKS)}: {task}")
        print(f"{'─'*60}")
        log.info(f"Starting example task {i}: {task}")
        orchestrator = OrchestratorAgent()
        result       = orchestrator.run(task)
        results.append(result)
        print(f"\n  ✓ Task {i} complete | score: {result['score']:.0%} | "
              f"saved: {result.get('saved_path', 'N/A')}")

    print(f"\n{'='*60}")
    print(f"  ALL {len(EXAMPLE_TASKS)} TASKS COMPLETE")
    print(f"{'='*60}")
    for i, (task, result) in enumerate(zip(EXAMPLE_TASKS, results), 1):
        print(f"  {i}. {task[:50]:<50} | {result['score']:.0%}")

    return results


def interactive_mode():
    """Interactive REPL for custom tasks."""
    print(BANNER)
    print("  Interactive Mode — type 'exit' to quit, 'examples' to run demos\n")

    while True:
        try:
            task = input("  NEXUS > ").strip()
            if not task:
                continue
            if task.lower() in ["exit", "quit", "q"]:
                print("  Goodbye!")
                break
            if task.lower() == "examples":
                run_all_example_tasks()
                continue
            result = run_task(task)
            print(f"\n  Report saved → {result.get('saved_path', 'N/A')}")
        except KeyboardInterrupt:
            print("\n  Interrupted.")
            break


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NEXUS AI — Autonomous Multi-Agent System")
    parser.add_argument("--task",        type=str, help="Run a specific task")
    parser.add_argument("--examples",    action="store_true", help="Run all 4 example tasks")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--task-id",     type=int, choices=[1,2,3,4],
                        help="Run example task by number (1-4)")
    args = parser.parse_args()

    if args.task:
        run_task(args.task)
    elif args.examples:
        run_all_example_tasks()
    elif args.task_id:
        run_task(EXAMPLE_TASKS[args.task_id - 1])
    elif args.interactive:
        interactive_mode()
    else:
        # Default: run task 1
        run_task(EXAMPLE_TASKS[0])