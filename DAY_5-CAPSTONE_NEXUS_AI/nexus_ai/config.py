"""
nexus_ai/config.py
NEXUS AI — Central configuration (updated with Ollama model settings)
"""

import os

# ── Project identity ──────────────────────────────────────────────────
PROJECT_NAME    = "NEXUS AI"
PROJECT_VERSION = "1.0.0"
DESCRIPTION     = "Autonomous Multi-Agent AI System — Day 5 Capstone"

# ── Paths ─────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")
LOGS_DIR    = os.path.join(BASE_DIR, "logs")
MEMORY_DIR  = os.path.join(BASE_DIR, "memory")

CSV_PATH    = os.path.join(DATA_DIR, "Large_Agentic_AI_Applications_2025.csv")
DB_PATH     = os.path.join(MEMORY_DIR, "nexus_memory.db")
INDEX_PATH  = os.path.join(MEMORY_DIR, "nexus_vectors.index")
META_PATH   = os.path.join(MEMORY_DIR, "nexus_vectors_meta.pkl")

# ── Agent settings ────────────────────────────────────────────────────
MAX_PLAN_STEPS       = 8
MAX_RETRIES          = 3
MAX_REFLECTION_LOOPS = 2
CONFIDENCE_THRESHOLD = 0.65

# ── Memory settings ───────────────────────────────────────────────────
SESSION_MAX_TURNS = 200
VECTOR_DIM        = 512
VECTOR_TOP_K      = 5

# ── Ollama settings ───────────────────────────────────────────────────
# Base URL for local Ollama server
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Model assigned to each agent role
# phi3:mini  → reasoning-heavy agents  (Orchestrator, Planner, Coder, Critic)
# qwen2:1.5b → data/formatting agents  (Researcher, Analyst, Optimizer, Reporter)
# tinyllama  → binary-check agent      (Validator)
OLLAMA_AGENT_MODELS = {
    "orchestrator": "phi3:mini",
    "planner":      "phi3:mini",
    "coder":        "phi3:mini",
    "critic":       "phi3:mini",
    "researcher":   "qwen2:1.5b",
    "analyst":      "qwen2:1.5b",
    "optimizer":    "qwen2:1.5b",
    "reporter":     "qwen2:1.5b",
    "validator":    "tinyllama",
}

# If True: LLM output ENRICHES/EXTENDS existing template logic
# If False: LLM output REPLACES template (pure LLM mode)
# Recommended: True for CPU — templates provide structure, LLM adds intelligence
OLLAMA_HYBRID_MODE = True

# Timeout per LLM call in seconds (CPU is slow — be generous)
OLLAMA_TIMEOUT = 120

# Max tokens per model call (controls CPU inference time)
OLLAMA_MAX_TOKENS = {
    "phi3:mini":  800,
    "qwen2:1.5b": 600,
    "tinyllama":  200,
}

# ── Agent roles ───────────────────────────────────────────────────────
AGENT_ROLES = {
    "orchestrator": "Master coordinator — assigns tasks to agents, manages flow",
    "planner":      "Breaks tasks into ordered multi-step execution plans",
    "researcher":   "Searches memory and data for relevant information",
    "coder":        "Writes and executes Python code for analysis",
    "analyst":      "Analyses CSV data, extracts business insights",
    "critic":       "Reviews outputs, identifies weaknesses (self-reflection)",
    "optimizer":    "Improves plans and outputs based on critic feedback",
    "validator":    "Validates final outputs for accuracy and completeness",
    "reporter":     "Generates final structured reports for the user",
}

# ── Example tasks ─────────────────────────────────────────────────────
EXAMPLE_TASKS = [
    "Plan a startup in AI for healthcare",
    "Generate backend architecture for scalable app",
    "Analyze CSV and create business strategy",
    "Design a RAG pipeline for 50k documents",
]

# ── Ensure directories exist ──────────────────────────────────────────
for d in [DATA_DIR, OUTPUT_DIR, LOGS_DIR, MEMORY_DIR]:
    os.makedirs(d, exist_ok=True)