import logging
import threading

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender='knowledge.Article')
def index_article_in_chroma(sender, instance, **kwargs):
    """Re-index article in Chroma in a background thread.

    Running in a thread means the HTTP response returns immediately after
    article.save() — the user doesn't wait for embedding inference.
    """
    thread = threading.Thread(
        target=_do_index_safe,
        args=(instance.pk,),
        daemon=False,
        name=f'chroma-index-{instance.pk}',
    )
    thread.start()


def _do_index_safe(article_pk):
    """Load a fresh Article instance inside the thread, then index."""
    try:
        from knowledge.models import Article
        article = Article.objects.select_related('category').get(pk=article_pk)
        _do_index(article)
    except Exception as e:
        logger.warning('Chroma indexing failed for article %s: %s', article_pk, e)


def _get_collection(chroma):
    """Get or create the knowledge_base collection.

    ChromaDB 0.5.x raises KeyError('_type') when a collection was created
    with a different embedding function than the one passed now.  We catch
    that and nuke the stale collection so it can be rebuilt cleanly.
    """
    try:
        return chroma.get_or_create_collection(
            'knowledge_base',
            metadata={'hnsw:space': 'cosine'},
        )
    except (KeyError, Exception):
        logger.warning('Collection incompatible — recreating knowledge_base.')
        try:
            chroma.delete_collection('knowledge_base')
        except Exception:
            pass
        return chroma.create_collection(
            'knowledge_base',
            metadata={'hnsw:space': 'cosine'},
        )


def _do_index(article):
    from django.conf import settings

    import chromadb

    from .embeddings import embed_passage

    chroma = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collection = _get_collection(chroma)

    # Remove old chunks for this article before re-indexing
    try:
        collection.delete(where={'article_id': str(article.pk)})
    except Exception:
        pass

    text = f'{article.title}\n\n{article.content}'
    chunks = _split_text(text)
    if not chunks:
        return

    ids, embeddings, documents, metadatas = [], [], [], []
    for i, chunk in enumerate(chunks):
        ids.append(f'article_{article.pk}_chunk_{i}')
        embeddings.append(embed_passage(chunk))
        documents.append(chunk)
        metadatas.append({
            'article_id': str(article.pk),
            'article_title': article.title,
            'article_slug': article.slug,
        })

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    logger.info('Indexed article %s "%s" (%d chunks)', article.pk, article.title, len(chunks))


def _split_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start >= len(text):
            break
    return [c for c in chunks if c.strip()]
