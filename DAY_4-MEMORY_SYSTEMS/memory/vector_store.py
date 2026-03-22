"""
memory/vector_store.py
Topic: Vector Memory (FAISS)
Dataset: Large_Agentic_AI_Applications_2025.csv
Logs: logs/vector_store.log
"""

import os
import sys
import json
import pickle
import hashlib
import numpy as np
import faiss
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import vector_logger

log = vector_logger()


class VectorStore:
    """FAISS vector memory with dataset-aware loading."""

    def __init__(self, dim: int = 512,
                 index_path: str = "memory/vector.index",
                 meta_path:  str = "memory/vector_meta.pkl"):
        self.dim        = dim
        self.index_path = index_path
        self.meta_path  = meta_path
        self.index      = faiss.IndexFlatIP(dim)
        self.metadata:  List[Dict] = []
        self.vocab:     Dict[str, int] = {}

        if os.path.exists(index_path) and os.path.exists(meta_path):
            self.load()
        else:
            log.info(f"VectorStore initialised (new) | dim={dim} | path={index_path}")

    # ── Encoding ──────────────────────────────────────────────────────
    def _encode(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dim, dtype=np.float32)
        if not self.vocab:
            for i, char in enumerate(text.lower()):
                idx = (ord(char) * 31 + i) % self.dim
                vec[idx] += 1.0
            for i in range(len(text) - 2):
                bigram = text[i:i+2].lower()
                idx    = abs(hash(bigram)) % self.dim
                vec[idx] += 0.5
        else:
            t = text.lower()
            for n in [2, 3, 4]:
                for i in range(len(t) - n + 1):
                    ng = t[i:i+n]
                    if ng in self.vocab:
                        vec[self.vocab[ng]] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.reshape(1, -1)

    # ── Load Day 3 dataset ────────────────────────────────────────────
    def load_dataset(self, csv_path: str) -> int:
        """Encode dataset facts into FAISS — 68 vectors."""
        if not os.path.exists(csv_path):
            log.error(f"CSV not found | path={csv_path}")
            print(f"[VectorStore] CSV not found: {csv_path}")
            return 0

        log.info(f"Loading dataset into FAISS | path={csv_path}")
        df    = pd.read_csv(csv_path)
        count = 0

        for ind, cnt in df["Industry"].value_counts().items():
            self.add(f"{ind} industry has {cnt} AI agents in the dataset.",
                     {"category": "industry", "industry": ind, "count": cnt, "source": "dataset"})
            count += 1
        for area, cnt in df["Application Area"].value_counts().items():
            self.add(f"{area} is an application area with {cnt} agents.",
                     {"category": "application_area", "area": area, "count": cnt, "source": "dataset"})
            count += 1
        for stack, cnt in df["Technology Stack"].value_counts().items():
            self.add(f"{stack} technology stack is used by {cnt} agents.",
                     {"category": "technology_stack", "stack": stack, "count": cnt, "source": "dataset"})
            count += 1
        for region, cnt in df["Geographical Region"].value_counts().items():
            self.add(f"{region} region has {cnt} AI agent deployments.",
                     {"category": "region", "region": region, "count": cnt, "source": "dataset"})
            count += 1
        for year, cnt in df["Deployment Year"].value_counts().sort_index().items():
            self.add(f"In {year}, {cnt} AI agents were deployed.",
                     {"category": "year", "year": int(year), "count": cnt, "source": "dataset"})
            count += 1

        overviews = [
            f"The dataset has {len(df):,} AI agent records in total.",
            f"There are {df['Industry'].nunique()} unique industries in the dataset.",
            f"There are {df['Application Area'].nunique()} unique application areas.",
            f"Top industry: {df['Industry'].value_counts().idxmax()} with {df['Industry'].value_counts().max()} agents.",
            f"Top application area: {df['Application Area'].value_counts().idxmax()} with {df['Application Area'].value_counts().max()} agents.",
            f"Top technology stack: {df['Technology Stack'].value_counts().idxmax()} with {df['Technology Stack'].value_counts().max()} uses.",
            f"Top geographical region: {df['Geographical Region'].value_counts().idxmax()} with {df['Geographical Region'].value_counts().max()} deployments.",
            f"Peak deployment year: {int(df['Deployment Year'].value_counts().idxmax())} with {df['Deployment Year'].value_counts().max()} agents.",
            f"The dataset covers deployment years 2023, 2024, and 2025.",
            f"6 geographical regions: Asia, Europe, Australia, North America, South America, Africa.",
        ]
        for text in overviews:
            self.add(text, {"category": "overview", "source": "dataset"})
            count += 1

        for _, row in df.head(20).iterrows():
            text = (f"{row['AI Agent Name']} in {row['Industry']} "
                    f"performs {row['Task Description']} "
                    f"using {row['Technology Stack']}.")
            self.add(text, {"category": "agent_sample", "agent": row["AI Agent Name"],
                            "industry": row["Industry"], "source": "dataset"})
            count += 1

        log.info(f"Dataset loaded | vectors={count} | total_index={self.index.ntotal}")
        print(f"[VectorStore] Dataset loaded: {count} vectors → FAISS index")
        return count

    # ── Core ──────────────────────────────────────────────────────────
    def add(self, text: str, metadata: Dict = None) -> int:
        vec    = self._encode(text)
        doc_id = len(self.metadata)
        self.index.add(vec)
        self.metadata.append({
            "id":        doc_id,
            "text":      text,
            "timestamp": datetime.now().isoformat(),
            "metadata":  metadata or {}
        })
        log.debug(f"Vector added | id={doc_id} | text={text[:60]}")
        return doc_id

    def add_batch(self, texts: List[str], metadatas: List[Dict] = None) -> List[int]:
        ids = []
        for i, text in enumerate(texts):
            meta = metadatas[i] if metadatas else {}
            ids.append(self.add(text, meta))
        log.info(f"Batch added | count={len(ids)}")
        return ids

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Similarity-based recall — exercise flow core step."""
        if self.index.ntotal == 0:
            log.warning("Search called on empty index")
            return []
        top_k  = min(top_k, self.index.ntotal)
        q_vec  = self._encode(query)
        scores, indices = self.index.search(q_vec, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            entry = self.metadata[idx].copy()
            entry["score"] = float(score)
            results.append(entry)
        results.sort(key=lambda x: x["score"], reverse=True)
        top_score = round(results[0]["score"], 3) if results else 0
        log.debug(f"Search | query={query[:50]} | top_k={top_k} | results={len(results)} | top_score={top_score}")
        return results

    def search_by_category(self, query: str, category: str,
                           top_k: int = 5) -> List[Dict]:
        results  = self.search(query, top_k=top_k * 3)
        filtered = [r for r in results
                    if r.get("metadata", {}).get("category") == category]
        log.debug(f"Category search | category={category} | results={len(filtered[:top_k])}")
        return filtered[:top_k]

    def inject_context(self, query: str, top_k: int = 3) -> str:
        """Build formatted context string — inject into prompt."""
        results = self.search(query, top_k=top_k)
        if not results:
            return ""
        lines = ["[RELEVANT MEMORY CONTEXT]"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. (score:{r['score']:.3f}) {r['text']}")
        lines.append("[END CONTEXT]")
        context = "\n".join(lines)
        log.info(f"Context injected | query={query[:50]} | memories={len(results)}")
        return context

    def build_prompt_with_memory(self, query: str,
                                 system_prompt: str = "",
                                 top_k: int = 3) -> str:
        context = self.inject_context(query, top_k=top_k)
        parts   = []
        if system_prompt:
            parts.append(f"SYSTEM: {system_prompt}")
        if context:
            parts.append(context)
        parts.append(f"USER QUERY: {query}")
        parts.append("ASSISTANT:")
        log.debug(f"Prompt built with memory | query={query[:50]}")
        return "\n\n".join(parts)

    # ── Persistence ───────────────────────────────────────────────────
    def save(self):
        os.makedirs(os.path.dirname(self.index_path) or ".", exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump({"metadata": self.metadata,
                         "vocab": self.vocab, "dim": self.dim}, f)
        log.info(f"Index saved | vectors={self.index.ntotal} | path={self.index_path}")
        print(f"[VectorStore] Saved {self.index.ntotal} vectors → {self.index_path}")

    def load(self):
        self.index    = faiss.read_index(self.index_path)
        with open(self.meta_path, "rb") as f:
            data = pickle.load(f)
        self.metadata = data["metadata"]
        self.vocab    = data.get("vocab", {})
        self.dim      = data.get("dim", self.dim)
        log.info(f"Index loaded | vectors={self.index.ntotal} | path={self.index_path}")
        print(f"[VectorStore] Loaded {self.index.ntotal} vectors from {self.index_path}")

    def stats(self) -> Dict:
        cats = {}
        for m in self.metadata:
            cat = m.get("metadata", {}).get("category", "unknown")
            cats[cat] = cats.get(cat, 0) + 1
        return {
            "total_vectors":   self.index.ntotal,
            "dimension":       self.dim,
            "index_type":      "IndexFlatIP (cosine similarity)",
            "index_path":      self.index_path,
            "categories":      cats,
        }

    def clear(self):
        self.index    = faiss.IndexFlatIP(self.dim)
        self.metadata = []
        self.vocab    = {}
        log.warning("VectorStore cleared")
        print("[VectorStore] Cleared.")

    def __len__(self):
        return self.index.ntotal

    def __repr__(self):
        return f"VectorStore(vectors={self.index.ntotal}, dim={self.dim})"


# ── Demo ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  TOPIC: Vector Memory (FAISS)")
    print("  Dataset: Large_Agentic_AI_Applications_2025.csv")
    print("=" * 55)

    vs = VectorStore(dim=512,
                     index_path="memory/vector.index",
                     meta_path="memory/vector_meta.pkl")
    vs.clear()

    print("\n[1] Loading Day 3 dataset into FAISS...")
    count = vs.load_dataset("data/Large_Agentic_AI_Applications_2025.csv")
    print(f"    Vectors: {len(vs)}")

    print("\n[2] Similarity search:")
    for q in [
        "Which industry has the most AI agents?",
        "What technology stack is most commonly used?",
        "Tell me about deployment regions.",
        "What year had the most deployments?",
    ]:
        print(f"\n    Query: '{q}'")
        for r in vs.search(q, top_k=2):
            print(f"      [{r['score']:.3f}] {r['text'][:65]}")

    print("\n[3] Context injection:")
    print(vs.inject_context("Key dataset statistics", top_k=3))

    print("\n[4] Full prompt with memory:")
    print(vs.build_prompt_with_memory(
        query="What are the key dataset insights?",
        system_prompt="You are an AI analyst. Use the context.",
        top_k=3
    ))

    vs.save()
    print("\n[5] Stats:")
    s = vs.stats()
    print(f"    Vectors   : {s['total_vectors']}")
    print(f"    Categories: {s['categories']}")
    print("\n  ✓ Check logs/vector_store.log for detailed logs")