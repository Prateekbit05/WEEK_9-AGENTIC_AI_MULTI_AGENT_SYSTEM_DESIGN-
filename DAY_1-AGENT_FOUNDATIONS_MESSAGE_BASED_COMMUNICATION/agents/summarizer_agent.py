"""
SUMMARIZER AGENT — FIXED & ENHANCED
======================================
✅ FIX: Reads LLM_CONFIG fresh at init (not stale import)
✅ FIX: System prompt preserves architecture/workflow details
✅ FIX: Does not strip technical content during summarization
"""
from typing import Dict, List
import time


class SummarizerAgent:

    SYSTEM_MESSAGE = """You are an expert SUMMARIZER AGENT specializing in technical content.

Your job is to condense research while PRESERVING all technical details, architecture, and workflow information.

Provide your response in this EXACT format:

## Summary
[2-3 sentences summarizing what this technology/concept is]

## Architecture Flow
[Preserve the architecture flow from the research — show component → component → component]
Example: Query → Retriever → Vector DB → Re-ranker → LLM → Response

## Key Components
1. [Component name]: [what it does]
2. [Component name]: [what it does]
3. [Component name]: [what it does]

## Types / Models Used
- [type or model name]: [brief description]
- [type or model name]: [brief description]

## Key Takeaway
[One sentence capturing the most important insight]

IMPORTANT RULES:
- NEVER remove architecture diagrams or workflow steps
- NEVER simplify technical details into vague statements
- Keep all component names and their relationships
- Keep between 150-250 words
- Do NOT repeat the question"""

    def __init__(self, memory_manager, llm_config=None, agent_config=None):
        import autogen
        from loguru import logger

        self.memory = memory_manager
        self.name   = "SummarizerAgent"
        self.role   = "Information Condensation"
        self.logger = logger

        # ✅ FIX: Always read fresh from config module
        import config as _cfg
        llm_config   = _cfg.LLM_CONFIG
        agent_config = _cfg.AGENT_CONFIG
        model_info   = _cfg.get_model_info()

        optimized_llm_config = {
            **llm_config,
            "max_tokens":  500,
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
            f"📊 {self.name} | Role: {self.role} | "
            f"Backend: {model_info.get('backend','?')} | "
            f"Model: {model_info.get('model','?')} | "
            f"Memory: {self.memory_window}"
        )

    def process_research(self, research_data: Dict) -> Dict:
        import autogen

        research_content = research_data.get("output", "")
        original_query   = research_data.get("query", "")

        start_time = time.time()
        self.logger.info(f"📊 Summarizing: '{original_query[:50]}...'")

        self.memory.add_message(
            agent_name=self.name, role="user", message=research_content,
            metadata={"stage": "input", "from": "ResearchAgent"},
        )

        # ✅ Prompt explicitly asks to keep architecture details
        prompt = (
            f"Summarize the following research about '{original_query}'.\n"
            f"IMPORTANT: Keep all architecture diagrams, component flows, workflow steps, "
            f"and model types. Do not remove technical details:\n\n{research_content}"
        )

        user_proxy = autogen.UserProxyAgent(
            name="SummarizerUserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
            is_termination_msg=lambda msg: True,
        )

        try:
            chat_result = user_proxy.initiate_chat(
                self.agent, message=prompt, clear_history=True,
            )
            summary_content = self._extract_reply(chat_result, prompt)
        except Exception as e:
            self.logger.error(f"Summarize error: {e}")
            summary_content = f"Error: {str(e)}"

        elapsed = time.time() - start_time

        self.memory.add_message(
            agent_name=self.name, role="assistant", message=summary_content,
            metadata={"stage": "complete", "next": "AnswerAgent", "time": elapsed},
        )
        self.logger.success(f"✅ Summary complete in {elapsed:.2f}s")

        return {
            "agent":           self.name,
            "query":           original_query,
            "research":        research_content,
            "output":          summary_content,
            "content_length":  len(summary_content),
            "processing_time": elapsed,
            "next_agent":      "AnswerAgent",
        }

    def _extract_reply(self, chat_result, original_prompt: str) -> str:
        try:
            if hasattr(chat_result, "chat_history") and chat_result.chat_history:
                for msg in chat_result.chat_history:
                    if isinstance(msg, dict):
                        role    = msg.get("role", "")
                        name    = msg.get("name", "")
                        content = msg.get("content", "").strip()
                        if name == self.name or (role == "assistant" and name != "SummarizerUserProxy"):
                            if content and len(content) > 50:
                                skip = [
                                    "Summarize the following",
                                    "Summarize this research",
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

            return "Summary generation failed. Please try again."
        except Exception as e:
            return f"Error: {str(e)}"

    def get_memory(self) -> List[Dict]:
        return self.memory.get_recent_messages(self.name, limit=self.memory_window)

    def get_info(self) -> Dict:
        return {
            "name":          self.name,
            "role":          self.role,
            "memory_window": self.memory_window,
            "memory_count":  len(self.get_memory()),
        }