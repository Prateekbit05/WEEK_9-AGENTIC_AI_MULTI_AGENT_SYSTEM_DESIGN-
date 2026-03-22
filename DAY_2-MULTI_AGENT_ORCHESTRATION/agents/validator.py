"""
Validator Agent
===============
Deliverable: /agents/validator.py

DAY 2 Exercise requirement:
  ✔  Checks the final answer for errors before it reaches the user
  ✔  Final stage in the chain-of-command:
       User → Orchestrator → Workers → Reflection → Validator → Answer

Two-pass validation
-------------------
Pass 1  Rule-based (fast, no LLM call):
        • Answer must be non-empty and above minimum length
        • No placeholder / mock text detected
        • Keyword overlap with original query ≥ 15%
        • Structural checks (paragraphs, headings)

Pass 2  LLM semantic (only runs if Pass 1 clears):
        • Model rates the answer 0–100
        • Returns specific issues[] and strengths[]
        • Only flags GENUINE errors (factual mistakes, off-topic content)
        • Score blended: 40% rule-based + 60% LLM semantic

Quality tiers
-------------
    75–100  Good      🟢 green
    50–74   Adequate  🟡 yellow
    0–49    Poor      🔴 red
"""
from __future__ import annotations

# ── Path fix ──────────────────────────────────────────────────────────────────
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
# ─────────────────────────────────────────────────────────────────────────────
import json
import re
from typing import Any, Dict, List, Optional

import config
from agents.base_agent import BaseAgent


# Strings that prove the answer is still a mock placeholder — never LLM output
_PLACEHOLDER_MARKERS = [
    "[Detailed information gathered]",
    "[Analytical insights provided]",
    "[Data processed successfully]",
    "[Result generated]",
    "TODO", "TBD", "PLACEHOLDER",
]


# ══════════════════════════════════════════════════════════════════════════
# ValidationResult
# ══════════════════════════════════════════════════════════════════════════

class ValidationResult:
    """
    Accumulates findings from both validation passes and computes a
    blended quality score.
    """

    def __init__(self):
        self.is_valid:     bool        = True
        self.errors:       List[str]   = []
        self.warnings:     List[str]   = []
        self.suggestions:  List[str]   = []
        self.quality_score: float      = 0.0
        self._llm_score:   Optional[float] = None

    # ── Mutators ──────────────────────────────────────────────────────────

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.is_valid = False          # any error → invalid

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def add_suggestion(self, msg: str) -> None:
        self.suggestions.append(msg)

    # ── Score calculation ─────────────────────────────────────────────────

    def compute_score(self, answer: str) -> None:
        """
        Rule-based score + optional LLM score → blended final score.

        Rule-based component (60 points possible):
          Length bonus  : up to +30 pts
          Structure     : up to +10 pts
          Penalise      : -20 per error, -5 per warning, +3 per suggestion
        LLM component (if available):
          Weighted 60%, rule-based weighted 40%.
        """
        # ── Rule-based ─────────────────────────────────────────────────
        rule = 50.0
        n = len(answer.strip())

        if n > 200:   rule += 10
        if n > 500:   rule += 10
        if n > 1000:  rule += 10
        if "\n" in answer:                    rule += 5
        if re.search(r"\n#{1,3} ", answer):   rule += 5   # has ## headings

        rule -= len(self.errors)      * 20
        rule -= len(self.warnings)    *  5
        rule += len(self.suggestions) *  3
        rule  = max(0.0, min(100.0, rule))

        # ── Blend ──────────────────────────────────────────────────────
        if self._llm_score is not None:
            final = 0.4 * rule + 0.6 * self._llm_score
        else:
            final = rule

        self.quality_score = round(max(0.0, min(100.0, final)), 1)

    # ── Serialisation ─────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid":      self.is_valid,
            "quality_score": self.quality_score,
            "errors":        self.errors,
            "warnings":      self.warnings,
            "suggestions":   self.suggestions,
        }


# ══════════════════════════════════════════════════════════════════════════
# ValidatorAgent
# ══════════════════════════════════════════════════════════════════════════

class ValidatorAgent(BaseAgent):
    """
    Quality-assurance gate — last agent in the pipeline.

    Chain of command position:
        Orchestrator → Workers (parallel) → Reflection → Validator → User

    The Validator ensures the final answer:
      • Is not empty or placeholder text
      • Is relevant to the original query
      • Has good structure
      • Is factually coherent (LLM semantic check)
    """

    def __init__(self, name: str = "Validator"):
        super().__init__(name=name, role="validator")

    # ── Public interface ──────────────────────────────────────────────────

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run both validation passes and return a ValidationResult."""
        task_id = task.get("task_id", "unknown")
        answer  = task.get("answer",  "")
        query   = task.get("query",   "")

        self.logger.info(f"Validator checking task {task_id}")
        self.add_to_memory({"action": "validation_started", "task_id": task_id})

        vr = await self._validate(answer, query)

        self.add_to_memory({
            "action":        "validation_completed",
            "task_id":       task_id,
            "is_valid":      vr.is_valid,
            "quality_score": vr.quality_score,
        })
        self.execution_count += 1

        return {
            "status":       "success",
            "task_id":      task_id,
            "validation":   vr.to_dict(),
            "final_answer": answer if vr.is_valid else None,
            "agent":        self.to_dict(),
        }

    # ── Validation pipeline ───────────────────────────────────────────────

    async def _validate(self, answer: str, query: str) -> ValidationResult:
        vr = ValidationResult()

        # Pass 1 — rule-based (always runs, fast)
        self._check_not_empty(answer, vr)
        self._check_no_placeholders(answer, vr)
        self._check_relevance(answer, query, vr)
        self._check_structure(answer, vr)

        # Pass 2 — LLM semantic (only if Pass 1 clears)
        if vr.is_valid:
            await self._llm_semantic_check(answer, query, vr)

        vr.compute_score(answer)
        return vr

    # ── Pass 1: rule-based ────────────────────────────────────────────────

    def _check_not_empty(self, answer: str, vr: ValidationResult) -> None:
        stripped = answer.strip()
        if not stripped:
            vr.add_error("Answer is empty.")
        elif len(stripped) < 30:
            vr.add_error(
                f"Answer is too short ({len(stripped)} chars — minimum 30)."
            )

    def _check_no_placeholders(self, answer: str, vr: ValidationResult) -> None:
        for marker in _PLACEHOLDER_MARKERS:
            if marker in answer:
                vr.add_error(
                    f"Answer contains placeholder text: '{marker}'. "
                    "Worker agents must use real LLM calls."
                )
                return  # one error per check is enough

    def _check_relevance(
        self, answer: str, query: str, vr: ValidationResult
    ) -> None:
        if not vr.is_valid:
            return
        # Use only "meaningful" words (length > 3) to avoid stop-word noise
        q_words = {w for w in re.findall(r"\b\w+\b", query.lower())  if len(w) > 3}
        a_words = {w for w in re.findall(r"\b\w+\b", answer.lower()) if len(w) > 3}
        if not q_words:
            return
        ratio = len(q_words & a_words) / len(q_words)
        if ratio < 0.15:
            vr.add_warning(
                f"Low keyword overlap with query ({ratio:.0%}). "
                "Answer may not address the question directly."
            )
        elif ratio >= 0.4:
            vr.add_suggestion(f"Strong keyword alignment with query ({ratio:.0%}).")

    def _check_structure(self, answer: str, vr: ValidationResult) -> None:
        if not vr.is_valid:
            return
        if len(answer) > 200 and "\n" in answer:
            vr.add_suggestion("Answer has good multi-paragraph structure.")
        if re.search(r"\n#{1,3} ", answer):
            vr.add_suggestion("Answer uses markdown headings — well organised.")
        if re.search(r"```", answer):
            vr.add_suggestion("Answer includes code blocks.")

    # ── Pass 2: LLM semantic check ────────────────────────────────────────

    async def _llm_semantic_check(
        self, answer: str, query: str, vr: ValidationResult
    ) -> None:
        """
        Ask the LLM to score the answer and surface genuine issues.
        Only flags real errors — not stylistic preferences or missing
        advanced content the question didn't ask for.
        """
        system = (
            "You are a quality-assurance reviewer for AI-generated answers.\n"
            "Given a question and an answer, respond ONLY with a JSON object.\n"
            "No markdown fences, no explanation — just the JSON:\n"
            '{"score": <0-100>, "issues": ["..."], "strengths": ["..."]}\n\n'
            "Scoring:\n"
            "  90-100 : Complete, accurate, well-structured\n"
            "  75-89  : Good with minor gaps\n"
            "  50-74  : Adequate but missing important aspects\n"
            "  0-49   : Inaccurate, off-topic, or too shallow\n\n"
            "issues   : ONLY flag factual errors, wrong information, off-topic "
            "content, or critically missing core concepts the question asked for.\n"
            "           Do NOT flag missing derivations or niche details unless "
            "the question specifically requested them.\n"
            "strengths: What the answer does well.\n"
            "One concise sentence per item. Use empty lists [] if nothing to report."
        )
        user = (
            f"Question: {query}\n\n"
            f"Answer:\n{answer}\n\n"
            "Rate this answer. Only flag genuine errors as issues."
        )

        try:
            raw   = await self.call_llm(
                system      = system,
                user        = user,
                model       = config.VALIDATOR_MODEL,
                max_tokens  = config.VALIDATOR_MAX_TOKENS,
                temperature = config.VALIDATOR_TEMPERATURE,
            )
            clean = re.sub(r"```(?:json)?|```", "", raw).strip()
            data  = json.loads(clean)

            vr._llm_score = float(data.get("score", 50))

            for issue in data.get("issues", []):
                vr.add_warning(f"[LLM] {issue}")
            for strength in data.get("strengths", []):
                vr.add_suggestion(f"[LLM] {strength}")

        except Exception as exc:
            # Non-fatal — fall back to rule-based score only
            self.logger.warning(f"LLM semantic check skipped: {exc}")

    def __repr__(self) -> str:
        return f"ValidatorAgent(name='{self.name}')"