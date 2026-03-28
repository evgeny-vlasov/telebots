"""
bots/anglers/rag_config.py
RAG settings for the Alberta Anglers Guide bot.
"""

TOP_K_CHUNKS = 6
SIMILARITY_THRESHOLD = 0.25   # Lower than default — fishing terms are domain-specific
CHUNK_SIZE = 350
CHUNK_OVERLAP = 60
VOYAGE_MODEL = "voyage-3-lite"
EMBEDDING_DIMENSION = 512
