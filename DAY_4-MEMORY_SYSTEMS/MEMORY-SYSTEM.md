# 🧠 MEMORY-SYSTEM.md
## Day 4 — Memory Systems: Short-term + Long-term + Vector Memory

---

## Overview

A 3-layer memory system for AI agents:

```
┌─────────────────────────────────────────────────────────┐
│                  AGENT MEMORY SYSTEM                    │
│                                                         │
│  Layer 1: SessionMemory   → short-term (in-memory)      │
│  Layer 2: LongTermMemory  → persistent (SQLite)         │
│  Layer 3: VectorStore     → similarity-based (FAISS)   │
└─────────────────────────────────────────────────────────┘
```

---

## Exercise Flow

```
New Query
    │
    ▼
Search vector memory (FAISS)
    │
    ▼
Fetch top-k similar context
    │
    ▼
Inject context into prompt
    │
    ▼
Generate response with context
    │
    ▼
Store turn in:
  ├── SessionMemory   (short-term)
  ├── LongTermMemory  (SQLite episodic + semantic)
  └── VectorStore     (FAISS embedding)
```

---

## Topics

### 1. Short-term Memory (`memory/session_memory.py`)
- Stores conversation turns in-memory for the current session
- Rolling window of last N turns
- Fact extraction from messages
- Context window builder for prompt injection
- Keyword search across session

### 2. Long-term Memory (`memory/long_term_memory.py`, `memory/long_term.db`)
- **Episodic memory** → stores what happened (conversation turns) in SQLite
- **Semantic memory** → stores extracted facts and knowledge
- Persists across sessions
- Recall by keyword, category, session ID
- Access count tracking (frequently recalled facts rank higher)

### 3. Vector Memory (`memory/vector_store.py`)
- Encodes text as n-gram frequency vectors (numpy + FAISS)
- Stores in FAISS `IndexFlatIP` (inner product = cosine similarity)
- Similarity-based recall: `query → search → top-k similar memories`
- `inject_context()` builds formatted context string
- `build_prompt_with_memory()` creates full prompt with context injected
- Persists index to `memory/vector.index`

### 4. Episodic vs Semantic Memory

| Type | What it stores | Where | Example |
|------|---------------|-------|---------|
| **Episodic** | Events, conversations, what happened | `episodes` table | "User asked about industries at 14:30" |
| **Semantic** | Facts, knowledge, what is known | `facts` table | "Transportation is top industry (1,044)" |
| **Short-term** | Current session context | in-memory | Last 5 conversation turns |
| **Vector** | Similarity-searchable embeddings | FAISS index | All memories encoded as vectors |

---

## Deliverables

| File | Purpose |
|------|---------|
| `memory/session_memory.py` | Short-term session memory |
| `memory/long_term_memory.py` | SQLite episodic + semantic memory |
| `memory/long_term.db` | Persistent SQLite database (generated on run) |
| `memory/vector_store.py` | FAISS vector memory |
| `memory/vector.index` | FAISS index file (generated on run) |
| `memory/vector_meta.pkl` | FAISS metadata (generated on run) |
| `agents/memory_agent.py` | Agent wiring all 3 memory layers |
| `main.py` | Full demo runner |
| `MEMORY-SYSTEM.md` | This document |

---

## How to Run

```bash
# Individual memory modules
python3 -m memory.session_memory
python3 -m memory.long_term_memory
python3 -m memory.vector_store

# Full memory agent (exercise flow)
python3 -m agents.memory_agent

# Full demo
python3 main.py
```
