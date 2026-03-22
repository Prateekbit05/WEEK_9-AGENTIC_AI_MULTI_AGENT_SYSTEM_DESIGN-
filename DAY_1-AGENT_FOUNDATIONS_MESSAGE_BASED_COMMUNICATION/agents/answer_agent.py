"""
ANSWER AGENT — FIXED & ENHANCED
==================================
✅ FIX: Reads LLM_CONFIG fresh at init (not stale import)
✅ FIX: System prompt produces full structured technical answers
✅ FIX: Produces architecture workflow + model types in final answer
"""
from typing import Dict, List
import time


class AnswerAgent:

    SYSTEM_MESSAGE = """You are an expert ANSWER AGENT specializing in AI systems, software architecture, and technology.

Your job is to produce a COMPLETE, PROFESSIONAL, and TECHNICALLY DETAILED final answer.

Structure your answer EXACTLY like this:

# [Topic Title]

## What Is It?
[2-3 sentences clearly explaining the concept]

## Architecture & Workflow
[Show the complete data/process flow using arrows]
Example:
User Query → Embedding Model → Vector Database → Retrieved Docs → LLM → Final Answer

Explain each step:
1. Step name: [what happens here, which component, which model type]
2. Step name: [what happens here, which component, which model type]
3. Step name: [what happens here, which component, which model type]

## Types of Models Used
| Component | Model Type | Examples |
|-----------|-----------|---------|
| Embedding | Sentence Transformer | all-MiniLM, text-embedding-ada |
| Retrieval | Dense/Sparse/Hybrid | FAISS, BM25, Pinecone |
| Generator | LLM | GPT-4, Claude, Llama |

## Key Components
- **[Component]**: [what it does and why it matters]
- **[Component]**: [what it does and why it matters]
- **[Component]**: [what it does and why it matters]

## Advantages
- [advantage with brief explanation]
- [advantage with brief explanation]

## Takeaway
[One powerful sentence summarizing the most important insight]

IMPORTANT RULES:
- RAG = Retrieval-Augmented Generation (AI), not fabric
- Always show complete architecture with data flow arrows (→)
- Always include model types table when relevant
- Be specific — use real model names and component names
- Aim for 300-450 words
- Do NOT repeat the question"""

    def __init__(self, memory_manager, llm_config=None, agent_config=None):
        import autogen
        from loguru import logger

        self.memory = memory_manager
        self.name   = "AnswerAgent"
        self.role   = "Final Response Generation"
        self.logger = logger

        # ✅ FIX: Always read fresh from config module
        import config as _cfg
        llm_config   = _cfg.LLM_CONFIG
        agent_config = _cfg.AGENT_CONFIG
        model_info   = _cfg.get_model_info()

        optimized_llm_config = {
            **llm_config,
            "max_tokens":  800,
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
            f"💬 {self.name} | Role: {self.role} | "
            f"Backend: {model_info.get('backend','?')} | "
            f"Model: {model_info.get('model','?')} | "
            f"Memory: {self.memory_window}"
        )

    def generate_answer(self, summary_data: Dict) -> Dict:
        import autogen

        summary_content = summary_data.get("output", "")
        original_query  = summary_data.get("query", "")

        start_time = time.time()
        self.logger.info(f"💬 Generating answer for: '{original_query[:50]}...'")

        self.memory.add_message(
            agent_name=self.name, role="user", message=summary_content,
            metadata={"stage": "input", "from": "SummarizerAgent"},
        )

        # ✅ Prompt that forces architecture + workflow output
        query_lower = original_query.lower()
        is_arch = any(w in query_lower for w in [
            "architecture", "workflow", "how does", "how do", "design",
            "pipeline", "rag", "flow", "diagram", "system", "model",
            "retrieval", "augmented", "generation"
        ])

        if is_arch:
            prompt = (
                f"Generate a comprehensive technical answer about: '{original_query}'\n\n"
                f"Based on this research:\n{summary_content}\n\n"
                f"REQUIREMENTS:\n"
                f"1. Show the complete architecture with data flow (use → arrows)\n"
                f"2. Include a table of model types used at each stage\n"
                f"3. Explain each workflow step in detail\n"
                f"4. Include real component names and model examples\n"
                f"5. Be thorough and technically accurate"
            )
        else:
            prompt = (
                f"Generate a comprehensive answer about '{original_query}' "
                f"based on this information:\n\n{summary_content}"
            )

        user_proxy = autogen.UserProxyAgent(
            name="AnswerUserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
            is_termination_msg=lambda msg: True,
        )

        try:
            chat_result = user_proxy.initiate_chat(
                self.agent, message=prompt, clear_history=True,
            )
            final_answer = self._extract_reply(chat_result, prompt)
        except Exception as e:
            self.logger.error(f"Answer error: {e}")
            final_answer = f"Error: {str(e)}"

        elapsed = time.time() - start_time

        self.memory.add_message(
            agent_name=self.name, role="assistant", message=final_answer,
            metadata={"stage": "complete", "delivered": True, "time": elapsed},
        )
        self.logger.success(f"✅ Answer complete in {elapsed:.2f}s ✅ DELIVERED")

        return {
            "agent":           self.name,
            "query":           original_query,
            "output":          final_answer,
            "content_length":  len(final_answer),
            "processing_time": elapsed,
            "status":          "delivered",
        }

    def _extract_reply(self, chat_result, original_prompt: str) -> str:
        try:
            if hasattr(chat_result, "chat_history") and chat_result.chat_history:
                for msg in chat_result.chat_history:
                    if isinstance(msg, dict):
                        role    = msg.get("role", "")
                        name    = msg.get("name", "")
                        content = msg.get("content", "").strip()
                        if name == self.name or (role == "assistant" and name != "AnswerUserProxy"):
                            if content and len(content) > 50:
                                skip = [
                                    "Generate a comprehensive answer",
                                    "Generate a comprehensive technical",
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

            return "Answer generation failed. Please try again."
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