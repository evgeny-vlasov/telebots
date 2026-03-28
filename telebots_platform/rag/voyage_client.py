"""
platform/rag/voyage_client.py
Voyage AI embeddings — same model as bot-army (voyage-3-lite, 512D).
"""
import voyageai
from ..config import PlatformConfig

_client = None


def get_client() -> voyageai.Client:
    global _client
    if _client is None:
        _client = voyageai.Client(api_key=PlatformConfig.VOYAGE_API_KEY)
    return _client


def embed(texts: list[str], input_type: str = "document") -> list[list[float]]:
    """Embed a list of texts. input_type: 'document' or 'query'."""
    result = get_client().embed(texts, model="voyage-3-lite", input_type=input_type)
    return result.embeddings
