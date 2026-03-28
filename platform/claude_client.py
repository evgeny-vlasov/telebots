"""
platform/claude_client.py
Thin wrapper around the Anthropic client.
"""
import anthropic
from .config import PlatformConfig

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=PlatformConfig.ANTHROPIC_API_KEY)
    return _client


def chat(system_prompt: str, messages: list, model: str = "claude-sonnet-4-5",
         max_tokens: int = 1024) -> str:
    """Single-turn or multi-turn chat. Returns assistant text."""
    response = get_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text
