# Week 9 — Agentic AI & Multi-Agent System Design
> **AutoGen + Open Models + Orchestration + Memory + Planning + Tool Use**
> A complete week of building autonomous AI systems — from single agents to a full 9-agent production system (NEXUS AI).

---

## 📌 Overview

This week transforms engineers from prompt users into **AI System Engineers**. Starting from agent fundamentals and progressing through orchestration, tool use, memory systems, and finally a full autonomous multi-agent capstone — NEXUS AI.

### What Was Built This Week
```
Day 1 → 3 Single Agents (Research, Summarizer, Answer)
Day 2 → 4-Agent Orchestration (Planner → Workers → Validator)
Day 3 → 3 Tool-Calling Agents (Code, DB, File)
Day 4 → 3-Layer Memory System (Session + Vector + Long-term)
Day 5 → NEXUS AI (9-Agent Autonomous System — Capstone)
```

---

## 🗂️ Repository Structure

```
WEEK_9-AGENTIC_AI_MULTI_AGENT_SYSTEM_DESIGN/
├── DAY_1-AGENT_FOUNDATIONS_MESSAGE_BASED_COMMUNICATION/
│   └── Screenshots/
├── DAY_2-MULTI_AGENT_ORCHESTRATION/
│   └── Screenshots/
├── DAY_3-TOOL_CALLING_AGENTS/
│   └── Screenshots/
├── DAY_4-MEMORY_SYSTEMS/
│   └── Screenshots/
└── DAY_5-CAPSTONE_NEXUS_AI/
    └── Screenshots/
```

---

## 📅 Day-by-Day Breakdown

---

### Day 1 — Agent Foundations + Message-Based Communication

**Goal:** Build 3 single agents with strict role isolation and message-passing protocol.

**Agent Pipeline:**
```
User → Research Agent → Info
     → Summarizer Agent → Summary
     → Answer Agent → Final Answer
```

**Key Files:**
| File | Description |
|---|---|
| `agents/research_agent.py` | Gathers and structures raw information with ReAct pattern |
| `agents/summarizer_agent.py` | Condenses research findings into clean summaries |
| `agents/answer_agent.py` | Formulates final user-facing response from summary |
| `AGENT-FUNDAMENTALS.md` | Agent architecture and message protocol documentation |

**Deliverables Checklist:**
- [x] Research Agent with ReAct pattern
- [x] Summarizer Agent with role isolation
- [x] Answer Agent with grounded response generation
- [x] Agent fundamentals documented

#### 📸 Screenshots

![Day 1 - Agent Pipeline 1](DAY_1-AGENT_FOUNDATIONS_MESSAGE_BASED_COMMUNICATION/Screenshots/day1_agent_pipeline.png01.png)
![Day 1 - Agent Pipeline 2](DAY_1-AGENT_FOUNDATIONS_MESSAGE_BASED_COMMUNICATION/Screenshots/day1_agent_pipeline.png02.png)
![Day 1 - Agent Pipeline 3](DAY_1-AGENT_FOUNDATIONS_MESSAGE_BASED_COMMUNICATION/Screenshots/day1_agent_pipeline.png03.png)
![Day 1 - Agent Pipeline 4](DAY_1-AGENT_FOUNDATIONS_MESSAGE_BASED_COMMUNICATION/Screenshots/day1_agent_pipeline.png04.png)
![Day 1 - Agent Pipeline 5](DAY_1-AGENT_FOUNDATIONS_MESSAGE_BASED_COMMUNICATION/Screenshots/day1_agent_pipeline.png05.png)
![Day 1 - Agent Pipeline 6](DAY_1-AGENT_FOUNDATIONS_MESSAGE_BASED_COMMUNICATION/Screenshots/day1_agent_pipeline.png06.png)
![Day 1 - Agent Pipeline 7](DAY_1-AGENT_FOUNDATIONS_MESSAGE_BASED_COMMUNICATION/Screenshots/day1_agent_pipeline.png07.png)
![Day 1 - Agent Pipeline 8](DAY_1-AGENT_FOUNDATIONS_MESSAGE_BASED_COMMUNICATION/Screenshots/day1_agent_pipeline.png08.png)

---

### Day 2 — Multi-Agent Orchestration (Planner → Workers → Validator)

**Goal:** Build a 4-agent hierarchy with DAG-based task execution and parallel workers.

**Execution Flow:**
```
User Query
↓
Orchestrator (creates steps)
↓
Worker Agents (parallel execution)
↓
Reflection Agent (improves answer)
↓
Validator (checks for errors)
↓
Final Answer
```

**Key Files:**
| File | Description |
|---|---|
| `orchestrator/planner.py` | Decomposes tasks into DAG execution steps |
| `agents/worker_agent.py` | Executes tasks in parallel across multiple instances |
| `agents/validator.py` | Final error and quality check before delivery |
| `FLOW-DIAGRAM.md` | Full orchestration flow and architecture diagram |

**Deliverables Checklist:**
- [x] Orchestrator / Planner with DAG task graph
- [x] Worker Agent with parallel execution support
- [x] Reflection Agent for answer improvement
- [x] Validator Agent for error checking
- [x] Execution tree visible in output

#### 📸 Screenshots

![Day 2 - Orchestration Flow 1](DAY_2-MULTI_AGENT_ORCHESTRATION/Screenshots/day2_orchestration_flow.png1.png)
![Day 2 - Orchestration Flow 2](DAY_2-MULTI_AGENT_ORCHESTRATION/Screenshots/day2_orchestration_flow.png2.png)
![Day 2 - Orchestration Flow 3](DAY_2-MULTI_AGENT_ORCHESTRATION/Screenshots/day2_orchestration_flow.png3.png)
![Day 2 - Orchestration Flow 4](DAY_2-MULTI_AGENT_ORCHESTRATION/Screenshots/day2_orchestration_flow.png4.png)
![Day 2 - Orchestration Flow 5](DAY_2-MULTI_AGENT_ORCHESTRATION/Screenshots/day2_orchestration_flow.png5.png)

---

### Day 3 — Tool-Calling Agents (Code, Files, Database, Search)

**Goal:** Build 3 agents that use real tools — Python execution, SQLite queries, and file I/O.

**Example Task:**
```
User: "Analyze sales.csv and generate top 5 insights"
→ Orchestrator assigns File + Code + Analysis Agents
→ File Agent reads CSV
→ Code Agent runs analysis
→ Combined final answer delivered
```

**Key Files:**
| File | Description |
|---|---|
| `tools/code_executor.py` | Executes Python code safely in isolated subprocess |
| `tools/db_agent.py` | Runs natural language → SQL queries on SQLite |
| `tools/file_agent.py` | Reads and writes .txt and .csv files |
| `TOOL-CHAIN.md` | Tool-calling architecture and pipeline documentation |

**Deliverables Checklist:**
- [x] Code Agent with Python execution tool
- [x] DB Agent with SQLite + SQL tool
- [x] File Agent with read/write .txt and .csv tool
- [x] Tool chain documented

#### 📸 Screenshots

![Day 3 - Tool Calling 1](DAY_3-TOOL_CALLING_AGENTS/Screenshots/day3_tool_calling.png1.png)
![Day 3 - Tool Calling 2](DAY_3-TOOL_CALLING_AGENTS/Screenshots/day3_tool_calling.png2.png)
![Day 3 - Tool Calling 3](DAY_3-TOOL_CALLING_AGENTS/Screenshots/day3_tool_calling.png3.png)
![Day 3 - Tool Calling 4](DAY_3-TOOL_CALLING_AGENTS/Screenshots/day3_tool_calling.png4.png)
![Day 3 - Tool Calling 5](DAY_3-TOOL_CALLING_AGENTS/Screenshots/day3_tool_calling.png5.png)
![Day 3 - Tool Calling 6](DAY_3-TOOL_CALLING_AGENTS/Screenshots/day3_tool_calling.png6.png)
![Day 3 - Tool Calling 7](DAY_3-TOOL_CALLING_AGENTS/Screenshots/day3_tool_calling.png7.png)

---

### Day 4 — Memory Systems (Short-term + Long-term + Vector)

**Goal:** Implement a 3-layer agent memory system with similarity-based recall.

**Memory Query Flow:**
```
New Query
→ Search vector memory (FAISS)
→ Fetch similar past context
→ Inject into prompt
→ Generate with full context
→ Store result back to memory
```

**Key Files:**
| File | Description |
|---|---|
| `memory/session_memory.py` | Short-term window memory (last 10 messages, in-memory) |
| `memory/vector_store.py` | FAISS vector memory for semantic similarity recall |
| `memory/long_term.db` | SQLite persistent memory across sessions |
| `MEMORY-SYSTEM.md` | Full memory architecture documentation |

**Memory Layers:**
| Layer | Storage | Scope | Use Case |
|---|---|---|---|
| Short-term | In-memory buffer | Current session | Conversation continuity |
| Long-term | SQLite DB | Persistent | Cross-session facts |
| Vector | FAISS index | Semantic | Similarity-based recall |

**Deliverables Checklist:**
- [x] Session memory with configurable window size
- [x] FAISS vector store for semantic recall
- [x] SQLite long-term persistent memory
- [x] Memory system documented

#### 📸 Screenshots

![Day 4 - Memory Recall 1](DAY_4-MEMORY_SYSTEMS/Screenshots/day4_memory_recall.png1.png)
![Day 4 - Memory Recall 2](DAY_4-MEMORY_SYSTEMS/Screenshots/day4_memory_recall.png2.png)
![Day 4 - Memory Recall 3](DAY_4-MEMORY_SYSTEMS/Screenshots/day4_memory_recall.png3.png)
![Day 4 - Memory Recall 4](DAY_4-MEMORY_SYSTEMS/Screenshots/day4_memory_recall.png4.png)
![Day 4 - Memory Recall 5](DAY_4-MEMORY_SYSTEMS/Screenshots/day4_memory_recall.png5.png)
![Day 4 - Memory Recall 6](DAY_4-MEMORY_SYSTEMS/Screenshots/day4_memory_recall.png6.png)
![Day 4 - Memory Recall 7](DAY_4-MEMORY_SYSTEMS/Screenshots/day4_memory_recall.png7.png)

---

### Day 5 — Capstone: NEXUS AI (Autonomous Multi-Agent System)

**Goal:** Build a fully autonomous 9-agent system that solves complex multi-step tasks end-to-end.

**Agent Roster:**
| Agent | Role |
|---|---|
| Orchestrator | Master controller and task router |
| Planner | Decomposes task into DAG execution steps |
| Researcher | Gathers context from memory and tools |
| Coder | Generates Python/SQL/config code |
| Analyst | Processes CSV, runs statistical analysis |
| Critic | Reviews output quality and flags gaps |
| Optimizer | Refines based on Critic feedback |
| Validator | Final accuracy and format check |
| Reporter | Formats and delivers final output |

**Benchmark Tasks Solved:**
```
1. "Plan a startup in AI for healthcare"          → Score: 98%
2. "Generate backend architecture for scalable app"
3. "Analyze CSV and create business strategy"
4. "Design a RAG pipeline for 50k documents"
```

**Key Files:**
| File | Description |
|---|---|
| `nexus_ai/main.py` | System entry point — bootstraps all 9 agents |
| `nexus_ai/config.py` | Centralized system configuration |
| `README.md` | Full NEXUS AI documentation |
| `ARCHITECTURE.md` | System architecture and agent flow diagrams |
| `FINAL-REPORT.md` | Capstone summary and benchmark results |

**Deliverables Checklist:**
- [x] 9-agent autonomous system
- [x] Tool use (code, CSV, file, search)
- [x] 3-layer memory (session + vector + long-term)
- [x] Self-reflection and self-improvement loop
- [x] Multi-step planning with DAG execution
- [x] Structured logging and execution tracing
- [x] Failure recovery and retry logic
- [x] Streamlit dashboard
- [x] 4 benchmark tasks solved

#### 📸 Screenshots — Terminal Run
![Day 5 - Terminal Run](DAY_5-CAPSTONE_NEXUS_AI/Screenshots/terminal_run.png)

#### 📸 Screenshots — Streamlit Dashboard
![Day 5 - Dashboard 1](DAY_5-CAPSTONE_NEXUS_AI/Screenshots/dashboard_1.png)
![Day 5 - Dashboard 2](DAY_5-CAPSTONE_NEXUS_AI/Screenshots/dashboard_2.png)

#### 📸 Screenshots — Generated Reports
![Day 5 - Output Report](DAY_5-CAPSTONE_NEXUS_AI/Screenshots/output_report.png)
![Day 5 - Output Report 2](DAY_5-CAPSTONE_NEXUS_AI/Screenshots/output_report_2.png)
![Day 5 - Output Report 3](DAY_5-CAPSTONE_NEXUS_AI/Screenshots/output_report_3.png)
![Day 5 - Output Report 4](DAY_5-CAPSTONE_NEXUS_AI/Screenshots/output_report_4.png)

#### 📸 Screenshots — Execution Trace
![Day 5 - Trace Log](DAY_5-CAPSTONE_NEXUS_AI/Screenshots/trace_log.png)

---

## 🧠 Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | AutoGen (Microsoft) |
| LLM — Orchestrator/Planner/Coder/Critic | phi3:mini (3.8B) |
| LLM — Researcher/Analyst/Optimizer/Reporter | qwen2:1.5b (1.5B) |
| LLM — Validator | tinyllama (1.1B) |
| Vector Memory | FAISS |
| Long-term Memory | SQLite |
| API Server | FastAPI |
| Dashboard | Streamlit |
| Model Server | Ollama (fully local) |

---

## 🔑 Core Concepts Covered

| Concept | Implemented In |
|---|---|
| ReAct pattern (Reason + Act) | Day 1 — all 3 agents |
| Message passing protocol | Day 1 — agent pipeline |
| DAG-based task execution | Day 2 — orchestrator |
| Agent registry pattern | Day 2 — planner |
| Python tool calling | Day 3 — code executor |
| SQL tool calling | Day 3 — DB agent |
| Episodic vs semantic memory | Day 4 — memory system |
| Blackboard memory | Day 4 — vector store |
| Chain-of-thought isolation | Day 5 — NEXUS AI |
| Swarm orchestration | Day 5 — NEXUS AI |
| Self-reflection loop | Day 5 — Critic + Optimizer |
| Failure recovery | Day 5 — NEXUS AI |

---

## ✅ Week 9 Completion Criteria

| Capability | Status |
|---|---|
| Multi-agent system | ✅ |
| Orchestrator | ✅ |
| Tool calling (code, DB, file) | ✅ |
| Memory (session + vector + long-term) | ✅ |
| Self-reflection loop | ✅ |
| Multi-step planning | ✅ |
| Parallel worker execution | ✅ |
| No paid APIs (fully local) | ✅ |
| Fully local LLMs via Ollama | ✅ |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone git@github.com:Prateekbit05/WEEK_9-AGENTIC_AI_MULTI_AGENT_SYSTEM_DESIGN-.git
cd WEEK_9-AGENTIC_AI_MULTI_AGENT_SYSTEM_DESIGN-

# Start Ollama and pull models
ollama serve
ollama pull phi3:mini
ollama pull qwen2:1.5b
ollama pull tinyllama

# Run NEXUS AI capstone
cd DAY_5-CAPSTONE_NEXUS_AI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python nexus_ai/main.py --task "Plan a startup in AI for healthcare"

# Launch dashboard
streamlit run dashboard.py
```

---
