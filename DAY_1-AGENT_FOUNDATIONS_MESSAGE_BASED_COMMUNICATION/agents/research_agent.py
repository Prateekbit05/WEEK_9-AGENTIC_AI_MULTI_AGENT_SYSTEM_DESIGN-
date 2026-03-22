"""
RESEARCH AGENT — FIXED & ENHANCED
===================================
✅ FIX: Reads LLM_CONFIG fresh at init (not stale import)
✅ FIX: System prompt forces structured technical answers
✅ FIX: Detects architecture/RAG/workflow queries and adapts prompt
"""
from typing import Dict, List
import time


class ResearchAgent:

    SYSTEM_MESSAGE = """You are an expert RESEARCH AGENT specializing in AI, software architecture, and technology systems.

When asked about any technical topic, provide a COMPREHENSIVE and STRUCTURED response.

ALWAYS include these sections when relevant:

## Overview
[Clear explanation of what this technology/concept is]

## Architecture / How It Works
[Step-by-step architecture explanation with components]
- Component 1 → Component 2 → Component 3 (show the flow)
- Explain what each component does

## Types / Variants
[Different types, models, or approaches used]

## Key Components
- [component]: [what it does]
- [component]: [what it does]

## Workflow
Step 1: [action]
Step 2: [action]
Step 3: [action]

## Use Cases
- [real-world application]
- [real-world application]

## Core Facts
- [important fact]
- [important fact]

IMPORTANT RULES:
- RAG means Retrieval-Augmented Generation (AI technique), NOT fabric rags
- Be specific and technical
- Always show data flow and component relationships
- Keep between 200-350 words
- Do NOT repeat the question"""

    def __init__(self, memory_manager, llm_config=None, agent_config=None):
        import autogen
        from loguru import logger

        self.memory = memory_manager
        self.name   = "ResearchAgent"
        self.role   = "Information Gathering"
        self.logger = logger

        # ✅ FIX: Always read fresh from config module (not stale import)
        import config as _cfg
        llm_config   = _cfg.LLM_CONFIG
        agent_config = _cfg.AGENT_CONFIG
        model_info   = _cfg.get_model_info()

        optimized_llm_config = {
            **llm_config,
            "max_tokens":  600,
            "temperature": 0.2,
            "timeout":     90,
        }

        self.agent = autogen.AssistantAgent(
            name=self.name,
            system_message=self.SYSTEM_MESSAGE,
            llm_config=optimized_llm_config,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

        self.memory_window = 5

        self.logger.info(
            f"🔍 {self.name} | Role: {self.role} | "
            f"Backend: {model_info.get('backend','?')} | "
            f"Model: {model_info.get('model','?')} | "
            f"Memory: {self.memory_window}"
        )

    def process_query(self, user_query: str) -> Dict:
        import autogen

        start_time = time.time()
        self.logger.info(f"🔍 Processing: '{user_query[:50]}...'")

        self.memory.add_message(
            agent_name=self.name, role="user", message=user_query,
            metadata={"stage": "input"},
        )

        # ✅ Smart prompt — detects architecture/workflow queries
        query_lower = user_query.lower()
        is_arch = any(w in query_lower for w in [
            "architecture", "workflow", "how does", "how do", "design",
            "pipeline", "rag", "flow", "diagram", "system", "model",
            "retrieval", "augmented", "generation"
        ])

        if is_arch:
            prompt = (
                f"Provide a detailed technical research on: {user_query}\n\n"
                f"IMPORTANT: Include the complete architecture with component flow, "
                f"step-by-step workflow, types of models/components used, and data flow. "
                f"Be specific and technical. Show the full pipeline."
            )
        else:
            prompt = f"Provide detailed research on: {user_query}"

        user_proxy = autogen.UserProxyAgent(
            name="ResearchUserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
            is_termination_msg=lambda msg: True,
        )

        try:
            chat_result = user_proxy.initiate_chat(
                self.agent, message=prompt, clear_history=True,
            )
            research_content = self._extract_reply(chat_result, prompt)
        except Exception as e:
            self.logger.error(f"Research error: {e}")
            research_content = f"Error during research: {str(e)}"

        elapsed = time.time() - start_time

        self.memory.add_message(
            agent_name=self.name, role="assistant", message=research_content,
            metadata={"stage": "complete", "next": "SummarizerAgent", "time": elapsed},
        )
        self.logger.success(f"✅ Research complete in {elapsed:.2f}s")

        return {
            "agent":           self.name,
            "query":           user_query,
            "output":          research_content,
            "content_length":  len(research_content),
            "processing_time": elapsed,
            "next_agent":      "SummarizerAgent",
        }

    def _extract_reply(self, chat_result, original_prompt: str) -> str:
        try:
            if hasattr(chat_result, "chat_history") and chat_result.chat_history:
                for msg in chat_result.chat_history:
                    if isinstance(msg, dict):
                        role    = msg.get("role", "")
                        name    = msg.get("name", "")
                        content = msg.get("content", "").strip()
                        if name == self.name or (role == "assistant" and name != "ResearchUserProxy"):
                            if content and len(content) > 50:
                                skip = [
                                    "Provide detailed research on:",
                                    "Provide a detailed technical research",
                                    original_prompt[:40] if original_prompt else "",
                                ]
                                if not any(content.startswith(p) for p in skip if p):
                                    return content

            if hasattr(chat_result, "summary") and chat_result.summary:
                s = str(chat_result.summary).strip()
                if s and len(s) > 50:
                    return s

            if hasattr(chat_result, "chat_messages") and chat_result.chat_messages:
                for agent_name, messages in chat_result.chat_messages.items():
                    if agent_name == self.name:
                        for msg in reversed(messages):
                            if isinstance(msg, dict):
                                content = msg.get("content", "").strip()
                                if content and len(content) > 50:
                                    return content

            return "Research completed but response extraction failed."
        except Exception as e:
            return f"Error extracting response: {str(e)}"

    def get_memory(self) -> List[Dict]:
        return self.memory.get_recent_messages(self.name, limit=self.memory_window)

    def get_info(self) -> Dict:
        return {
            "name":          self.name,
            "role":          self.role,
            "memory_window": self.memory_window,
            "memory_count":  len(self.get_memory()),
        }