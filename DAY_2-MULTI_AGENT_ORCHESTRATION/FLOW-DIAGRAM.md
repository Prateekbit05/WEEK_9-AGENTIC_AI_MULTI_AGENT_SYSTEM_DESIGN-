# DAY 2 — Multi-Agent Orchestration
# FLOW-DIAGRAM.md

---

## Exercise Flow (exact spec)

```
User Query
    ↓
Orchestrator (creates steps)
    ↓
Worker Agents (parallel)
    ↓
Reflection Agent (improves answer)
    ↓
Validator (checks for errors)
    ↓
Final Answer
```

---

## Complete System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        USER QUERY                            │
│              e.g. "How does self-attention work?"            │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR / PLANNER AGENT                    │
│                                                              │
│   1. Receive user query                                      │
│   2. Decompose into sub-tasks                                │
│   3. Build DAG — assign task_ids, agent types, dependencies  │
│   4. Look up each agent type in Agent Registry               │
│   5. Set task statuses: READY (workers) / WAITING (rest)     │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │             AGENT REGISTRY                          │   │
│   │   "WORKER"     → WorkerAgent(worker_id=N)           │   │
│   │   "REFLECTION" → ReflectionAgent()                  │   │
│   │   "VALIDATOR"  → ValidatorAgent()                   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Model: llama-3.3-70b-versatile  |  Temp: 0.3              │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────┐
            │    EXECUTION PLAN  (DAG)    │
            │                             │
            │  task_1 ──┐                 │
            │  task_2 ──┼──► task_4 ──► task_5
            │  task_3 ──┘                 │
            │  (READY)    (WAITING)        │
            └─────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│           PARALLEL WORKER AGENTS  (asyncio.gather)           │
│                                                              │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐      │
│  │  WORKER-1     │ │  WORKER-2     │ │  WORKER-3     │      │
│  │  researcher   │ │  analyst      │ │  processor    │      │
│  │               │ │               │ │               │      │
│  │ Theory, math  │ │ Trade-offs,   │ │ Code, impl,   │      │
│  │ derivations,  │ │ hyperparams,  │ │ practical     │      │
│  │ history       │ │ benchmarks    │ │ usage         │      │
│  │               │ │               │ │               │      │
│  │ task_1 READY  │ │ task_2 READY  │ │ task_3 READY  │      │
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘      │
│          │                 │                 │              │
│          └─────────────────┴─────────────────┘              │
└──────────────────────────────────────────────────────────────┘
                              │
                   [All 3 workers complete]
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    REFLECTION AGENT                          │
│                    task_4  WAITING → RUNNING                 │
│                                                              │
│   1. Receive all 3 worker outputs                            │
│   2. Identify best insights from each role                   │
│   3. Fill gaps (math, hyperparameters, code examples)        │
│   4. Remove redundancies and contradictions                  │
│   5. Produce ONE well-structured, complete answer            │
│                                                              │
│   Model: llama-3.3-70b-versatile  |  Temp: 0.6              │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    VALIDATOR AGENT                           │
│                    task_5  WAITING → RUNNING                 │
│                                                              │
│   PASS 1 — Rule-based (fast, no LLM):                        │
│     ✓ Answer non-empty and above minimum length              │
│     ✓ No placeholder text detected                           │
│     ✓ Keyword overlap with query ≥ 15%                       │
│     ✓ Structural quality (paragraphs, headings)              │
│                                                              │
│   PASS 2 — LLM semantic (only if Pass 1 clears):             │
│     ✓ Model rates answer 0–100                               │
│     ✓ Returns issues[] and strengths[] as JSON               │
│     ✓ Only flags genuine errors, not stylistic gaps          │
│     ✓ Score = 40% rule-based + 60% LLM semantic              │
│                                                              │
│   Model: llama-3.1-8b-instant  |  Temp: 0.2                 │
└─────────────────────────────┬────────────────────────────────┘
                              │
                         [If Valid ✓]
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                      FINAL ANSWER                            │
│                                                              │
│   • Synthesised from 3 parallel specialist passes            │
│   • Refined by Reflection Agent                              │
│   • Validated — Quality Score: XX/100                        │
│   • Errors: 0  |  Warnings: 0                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Task Execution DAG

```
                       [USER QUERY]
                            │
                            ▼
                  ┌──────────────────┐
                  │  ORCHESTRATOR    │
                  │  builds DAG      │
                  │  + AgentRegistry │
                  └────────┬─────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
  ┌────────────┐   ┌────────────┐   ┌────────────┐
  │  task_1    │   │  task_2    │   │  task_3    │
  │  WORKER    │   │  WORKER    │   │  WORKER    │
  │ researcher │   │  analyst   │   │ processor  │
  │   READY    │   │   READY    │   │   READY    │
  └──────┬─────┘   └──────┬─────┘   └──────┬─────┘
         │                │                │
         └────────────────┴────────────────┘
                          │
                   [All Complete]
                          │
                          ▼
                  ┌───────────────┐
                  │    task_4     │
                  │  REFLECTION   │
                  │   WAITING     │
                  │  → RUNNING    │
                  │  → COMPLETED  │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │    task_5     │
                  │  VALIDATOR    │
                  │   WAITING     │
                  │  → RUNNING    │
                  │  → COMPLETED  │
                  └───────┬───────┘
                          │
                          ▼
                   [FINAL ANSWER]
```

---

## Agent Characteristics

### 1. Orchestrator / Planner — `/orchestrator/planner.py`

| Property       | Value                                        |
|----------------|----------------------------------------------|
| Role           | Strategic planning + DAG construction        |
| Model          | llama-3.3-70b-versatile                      |
| Temperature    | 0.3 (low — consistent, deterministic plans)  |
| Output         | `ExecutionPlan` — a DAG of `Task` nodes      |

**Responsibilities:**
- Decompose query into `Task` nodes with explicit `dependencies`
- Register agent types in `AgentRegistry` (type string → factory)
- Set `READY` on tier-0 workers, `WAITING` on everything else
- Expose `visualise()` for ASCII execution tree display

---

### 2. Worker Agent — `/agents/worker_agent.py`

| Property       | Value                                         |
|----------------|-----------------------------------------------|
| Count          | 3 simultaneous instances                      |
| Execution      | `asyncio.gather()` — true parallel            |
| Model          | llama-3.1-8b-instant (fast, free tier)        |
| Temperature    | 0.7                                           |
| Max tokens     | 2048                                          |

**Three specialised roles (one per instance):**

| Worker | Role       | Focuses on                                    |
|--------|------------|-----------------------------------------------|
| 1      | researcher | Theory, math, derivations, history            |
| 2      | analyst    | Trade-offs, hyperparameters, benchmarks       |
| 3      | processor  | Working code, implementation, practical usage |

**Why parallel workers?**
Each role covers a different dimension of the query. Running them in
parallel (not sequentially) means the total time is the time of the
slowest single worker, not the sum of all three.

---

### 3. Reflection Agent — `/agents/reflection_agent.py`

| Property       | Value                                        |
|----------------|----------------------------------------------|
| Role           | Answer synthesis and improvement             |
| Model          | llama-3.3-70b-versatile                      |
| Temperature    | 0.6                                          |
| Max tokens     | 4096                                         |
| Input          | 3 worker outputs                             |
| Output         | Single comprehensive synthesised answer      |

**Responsibilities:**
- Combine researcher + analyst + processor outputs
- Explicitly fill gaps: math, hyperparameters, code examples
- Remove redundancies — each point appears only once
- Produce clean, well-structured markdown

---

### 4. Validator Agent — `/agents/validator.py`

| Property       | Value                                        |
|----------------|----------------------------------------------|
| Role           | Quality-assurance gate                       |
| Model          | llama-3.1-8b-instant                         |
| Temperature    | 0.2 (strict, consistent)                     |
| Max tokens     | 768                                          |
| Output         | `ValidationResult` with quality score        |

**Two-pass validation:**

```
Pass 1 — Rule-based (no LLM, always runs)
  ✓ Non-empty, meets minimum length (30 chars)
  ✓ No placeholder / mock text markers
  ✓ Keyword overlap with query ≥ 15%
  ✓ Structural checks (paragraphs, headings, code blocks)

Pass 2 — LLM semantic (only if Pass 1 clears)
  ✓ Model rates answer 0–100
  ✓ Issues = genuine errors only (not stylistic preferences)
  ✓ Final score = 40% rule-based + 60% LLM
```

**Quality tiers:**

| Score  | Tier     | Display   |
|--------|----------|-----------|
| 75–100 | Good     | 🟢 Green  |
| 50–74  | Adequate | 🟡 Yellow |
| 0–49   | Poor     | 🔴 Red    |

---

## Agent Registry Pattern

```python
# Registration (in OrchestratorAgent._build_registry):
registry = AgentRegistry()
registry.register("WORKER",     lambda worker_id=1: WorkerAgent(worker_id=worker_id))
registry.register("REFLECTION", lambda: ReflectionAgent())
registry.register("VALIDATOR",  lambda: ValidatorAgent())

# Usage (in ExecutionEngine):
agent = registry.create("WORKER", worker_id=2)   # → WorkerAgent(worker_id=2)
```

**Benefits of registry pattern:**
- New agent types added without touching the planner
- Factory functions inject config at creation time
- Planner stays decoupled from concrete agent classes
- Easy to swap or mock agents for testing

---

## Delegation Logic (Chain of Command)

```
User
  │ sends query
  ▼
OrchestratorAgent.process({"query": ...})
  │ builds DAG, sets dependencies
  ▼
ExecutionEngine.execute_plan(plan, query)
  │
  ├── Tier 0: asyncio.gather(
  │       worker1.process(task_1),    ← researcher
  │       worker2.process(task_2),    ← analyst
  │       worker3.process(task_3),    ← processor
  │   )                               ← all 3 run in parallel
  │
  ├── Tier 1: reflection.process({
  │       worker_results: [out1, out2, out3]
  │   })
  │
  └── Tier 2: validator.process({
          answer: reflection_output,
          query:  original_query
      })
            │
            └── returns ValidationResult + final_answer → User
```

---

## Memory Architecture

```
┌──────────────────────────────────────┐
│          MEMORY HIERARCHY            │
├──────────────────────────────────────┤
│  Short-term  (per agent, deque=10)   │
│  - task_started / task_completed     │
│  - Current execution context         │
├──────────────────────────────────────┤
│  Task memory  (ExecutionPlan)        │
│  - Full DAG with statuses            │
│  - Per-task results + errors         │
│  - Dependency relationships          │
└──────────────────────────────────────┘
```

---

## Error Handling + Retry

```
         ┌──────────────────┐
         │  Task Executes   │
         └────────┬─────────┘
                  │
          ┌───────┴───────┐
          │               │
        ERROR           SUCCESS
          │               │
          ▼               ▼
   ┌────────────┐   ┌──────────────┐
   │ attempt    │   │  COMPLETED   │
   │ < MAX (3)? │   │  status set  │
   └──────┬─────┘   └──────────────┘
          │
   ┌──────┴──────┐
   │             │
  YES            NO
   │             │
   ▼             ▼
Back-off      FAILED status
1s × attempt  + error message
then retry    propagates up
```

---

## Execution Modes

| Mode       | How                            | Used for                        |
|------------|--------------------------------|---------------------------------|
| Parallel   | `asyncio.gather()` on workers  | All 3 WORKER tasks (Tier 0)     |
| Sequential | await one at a time            | REFLECTION then VALIDATOR       |

Parallel speedup: ~3× vs sequential for worker tier.

---

## Performance Metrics

| Metric               | Typical value          |
|----------------------|------------------------|
| Total execution time | 5–10 seconds           |
| Worker tier time     | = slowest single worker|
| Parallel speedup     | ~3× vs sequential      |
| Quality score        | 75–95 / 100            |
| Errors               | 0                      |
| Warnings             | 0                      |

---

## Project Structure

```
DAY_2-MULTI_AGENT_ORCHESTRATION/
│
├── main.py                        Entry point
├── config.py                      All settings (API key, models, limits)
├── logger.py                      setup_logger() utility
│
├── orchestrator/
│   ├── __init__.py
│   ├── planner.py                 ✅ DELIVERABLE
│   │                              OrchestratorAgent, AgentRegistry,
│   │                              ExecutionPlan, Task, TaskStatus
│   └── executor.py                ExecutionEngine (parallel + retry)
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py              Shared call_llm() + memory (Groq SDK)
│   ├── worker_agent.py            ✅ DELIVERABLE  — parallel workers
│   ├── reflection_agent.py        Synthesis agent
│   └── validator.py               ✅ DELIVERABLE  — two-pass validator
│
├── logs/
│   ├── orchestrator.log
│   └── agents.log
│
└── FLOW-DIAGRAM.md                ✅ DELIVERABLE  — this file
```

---

## Technologies Used

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Async       | `asyncio.gather` — true parallelism |
| DAG         | Custom `ExecutionPlan` + `Task`     |
| Registry    | `AgentRegistry` (factory pattern)   |
| LLM backend | Groq API (free tier)                |
| Workers     | llama-3.1-8b-instant (fast)         |
| Reflection  | llama-3.3-70b-versatile (quality)   |
| Validator   | llama-3.1-8b-instant                |
| UI          | Rich (panels, tables, spinners)     |
| Logging     | Python logging + rotating files     |

---

> **DAY 2 Exercise requirements met:**
> Planner–Executor architecture · DAG-based execution · Task graph generation
> Agent registry pattern · Parallel workers · Execution tree display
> Chain-of-command: Orchestrator → Workers → Reflection → Validator → Answer