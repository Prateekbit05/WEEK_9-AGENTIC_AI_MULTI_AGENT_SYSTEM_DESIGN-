"""
memory/session_memory.py
Topic: Short-term (Session Memory)
Dataset: Large_Agentic_AI_Applications_2025.csv
Logs: logs/session_memory.log
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import session_logger

log = session_logger()

DATASET_KEYWORDS = [
    "industry", "application area", "technology stack", "region",
    "deployment year", "transportation", "healthcare", "retail",
    "education", "agriculture", "iot", "ml", "robotics", "drones",
    "personalized learning", "fraud detection", "customer service",
    "energy management", "autonomous vehicles", "asia", "europe",
    "australia", "north america", "south america", "africa",
    "2023", "2024", "2025", "agent", "dataset"
]

USER_FACT_PATTERNS = [
    "my name is", "i am", "i work", "i like", "i prefer",
    "i need", "i want", "remember that", "important:", "note:",
    "always", "never", "my goal", "i study", "i analyse",
]


class SessionMemory:
    """Short-term in-memory store for the current conversation session."""

    def __init__(self, session_id: str = None, max_turns: int = 100):
        self.session_id      = session_id or self._gen_id()
        self.max_turns       = max_turns
        self.turns:  List[Dict] = []
        self.facts:  List[str] = []
        self.created_at      = datetime.now().isoformat()
        self.dataset_context: Dict = {}
        log.info(f"SessionMemory created | session_id={self.session_id} | max_turns={max_turns}")

    def _gen_id(self) -> str:
        return hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:8]

    def _turn_id(self, content: str) -> str:
        return hashlib.md5(f"{datetime.now().isoformat()}{content}".encode()).hexdigest()[:12]

    # ── Dataset loading ───────────────────────────────────────────────
    def load_dataset_context(self, csv_path: str):
        """Load Day 3 dataset stats into session as short-term knowledge."""
        log.info(f"Loading dataset context | path={csv_path}")
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            self.dataset_context = {
                "csv_path":          csv_path,
                "total_records":     len(df),
                "columns":           list(df.columns),
                "industries":        df["Industry"].value_counts().to_dict(),
                "application_areas": df["Application Area"].value_counts().to_dict(),
                "technology_stacks": df["Technology Stack"].value_counts().to_dict(),
                "regions":           df["Geographical Region"].value_counts().to_dict(),
                "years":             df["Deployment Year"].value_counts().sort_index().to_dict(),
                "top_industry":      df["Industry"].value_counts().idxmax(),
                "top_area":          df["Application Area"].value_counts().idxmax(),
                "top_stack":         df["Technology Stack"].value_counts().idxmax(),
                "top_region":        df["Geographical Region"].value_counts().idxmax(),
                "peak_year":         int(df["Deployment Year"].value_counts().idxmax()),
            }
            self._auto_store_dataset_facts()
            log.info(f"Dataset loaded | records={len(df):,} | top_industry={self.dataset_context['top_industry']}")
            print(f"[SessionMemory] Dataset loaded: {len(df):,} records")
            return self.dataset_context
        except Exception as e:
            log.error(f"Dataset load failed | path={csv_path} | error={e}")
            print(f"[SessionMemory] Dataset load error: {e}")
            return {}

    def _auto_store_dataset_facts(self):
        ctx = self.dataset_context
        if not ctx:
            return
        auto_facts = [
            f"Dataset has {ctx['total_records']:,} AI agent records.",
            f"Dataset columns: {', '.join(ctx['columns'])}.",
            f"Top industry: {ctx['top_industry']} ({ctx['industries'][ctx['top_industry']]:,} agents).",
            f"Top application area: {ctx['top_area']} ({ctx['application_areas'][ctx['top_area']]:,} agents).",
            f"Top technology stack: {ctx['top_stack']} ({ctx['technology_stacks'][ctx['top_stack']]:,} uses).",
            f"Top region: {ctx['top_region']} ({ctx['regions'][ctx['top_region']]:,} deployments).",
            f"Peak deployment year: {ctx['peak_year']}.",
            f"Industries: {', '.join(list(ctx['industries'].keys()))}.",
            f"Year breakdown: 2023={ctx['years'].get(2023,0)}, 2024={ctx['years'].get(2024,0)}, 2025={ctx['years'].get(2025,0)}.",
        ]
        for fact in auto_facts:
            self.add_fact(fact)
        log.debug(f"Auto-stored {len(auto_facts)} dataset facts")

    # ── Core ──────────────────────────────────────────────────────────
    def add_message(self, role: str, content: str, metadata: Dict = None) -> Dict:
        turn = {
            "turn_id":   self._turn_id(content),
            "role":      role,
            "content":   content,
            "timestamp": datetime.now().isoformat(),
            "metadata":  metadata or {}
        }
        self.turns.append(turn)
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
        log.debug(f"Message added | role={role} | turn={len(self.turns)} | content={content[:60]}")
        return turn

    def get_history(self) -> List[Dict]:
        return self.turns.copy()

    def get_recent(self, n: int = 5) -> List[Dict]:
        return self.turns[-n:]

    def get_by_role(self, role: str) -> List[Dict]:
        return [t for t in self.turns if t["role"] == role]

    def get_context_window(self, n: int = 6) -> str:
        lines = []
        for t in self.get_recent(n):
            lines.append(f"{t['role'].upper()}: {t['content']}")
        context = "\n".join(lines)
        log.debug(f"Context window built | turns={min(n, len(self.turns))}")
        return context

    def get_dataset_summary(self) -> str:
        ctx = self.dataset_context
        if not ctx:
            return ""
        return (
            f"Dataset: {ctx['total_records']:,} records | "
            f"Top industry: {ctx['top_industry']} | "
            f"Top stack: {ctx['top_stack']} | "
            f"Top region: {ctx['top_region']} | "
            f"Peak year: {ctx['peak_year']}"
        )

    # ── Facts ─────────────────────────────────────────────────────────
    def add_fact(self, fact: str):
        if fact and fact not in self.facts:
            self.facts.append(fact)
            log.debug(f"Fact added | fact={fact[:60]}")

    def get_facts(self) -> List[str]:
        return self.facts.copy()

    def extract_facts_from_turn(self, content: str) -> List[str]:
        facts = []
        sentences = content.replace(".", ".\n").split("\n")
        for sentence in sentences:
            s  = sentence.strip()
            sl = s.lower()
            if len(s) < 10:
                continue
            if any(p in sl for p in USER_FACT_PATTERNS):
                facts.append(s)
            elif any(k in sl for k in DATASET_KEYWORDS):
                facts.append(s)
        if facts:
            log.debug(f"Facts extracted | count={len(facts)} | from={content[:50]}")
        return facts

    # ── Search ────────────────────────────────────────────────────────
    def search(self, keyword: str) -> List[Dict]:
        kw      = keyword.lower()
        results = [t for t in self.turns if kw in t["content"].lower()]
        log.debug(f"Session search | keyword={keyword} | matches={len(results)}")
        return results

    def search_dataset_context(self, keyword: str) -> Dict:
        ctx = self.dataset_context
        if not ctx:
            return {}
        kw      = keyword.lower()
        results = {}
        for k, v in ctx.get("industries", {}).items():
            if kw in k.lower():
                results[f"industry:{k}"] = v
        for k, v in ctx.get("application_areas", {}).items():
            if kw in k.lower():
                results[f"area:{k}"] = v
        for k, v in ctx.get("technology_stacks", {}).items():
            if kw in k.lower():
                results[f"stack:{k}"] = v
        for k, v in ctx.get("regions", {}).items():
            if kw in k.lower():
                results[f"region:{k}"] = v
        log.debug(f"Dataset context search | keyword={keyword} | results={len(results)}")
        return results

    # ── Stats & IO ────────────────────────────────────────────────────
    def stats(self) -> Dict:
        return {
            "session_id":     self.session_id,
            "total_turns":    len(self.turns),
            "user_turns":     len(self.get_by_role("user")),
            "ai_turns":       len(self.get_by_role("assistant")),
            "facts_stored":   len(self.facts),
            "dataset_loaded": bool(self.dataset_context),
            "created_at":     self.created_at,
        }

    def to_dict(self) -> Dict:
        return {
            "session_id":      self.session_id,
            "created_at":      self.created_at,
            "turns":           self.turns,
            "facts":           self.facts,
            "dataset_context": self.dataset_context,
        }

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        log.info(f"Session saved | path={filepath} | turns={len(self.turns)} | facts={len(self.facts)}")
        print(f"[SessionMemory] Saved → {filepath}")

    def load(self, filepath: str):
        with open(filepath, "r") as f:
            data = json.load(f)
        self.session_id      = data["session_id"]
        self.created_at      = data["created_at"]
        self.turns           = data["turns"]
        self.facts           = data["facts"]
        self.dataset_context = data.get("dataset_context", {})
        log.info(f"Session loaded | path={filepath} | turns={len(self.turns)}")
        print(f"[SessionMemory] Loaded {len(self.turns)} turns from {filepath}")

    def clear(self):
        log.warning(f"Session cleared | session_id={self.session_id}")
        self.turns = []
        self.facts = []
        print(f"[SessionMemory] Session {self.session_id} cleared.")

    def __len__(self):
        return len(self.turns)

    def __repr__(self):
        return f"SessionMemory(id={self.session_id}, turns={len(self.turns)})"


# ── Demo ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  TOPIC: Short-term (Session Memory)")
    print("  Dataset: Large_Agentic_AI_Applications_2025.csv")
    print("=" * 55)

    mem = SessionMemory(session_id="day4_session")

    print("\n[1] Loading Day 3 dataset into session context...")
    mem.load_dataset_context("data/Large_Agentic_AI_Applications_2025.csv")
    print(f"    Facts auto-stored: {len(mem.get_facts())}")
    print(f"    Dataset summary  : {mem.get_dataset_summary()}")

    print("\n[2] Simulating conversation...")
    turns = [
        ("user",      "Hi! My name is Prateek. I am analysing the Agentic AI dataset."),
        ("assistant", "Hello Prateek! The dataset has 10,000 records across 10 industries."),
        ("user",      "Which industry has the most agents?"),
        ("assistant", "Transportation leads with 1,044 agents in the dataset."),
        ("user",      "What about technology stacks used?"),
        ("assistant", "IoT and ML is most used with 2,053 deployments."),
        ("user",      "Tell me about deployment regions."),
        ("assistant", "Asia and Europe are tied at 1,711 deployments each."),
    ]
    for role, content in turns:
        mem.add_message(role, content)
        for fact in mem.extract_facts_from_turn(content):
            mem.add_fact(fact)

    print(f"    Turns: {len(mem)} | Facts: {len(mem.get_facts())}")

    print("\n[3] Recent 4 turns:")
    for t in mem.get_recent(4):
        print(f"    [{t['role'].upper():<10}] {t['content'][:60]}")

    print("\n[4] Context window:")
    print(mem.get_context_window(n=4))

    print("\n[5] Search 'healthcare':")
    for k, v in mem.search_dataset_context("healthcare").items():
        print(f"    {k}: {v}")

    print("\n[6] Stats:")
    for k, v in mem.stats().items():
        print(f"    {k:<22}: {v}")

    mem.save("output/session_day4.json")
    print("\n  ✓ Check logs/session_memory.log for detailed logs")