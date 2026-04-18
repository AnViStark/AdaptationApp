"""Embedding helpers using intfloat/multilingual-e5-large.

The model is loaded lazily on first use and cached in memory for the
lifetime of the process.  Use the 'passage:' / 'query:' prefixes as
recommended by the e5 paper for best retrieval quality.
"""

import logging
import threading

logger = logging.getLogger(__name__)

MODEL_NAME = 'intfloat/multilingual-e5-large'

_embedder = None
_lock = threading.Lock()


def get_embedder():
    global _embedder
    if _embedder is None:
        with _lock:
            if _embedder is None:
                from sentence_transformers import SentenceTransformer
                logger.info('Loading embedding model %s …', MODEL_NAME)
                _embedder = SentenceTransformer(MODEL_NAME)
                logger.info('Embedding model loaded.')
    return _embedder


def embed_passage(text: str) -> list:
    """Embed a document chunk for storage in Chroma."""
    return get_embedder().encode(
        f'passage: {text}',
        normalize_embeddings=True,
    ).tolist()


def embed_query(text: str) -> list:
    """Embed a user question for similarity search."""
    return get_embedder().encode(
        f'query: {text}',
        normalize_embeddings=True,
    ).tolist()
