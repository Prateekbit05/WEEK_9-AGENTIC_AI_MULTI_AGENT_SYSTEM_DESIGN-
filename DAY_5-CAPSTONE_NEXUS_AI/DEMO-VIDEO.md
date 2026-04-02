# DEMO-VIDEO.md
## NEXUS AI — Demo Script

---

## Setup (30 seconds)

```bash
cd DAY_5-CAPSTONE_NEXUS_AI
source venv/bin/activate
export PYTHONPATH=$(pwd)

# Show structure
tree -I "venv|__pycache__|*.pyc" -L 3
```

---

## Demo 1 — Single Task (2 minutes)

```bash
# Task 1: Healthcare startup — watch 9 agents execute live
python3 -m nexus_ai.main --task-id 1
```

Point out:
- NEXUS AI banner + 9 agent names
- Each step [1/8] through [8/8] printing live
- CriticAgent score appearing (98%)
- OptimizerAgent showing 0 loops needed
- ValidatorAgent: 5/5 checks PASSED
- Report saved path + trace path

---

## Demo 2 — All 4 Tasks (3 minutes)

```bash
python3 -m nexus_ai.main --examples
```

Show the final summary table at the bottom:
```
1. Plan a startup in AI for healthcare          | 98%
2. Generate backend architecture for scalable   | 98%
3. Analyze CSV and create business strategy     | 98%
4. Design a RAG pipeline for 50k documents      | 98%
```

---

## Demo 3 — Custom Task (1 minute)

```bash
python3 -m nexus_ai.main --task "Design a fraud detection system for fintech"
```

Show that NEXUS AI adapts to any task — selects appropriate template, generates domain-specific strategy and risk matrix.

---

## Demo 4 — Generated Report (1 minute)

```bash
# Show latest report
ls -t output/ | head -1 | xargs -I{} cat output/{}
```

Scroll through: research findings, code output, business strategy, risk matrix, validation, execution plan.

---

## Demo 5 — Execution Trace (30 seconds)

```bash
ls -t logs/*_trace.json | head -1 | xargs python3 -m json.tool | head -50
```

Show: task_id, started_at, all steps with agent + duration_ms + output preview.

---

## Demo 6 — Tests (30 seconds)

```bash
python3 -m pytest tests/ -v --tb=short 2>&1 | tail -20
```

Show: 64 passed in 4.39s

---

## Demo 7 — Production Dashboard (2 minutes)

```bash
python3 dashboard.py
```

Open http://localhost:5000 in browser. Show:
- Dark theme, hexagonal NEXUS logo, live clock
- 9 agent dots on sidebar (all idle)
- 8-step pipeline bar
- Select example task 1 from dropdown → click Run
- Watch: agent dots turn amber → green one by one
- Pipeline steps light up in sequence
- Trace log fills with live events
- Score gauge updates to 98%
- Report appears in Generated Reports section

---

## Key Points to Highlight

1. Zero human intervention from task submission to report save
2. Self-reflection: CriticAgent objectively scores its own pipeline output
3. Self-improvement: OptimizerAgent would loop if score were below threshold
4. All 5 validation checks passing independently
5. Every action traced with agent name, output preview, and timing
6. Dashboard streams live via SSE — no polling, no page refresh
7. 64 tests verify every component independently

## DEMO VIDEO_COMMANDS-PART-2

# 🎬 DEMO-VIDEO.md
## NEXUS AI — Demo Script

---

## Setup (30 seconds)

```bash
cd DAY_5-CAPSTONE_NEXUS_AI
source venv/bin/activate
export PYTHONPATH=$(pwd)

# Verify Ollama is running and models are ready
python setup_ollama.py

# Show structure
tree -I "venv|__pycache__|*.pyc" -L 3
```

---

## Demo 1 — Single Task (2 minutes)

```bash
# Task 1: Healthcare startup — watch 9 agents + 3 LLMs execute live
python3 -m nexus_ai.main --task-id 1
```

Point out:
- NEXUS AI banner + model assignment table (phi3/qwen2/tinyllama per agent)
- Each step [1/8] through [8/8] printing live with model name
- CriticAgent score appearing (98%)
- OptimizerAgent showing 0 loops needed
- ValidatorAgent: 5/5 checks PASSED + tinyllama sanity check
- Report saved path + trace path

---

## Demo 2 — All 4 Tasks (3 minutes)

```bash
python3 -m nexus_ai.main --examples
```

Show the final summary table at the bottom:
```
1. Plan a startup in AI for healthcare          | 98%
2. Generate backend architecture for scalable   | 98%
3. Analyze CSV and create business strategy     | 98%
4. Design a RAG pipeline for 50k documents      | 98%
```

---

## Demo 3 — Custom Task (1 minute)

```bash
python3 -m nexus_ai.main --task "Design a fraud detection system for fintech"
```

Show that NEXUS AI adapts to any task — selects appropriate template, generates domain-specific strategy and risk matrix, routes to the right LLM per agent.

---

## Demo 4 — Generated Report (1 minute)

```bash
# Show latest report
ls -t output/ | head -1 | xargs -I{} cat output/{}
```

Scroll through: LLM executive summary (qwen2:1.5b), research findings + LLM synthesis, business strategy + LLM interpretation, LLM architecture insights, LLM deep critique, model usage section at the bottom.

---

## Demo 5 — Execution Trace (30 seconds)

```bash
ls -t logs/*_trace.json | head -1 | xargs python3 -m json.tool | head -50
```

Show: task_id, started_at, all steps with agent + duration_ms + output preview.

---

## Demo 6 — Tests (30 seconds)

```bash
python3 -m pytest tests/ -v --tb=short 2>&1 | tail -25
```

Show: 99 passed — including TestOllamaModelManager (18 tests) and TestBaseAgentLLM (6 tests).

---

## Demo 7 — Production Dashboard (2 minutes)

```bash
python3 dashboard.py
```

Open http://localhost:5000 in browser. Show:
- Dark theme, hexagonal NEXUS logo, live clock
- **Ollama status pill** in topbar (green = online)
- **Ollama models card** — 3 model tiles with pulled/missing status:
  - phi3:mini (3.8B) — Orchestrator · Planner · Coder · Critic
  - qwen2:1.5b (1.5B) — Researcher · Analyst · Optimizer · Reporter
  - tinyllama (1.1B) — Validator
- 9 agent rows on sidebar — each with **colour-coded model badge** (purple phi3 / teal qwen2 / amber tiny)
- 8-step pipeline bar — each step shows model name underneath
- Select example task 1 from dropdown → click Run
- Watch: agent dots turn amber → green one by one
- Trace log: each event shows `[phi3:mini] Starting…` or `[qwen2:1.5b] Starting…`
- Pipeline steps light up in sequence with model names
- Score gauge updates to 98%
- Report appears in Generated Reports section

---

## Key Points to Highlight

1. Zero human intervention from task submission to report save
2. **3 local LLMs running on CPU** — no API keys, no internet, fully offline
3. **Hybrid mode** — templates guarantee stability, LLMs add intelligence
4. **Smart model routing** — phi3:mini for reasoning, qwen2:1.5b for speed, tinyllama for binary checks
5. Self-reflection: CriticAgent + phi3:mini jointly score the pipeline output
6. Self-improvement: OptimizerAgent + qwen2:1.5b rewrite weak sections
7. All 5 validation checks + tinyllama sanity check passing independently
8. Every action traced with agent name, output preview, and timing
9. Dashboard streams live via SSE with per-agent model visibility
10. 99 tests verify every component including model routing and fallback
