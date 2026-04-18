import sys

from django.apps import AppConfig


class KnowledgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knowledge'
    verbose_name = 'База знаний'

    def ready(self):
        import knowledge.signals  # noqa: F401

        # Pre-warm the embedding model when running the web server so the
        # first user request doesn't freeze.  Skip for management commands
        # (migrate, seed_demo, reindex_articles, etc.) to avoid a pointless
        # 1.3 GB load during CLI operations.
        if len(sys.argv) >= 2 and sys.argv[1] == 'runserver':
            import threading

            def _warmup():
                try:
                    import logging
                    from knowledge.embeddings import get_embedder
                    logging.getLogger(__name__).info(
                        'Pre-warming multilingual-e5-large …'
                    )
                    get_embedder()
                    logging.getLogger(__name__).info('Embedding model ready.')
                except Exception as exc:
                    import logging
                    logging.getLogger(__name__).warning(
                        'Model warmup failed: %s', exc
                    )

            threading.Thread(
                target=_warmup, daemon=True, name='embedder-warmup'
            ).start()
