"""
LLM Client for DAMAC Finance AI
Handles OpenAI GPT-5 API connections
"""
import os
from functools import lru_cache
from openai import OpenAI
from dotenv import load_dotenv
import structlog

load_dotenv()

logger = structlog.get_logger()


class LLMClient:
    """
    OpenAI GPT-5 client wrapper.

    Handles:
    - API connection
    - Model selection
    - Token management for GPT-5 reasoning models
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=self.api_key)

        # Model configuration
        self.orchestrator_model = os.getenv("OPENAI_MODEL_ORCHESTRATOR", "gpt-5-mini")
        self.agent_model = os.getenv("OPENAI_MODEL_AGENTS", "gpt-5-mini")

        logger.info(
            "llm_client_initialized",
            orchestrator_model=self.orchestrator_model,
            agent_model=self.agent_model,
        )

    def chat_completion(
        self,
        messages: list[dict],
        model: str = None,
        json_response: bool = True,
        max_tokens: int = 2000,
    ) -> dict:
        """
        Make a chat completion request.

        Args:
            messages: List of message dicts with role and content
            model: Model to use (defaults to agent_model)
            json_response: Whether to request JSON output
            max_tokens: Maximum completion tokens (GPT-5 uses this for reasoning + output)

        Returns:
            Response content as dict (if json_response) or str
        """
        import json

        model = model or self.agent_model

        kwargs = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": max_tokens,  # GPT-5 parameter
        }

        if json_response:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content

        # Log usage
        usage = response.usage
        logger.debug(
            "llm_request_complete",
            model=model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            reasoning_tokens=getattr(usage.completion_tokens_details, 'reasoning_tokens', 0),
        )

        if json_response and content:
            return json.loads(content)
        return content or {}


@lru_cache()
def get_llm_client() -> LLMClient:
    """Get singleton LLM client instance."""
    return LLMClient()
