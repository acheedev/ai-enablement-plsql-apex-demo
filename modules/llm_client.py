"""
llm_client.py

Thin wrapper around the LLM provider.

Current implementation:
- Uses OpenAI's Chat Completions API.
- Exposes a single call_llm() function used by the review pipeline.

To switch providers (Azure OpenAI, Bedrock, OCI, etc.), replace the internals
of call_llm() but keep the function signature the same.
"""

import os
from typing import Optional

from openai import OpenAI


# You can change this default model if you like.
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")


# Lazily create a client so import-time failure is less annoying.
_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is not set. "
                "Export it before running the review script."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def call_llm(system_prompt: str, user_prompt: str, model: Optional[str] = None) -> str:
    """
    Call the LLM with a system prompt and user prompt and return the text content.

    - system_prompt: high-level behavioral instructions and role
    - user_prompt: the structured, task-specific prompt (with code, constraints, etc.)
    - model: optional override model name

    Returns:
        The text content of the first message in the response.
    """
    client = _get_client()
    model_name = model or DEFAULT_MODEL

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,  # low for deterministic, engineering-style work
    )

    # We expect a single choice with a text response.
    choice = response.choices[0]
    content = choice.message.content or ""
    return content.strip()
