# TOOL-CHAIN.md
## Day 3 — Tool-Calling Agents (Code, Files, Database, Search)
### Agentic AI Applications 2025 Analysis System

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Tool Chain Flow](#tool-chain-flow)
4. [Tool Reference](#tool-reference)
   - [CodeExecutorTool](#1-codeexecutortool)
   - [DBAgentTool](#2-dbagentool)
   - [FileAgentTool](#3-fileagenttool)
   - [SearchAgentTool](#4-searchagenttool)
5. [Agent Reference](#agent-reference)
   - [OrchestratorAgent](#orchestratoragent)
   - [ToolAgent](#toolagent)
6. [Exercise Walkthrough](#exercise-walkthrough)
7. [Memory System](#memory-system)
8. [Logging System](#logging-system)
9. [File Structure](#file-structure)
10. [Running the System](#running-the-system)
11. [Testing](#testing)
12. [Topic Coverage Map](#topic-coverage-map)

---

## Overview

This project implements a **multi-agent tool-calling system** built around a real dataset:
`Large_Agentic_AI_Applications_2025.csv` — 10,000+ records of AI agent deployments
across industries, regions, and technology stacks.

**Three specialised tool agents** collaborate under a central **OrchestratorAgent**
to answer complex analytical queries that no single tool could handle alone.

```
User Query
    │
    ▼
OrchestratorAgent
    ├── FileAgentTool    (read + summarise CSV, write reports)
    ├── DBAgentTool      (SQLite queries, structured stats)
    ├── CodeExecutorTool (pandas analysis, shell commands)
    └── SearchAgentTool  (local search engine, content ranking)
```

---

## Architecture

```
DAY_3-TOOL_CALLING_AGENTS/
├── tools/
│   ├── base_tool.py          ← Abstract interface all tools implement
│   ├── code_executor.py      ← Tool 1: Python exec + shell subprocess
│   ├── db_agent.py           ← Tool 2: SQLite / CSV querying
│   ├── file_agent.py         ← Tool 3: Read/write .txt .csv .json
│   └── search_agent.py       ← Tool 4: Local search engine
│
├── agents/
│   ├── base_agent.py         ← Abstract agent base class
│   ├── tool_agent.py         ← Manages + executes tools by name
│   └── orchestrator_agent.py ← Delegates subtasks to all three agents
│
├── memory/
│   └── tool_memory.py        ← Records every tool call with timing
│
├── logger.py                 ← Centralised logging (file + console)
├── config.py                 ← Config constants for each tool
├── main.py                   ← Demo runner (4 demos + orchestrator)
└── TOOL-CHAIN.md             ← This file
```

### Key Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Unified execute()** | Every tool exposes a single `execute(**kwargs)` entry point |
| **Tool Schema** | Each tool declares a JSON schema (function-calling format) |
| **Separation of concerns** | Tools only do I/O; agents handle coordination logic |
| **Fail-safe returns** | Every method returns `{"success": bool, ...}` — never raises |
| **Composable** | Tools can be used standalone or chained through the orchestrator |

---

## Tool Chain Flow

### Exercise Scenario
> **User:** "Analyze `Large_Agentic_AI_Applications_2025.csv` and generate top 5 insights"

```
┌─────────────────────────────────────────────────────────────────┐
│                      OrchestratorAgent.run()                    │
│                                                                  │
│  Step 1 ── FileAgentTool.summarize_csv()                        │
│             → total_rows, industries, application_areas,         │
│               top_tech_stacks, regions, deployment_years         │
│             → Produces Insights #1 – #4                         │
│                                                                  │
│  Step 2 ── DBAgentTool SQL queries                              │
│             → deployments_by_year()    → Insight #5 (peak year) │
│             → industry_area_breakdown()→ Insight #6 (top combo) │
│             → agents_by_year_and_region()→ Insight #7           │
│             → custom SQL (region diversity) → Insight #8        │
│                                                                  │
│  Step 3 ── CodeExecutorTool.analyze_dataset()                   │
│             → pandas JSON analysis   → Insight #9 (year counts) │
│             → run_python() diversity → Insight #10              │
│                                                                  │
│  Step 4 ── FileAgentTool.write_report() / write_json()         │
│             → output/agentic_ai_insights.txt                    │
│             → output/agentic_ai_insights.json                   │
│             → output/agentic_ai_insights.csv                    │
│                                                                  │
│  Returns: List[str]  (all insights, top 5 printed to console)   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
Large_Agentic_AI_Applications_2025.csv
          │
          ├──► FileAgentTool ──► summarize_csv() ──► dict of counts
          │
          ├──► DBAgentTool ────► load_csv() ──► SQLite DB
          │                           │
          │                           └──► SQL queries ──► list of rows
          │
          ├──► CodeExecutorTool ──► exec(pandas code) ──► JSON string
          │
          └──► SearchAgentTool ──► CSV content search ──► ranked rows

All results ──► OrchestratorAgent ──► combined insights list
                                              │
                                    FileAgentTool.write_*()
                                              │
                              output/ (.txt + .json + .csv)
```

---

## Tool Reference

### 1. CodeExecutorTool
**File:** `tools/code_executor.py`
**Topics:** Python tool calling, Shell command tools

Executes arbitrary Python code strings and shell commands. Used by the
orchestrator's CodeAgent step to run pandas analysis dynamically.

#### Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `run_python(code)` | Execute Python via `exec()`, capture stdout | `{status, output, error}` |
| `run_shell(command, timeout)` | Run shell via `subprocess.run()` | `{status, stdout, stderr, return_code}` |
| `execute(python_code, shell_command)` | Unified entry point | delegates to above |
| `analyze_dataset(csv_path)` | Full pandas JSON analysis | `{status, output}` |
| `top_5_insights(csv_path)` | Prints 5 human-readable insights | `{status, output}` |
| `industry_area_crosstab(csv_path)` | Cross-tab pivot table | `{status, output}` |
| `year_region_trend(csv_path)` | Grouped trend table | `{status, output}` |
| `shell_file_info(csv_path)` | `wc -l`, `du -sh`, `head -1`, `tail -3` | `dict of shell results` |

#### Tool Schema
```json
{
  "name": "code_executor",
  "description": "Run Python code or a shell command",
  "parameters": {
    "type": "object",
    "properties": {
      "python_code":   { "type": "string" },
      "shell_command": { "type": "string" }
    }
  }
}
```

#### Example
```python
tool = CodeExecutorTool()

# Python execution
r = tool.run_python("import pandas as pd; df = pd.read_csv('data/...csv'); print(len(df))")
print(r["output"])   # → "10000"

# Shell command
r = tool.run_shell("wc -l data/Large_Agentic_AI_Applications_2025.csv")
print(r["stdout"])   # → "10001 data/..."
```

---

### 2. DBAgentTool
**File:** `tools/db_agent.py`
**Topics:** SQLite / CSV querying

Loads the CSV into a SQLite database and exposes pre-built and custom SQL queries.
Creates three summary tables on load for fast lookups.

#### Methods

| Method | SQL Operation | Returns |
|--------|--------------|---------|
| `load_csv(csv_path)` | `CREATE TABLE agentic_applications` + 3 summary tables | `{success, rows, tables}` |
| `connect() / close()` | Manage SQLite connection | self / None |
| `execute(sql)` | Any SQL statement | `{success, data, count}` |
| `top_industries(limit)` | `GROUP BY Industry ORDER BY count DESC` | list of rows |
| `top_application_areas(limit)` | `GROUP BY "Application Area"` | list of rows |
| `deployments_by_year()` | `GROUP BY "Deployment Year"` | list of rows |
| `deployments_by_region()` | `GROUP BY "Geographical Region"` | list of rows |
| `top_tech_stacks(limit)` | `GROUP BY "Technology Stack"` | list of rows |
| `industry_area_breakdown(limit)` | Two-column GROUP BY | list of rows |
| `agents_by_year_and_region()` | Two-column GROUP BY + ORDER | list of rows |
| `search_by_task(keyword, limit)` | `LIKE '%keyword%'` on Task Description | list of rows |
| `filter_by_industry(industry, limit)` | `WHERE Industry = ?` | list of rows |
| `filter_by_year(year, limit)` | `WHERE "Deployment Year" = ?` | list of rows |
| `stack_by_industry()` | Industry + Stack GROUP BY | list of rows |

#### Tables Created on `load_csv()`

| Table | Contents |
|-------|----------|
| `agentic_applications` | Full CSV (all 8 columns, all rows) |
| `industry_summary` | `Industry, agent_count` |
| `area_summary` | `Application Area, agent_count` |
| `stack_summary` | `Technology Stack, usage_count` |

#### Example
```python
tool = DBAgentTool(db_path="data/agentic_ai.db")
tool.load_csv("data/Large_Agentic_AI_Applications_2025.csv")
tool.connect()

# Pre-built query
r = tool.top_industries(5)
for row in r["data"]:
    print(row["Industry"], row["agent_count"])

# Custom SQL
r = tool.execute("""
    SELECT "Geographical Region", COUNT(DISTINCT Industry) as unique_industries
    FROM agentic_applications
    GROUP BY "Geographical Region"
    ORDER BY unique_industries DESC
    LIMIT 3
""")

tool.close()
```

---

### 3. FileAgentTool
**File:** `tools/file_agent.py`
**Topics:** File reading/writing, Local search engine

Handles all file I/O and provides a local filesystem search engine.
Auto-detects file type from extension for both reads and writes.

#### Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `read_file(filepath)` | Auto-detect type and read | type-specific dict |
| `read_csv(filepath)` | pandas read, return first 10 rows + meta | `{success, rows, columns, data, dtypes}` |
| `read_txt(filepath)` | Read plain text | `{success, content, lines}` |
| `read_json(filepath)` | Parse JSON file | `{success, data}` |
| `summarize_csv(filepath)` | Deep summary — counts per column | `{success, total_rows, industries, ...}` |
| `write_file(filepath, content)` | Auto-detect type and write | `{success, path}` |
| `write_txt(filename, content)` | Write to `output/` | `{success, path, bytes}` |
| `write_csv(filename, data)` | Write list-of-dicts to CSV | `{success, path, rows}` |
| `write_json(filename, data)` | JSON dump with indent=2 | `{success, path}` |
| `write_report(filename, insights, title)` | Numbered insights report | `{success, path}` |
| `search_files(keyword, search_dir)` | Find files by name keyword | `{success, matches, count}` |
| `search_csv_content(filepath, keyword)` | Full-text search in CSV | `{success, matches, data}` |
| `search_by_column(filepath, column, value)` | Filter CSV by column value | `{success, matches, data}` |
| `list_directory(directory)` | Recursive file index | `{success, files, count}` |
| `execute(action, ...)` | Unified dispatcher | delegates |

#### Example
```python
tool = FileAgentTool(output_dir="output")

# Read
r = tool.read_csv("data/Large_Agentic_AI_Applications_2025.csv")
print(f"{r['rows']} rows, columns: {r['columns']}")

# Summarise
s = tool.summarize_csv("data/Large_Agentic_AI_Applications_2025.csv")
print(f"Industries: {s['industries']}")

# Write report
tool.write_report("report.txt", ["Insight 1", "Insight 2"], title="MY REPORT")

# Search files
r = tool.search_files("agentic", search_dir=".")
print(f"Found {r['count']} files")

# Search CSV content
r = tool.search_csv_content("data/...csv", "fraud")
print(f"{r['matches']} rows match 'fraud'")
```

---

### 4. SearchAgentTool
**File:** `tools/search_agent.py`
**Topics:** Local search engine, content ranking

Provides multiple search modalities over the local filesystem and CSV content.
Includes a relevance-ranking engine.

#### Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `search_files(keyword, search_dir)` | Find files by name keyword | `{success, matches, count}` |
| `search_csv_content(filepath, keyword, columns, top_n)` | Full-text CSV search | `{success, matches, data}` |
| `search_column_values(filepath, column, keyword, exact)` | Specific-column search | `{success, matches, data}` |
| `search_all_text_files(keyword, search_dir)` | grep-like across .py/.txt/.md | `{success, hits, count}` |
| `build_index(search_dir)` | Walk tree, build file index | `{success, total, extensions, index}` |
| `query_index(keyword)` | Search pre-built index | `List[Dict]` |
| `rank_results(filepath, keyword, top_n)` | Rank CSV rows by keyword frequency | `{success, data, total_matches}` |
| `list_unique_values(filepath, column)` | All unique values in a column | `{success, values, count}` |
| `execute(action, ...)` | Unified dispatcher | delegates |

#### Example
```python
tool = SearchAgentTool()

# Find files
r = tool.search_files("agentic", search_dir=".")

# Grep-like search
r = tool.search_all_text_files("execute", search_dir="tools")
print(f"{r['count']} lines match across {r['files_with_hits']} files")

# Build index
r = tool.build_index(".")
files = tool.query_index("csv")   # → all .csv files in index

# Rank by relevance
r = tool.rank_results("data/...csv", "healthcare", top_n=5)
for row in r["data"]:
    print(row["relevance_score"], row["Industry"])
```

---

## Agent Reference

### OrchestratorAgent
**File:** `agents/orchestrator_agent.py`

Central coordinator. On startup it loads the CSV into SQLite, connects all three
sub-agents, and exposes a single `run(user_query)` method.

```python
class OrchestratorAgent:
    file_agent : FileAgentTool
    db_agent   : DBAgentTool
    code_agent : CodeExecutorTool

    def run(self, user_query: str) -> List[str]:
        # Step 1 — FileAgent: read + summarise
        # Step 2 — DBAgent:   SQL queries
        # Step 3 — CodeAgent: pandas analysis
        # Step 4 — FileAgent: write .txt + .json + .csv reports
        return insights   # List[str]
```

**Usage:**
```python
orch = OrchestratorAgent()
insights = orch.run("Analyze sales.csv and generate top 5 insights")
for i, ins in enumerate(insights[:5], 1):
    print(f"{i}. {ins}")
```

---

### ToolAgent
**File:** `agents/tool_agent.py`

Lower-level agent that manages a registry of tools and can execute them
by name, optionally chaining output from one step as input to the next.

```python
agent = ToolAgent()

# Execute single tool
result = agent.execute_tool("code_executor", python_code="print('hi')")

# Execute a tool chain
result = agent.process_task("Analyse data", [
    {"tool": "file_agent",    "params": {"action": "read", "filepath": "data/...csv"}},
    {"tool": "code_executor", "params": {"python_code": "..."}},
])
```

Context variables (prefixed with `$`) are resolved automatically between steps:
```python
{"params": {"data": "$step_1_output"}}   # ← injects output of step 1
```

---

## Exercise Walkthrough

### Exact Exercise Flow

```
User: "Analyze Large_Agentic_AI_Applications_2025.csv and generate top 5 insights"

→ OrchestratorAgent.run() called
    │
    ├─► [FileAgent] summarize_csv()
    │     Insight 1: "Dataset: 10,000 AI agent records, N industries, M application areas."
    │     Insight 2: "Most active industry: <X> (N agents)."
    │     Insight 3: "Most common application area: <Y> (N agents)."
    │     Insight 4: "Most used technology stack: <Z> (N deployments)."
    │
    ├─► [DBAgent] deployments_by_year()
    │     Insight 5: "Peak deployment year: 2025 (N agents launched)."
    │
    ├─► [DBAgent] industry_area_breakdown()
    │     Insight 6: "Top industry-area combo: <X> + <Y> (N agents)."
    │
    ├─► [DBAgent] agents_by_year_and_region()
    │     Insight 7: "Highest single year-region group: 2025 / North America (N agents)."
    │
    ├─► [DBAgent] custom SQL (region diversity)
    │     Insight 8: "Most diverse region by industry: <R> (N unique industries)."
    │
    ├─► [CodeAgent] analyze_dataset() → JSON
    │     Insight 9: "Year breakdown: 2022:N, 2023:N, 2024:N, 2025:N."
    │
    ├─► [CodeAgent] run_python() tech diversity
    │     Insight 10: "Industry with most tech stack diversity: <X> (N unique stacks)"
    │
    └─► [FileAgent] write outputs
          output/agentic_ai_insights.txt   ← formatted numbered report
          output/agentic_ai_insights.json  ← JSON array
          output/agentic_ai_insights.csv   ← insight_no, insight

→ Top 5 printed to console
→ Returns List[str] of all 10 insights
```

---

## Memory System

**File:** `memory/tool_memory.py`

Records every tool call in a structured audit trail with timing.

```python
from memory.tool_memory import ToolMemory

mem = ToolMemory(persist_path="output/tool_memory.json")

# Manual recording
mem.record(
    tool_name="file_agent",
    action="read_csv",
    input_data={"path": "data/...csv"},
    output_data={"rows": 10000},
    success=True,
    duration_ms=45.3,
)

# Timed context manager
with mem.timed("code_executor", "run_python", {"code": "..."}) as t:
    t.result = tool.run_python("print('hi')")

# Query history
mem.get_by_tool("db_agent")
mem.get_by_status(success=False)
mem.slowest_call()
mem.failed_calls()

# Summary + persist
mem.print_summary()
mem.save()    # → output/tool_memory.json
```

**Summary output example:**
```
=======================================================
  TOOL MEMORY — SESSION SUMMARY
=======================================================
  Session start  : 2025-01-15T10:30:00
  Total calls    : 12
  Success        : 11   Failure: 1
  Success rate   : 91.7%
  Avg duration   : 38.5 ms

  Per-tool stats:
    file_agent          calls=4  ok=4  fail=0  avg=12.3 ms
    db_agent            calls=5  ok=5  fail=0  avg=8.1 ms
    code_executor       calls=3  ok=2  fail=1  avg=95.2 ms
```

---

## Logging System

**File:** `logger.py`

Two-handler logging: DEBUG → file, INFO → console.

```python
from logger import get_logger, log_tool_call, ToolLogger

# Named logger
log = get_logger("my_module")
log.info("Processing started")
log.debug("Low-level detail")

# Auto-log decorator
@log_tool_call
def execute(self, **kwargs):
    ...

# Class-based helper
tlog = ToolLogger("my_tool")
tlog.start("execute", csv_path="data/...")
tlog.success("execute", rows=10000)
tlog.failure("execute", error="File not found")
tlog.summary()   # → {"tool": "my_tool", "total": 3, "success": 2, "failure": 1}
```

**Log file location:** `logs/tool_execution.log`

**Log format:**
```
2025-01-15 10:30:00 | INFO     | tool.file_agent      | [file_agent] START  read_csv  params={'path': 'data/...'}
2025-01-15 10:30:00 | INFO     | tool.file_agent      | [file_agent] OK     read_csv  rows=10000
```

---

## File Structure

```
DAY_3-TOOL_CALLING_AGENTS/
│
├── tools/
│   ├── base_tool.py          Abstract base: execute(), get_schema(), log_execution()
│   ├── code_executor.py      Python exec + subprocess shell
│   ├── db_agent.py           SQLite load + SQL query runner
│   ├── file_agent.py         Read/write .txt .csv .json + search
│   ├── search_agent.py       File search + CSV ranking + grep
│   └── __init__.py
│
├── agents/
│   ├── base_agent.py         Abstract agent with tool registry
│   ├── tool_agent.py         Named tool executor + chain runner
│   ├── orchestrator_agent.py 3-agent pipeline → combined insights
│   └── __init__.py
│
├── memory/
│   ├── tool_memory.py        Execution history + timing + persistence
│   └── __init__.py
│
├── data/
│   ├── Large_Agentic_AI_Applications_2025.csv   ← Source dataset (10k rows)
│   └── agentic_ai.db                            ← SQLite (auto-generated)
│
├── output/
│   ├── agentic_ai_insights.txt    ← Final report (numbered)
│   ├── agentic_ai_insights.json   ← JSON array of insights
│   ├── agentic_ai_insights.csv    ← CSV: insight_no, insight
│   ├── demo_report.txt            ← Quick demo output
│   └── tool_memory.json           ← Session memory dump
│
├── logs/
│   └── tool_execution.log         ← DEBUG + INFO log entries
│
├── tests/
│   ├── test_code_executor.py      35 unit tests
│   ├── test_db_agent.py           30 unit tests
│   ├── test_file_agent.py         35 unit tests
│   ├── test_orchestrator.py       15 unit tests
│   ├── test_integration.py        20 integration tests
│   └── __init__.py
│
├── config.py                      Per-tool config constants
├── logger.py                      Centralised logging
├── main.py                        Demo runner (4 demos)
├── utils.py                       Shared utilities
├── requirements.txt
├── run_demo.sh
├── run_tests.sh
├── setup.sh
└── TOOL-CHAIN.md                  ← This file
```

---

## Running the System

### Quick Start
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place the dataset
cp Large_Agentic_AI_Applications_2025.csv data/

# 4. Run the full demo
python main.py

# 5. Run only the orchestrator
python agents/orchestrator_agent.py

# 6. Run individual tools
python tools/code_executor.py
python tools/db_agent.py
python tools/file_agent.py
python tools/search_agent.py
```

### Using the Shell Scripts
```bash
./setup.sh      # Install deps + create directories
./run_demo.sh   # Run main.py
./run_tests.sh  # Run pytest with coverage
```

### Expected Console Output
```
╔═══════════════════════════════════════════════════════════╗
║        🤖 TOOL-CALLING AGENTS SYSTEM 🤖                  ║
║        Agentic AI Applications 2025 Analysis             ║
╚═══════════════════════════════════════════════════════════╝

✓ Dataset found at data/Large_Agentic_AI_Applications_2025.csv
✓ Database ready at data/agentic_ai.db

═══════════════════════════════════════
📁 DEMO 1: File Operations
...
🗄️  DEMO 2: Database Queries
...
💻 DEMO 3: Code Execution
...
🎯 DEMO 4: Orchestrated Task
...

=======================================================
  COMBINED FINAL ANSWER — TOP 5 INSIGHTS
=======================================================
1. Dataset: 10,000 AI agent records, 10 industries, 8 application areas.
2. Most active industry: Transportation (1,234 agents).
3. Most common application area: Predictive Analytics (1,100 agents).
4. Most used technology stack: TensorFlow + Python (890 deployments).
5. Top deployment region: North America (3,200 deployments).
=======================================================
Full report  → output/agentic_ai_insights.txt
JSON report  → output/agentic_ai_insights.json
CSV report   → output/agentic_ai_insights.csv
Total insights generated: 10
```

---

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ -v --cov=tools --cov=agents --cov-report=term-missing
```

### Run by Category
```bash
pytest tests/test_code_executor.py -v   # Python exec + shell
pytest tests/test_db_agent.py      -v   # SQLite queries
pytest tests/test_file_agent.py    -v   # File I/O + search
pytest tests/test_orchestrator.py  -v   # Pipeline
pytest tests/test_integration.py   -v   # End-to-end
```

### Test Structure

| File | Classes | Tests | What it Verifies |
|------|---------|-------|-----------------|
| `test_code_executor.py` | 5 | ~35 | Python exec, shell, dataset methods, schema |
| `test_db_agent.py` | 4 | ~30 | CSV load, SQL execution, pre-built queries, schema |
| `test_file_agent.py` | 6 | ~35 | Read/write .txt/.csv/.json, search, summarise |
| `test_orchestrator.py` | 4 | ~15 | Init, pipeline, output files, delegation |
| `test_integration.py` | 6 | ~20 | Exercise scenario, cross-tool consistency, E2E |

### Key Integration Test
```python
# test_integration.py — TestCrossToolConsistency
def test_row_count_consistent_file_vs_db(file_agent, db_agent):
    """FileAgent and DBAgent must agree on total row count."""
    file_r = file_agent.read_csv(CSV_PATH)
    db_r   = db_agent.execute("SELECT COUNT(*) as cnt FROM agentic_applications")
    assert file_r["rows"] == db_r["data"][0]["cnt"]

def test_top_industry_consistent_db_vs_code(db_agent, code_agent):
    """DBAgent SQL and CodeAgent pandas must agree on top industry."""
    ...
```

---

## Topic Coverage Map

| Day 3 Topic | Where Implemented | Method / Feature |
|-------------|------------------|-----------------|
| **Python tool calling** | `tools/code_executor.py` | `run_python()` via `exec()` |
| **Shell command tools** | `tools/code_executor.py` | `run_shell()` via `subprocess.run()` |
| **SQLite / CSV querying** | `tools/db_agent.py` | `load_csv()` → SQLite, `execute(sql)` |
| **File reading (.txt, .csv)** | `tools/file_agent.py` | `read_csv()`, `read_txt()`, `read_json()` |
| **File writing (.txt, .csv)** | `tools/file_agent.py` | `write_txt()`, `write_csv()`, `write_json()` |
| **Local search engine** | `tools/search_agent.py` + `tools/file_agent.py` | `search_files()`, `search_csv_content()`, `rank_results()` |
| **CodeAgent** | `tools/code_executor.py` + `agents/orchestrator_agent.py` | Step 3 of pipeline |
| **DBAgent** | `tools/db_agent.py` + `agents/orchestrator_agent.py` | Step 2 of pipeline |
| **FileAgent** | `tools/file_agent.py` + `agents/orchestrator_agent.py` | Steps 1 + 4 of pipeline |
| **Orchestrator** | `agents/orchestrator_agent.py` | Assigns + combines all agents |
| **Function calling schema** | Every tool's `.schema` attribute | JSON `{name, description, parameters}` |
| **Tool memory** | `memory/tool_memory.py` | `record()`, `timed()`, `summary()`, `save()` |
| **Logging** | `logger.py` | `get_logger()`, `ToolLogger`, `@log_tool_call` |

---

