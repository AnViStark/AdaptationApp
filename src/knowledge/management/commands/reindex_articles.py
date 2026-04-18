"""Management command: re-index all knowledge base articles in Chroma.

Run after switching the embedding model or when the Chroma collection
becomes stale / incompatible:

    docker-compose run --rm web python manage.py reindex_articles
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Wipe the Chroma knowledge_base collection and re-index every article.'

    def handle(self, *args, **options):
        from django.conf import settings

        import chromadb

        from knowledge.models import Article
        from knowledge.signals import _do_index, _get_collection

        self.stdout.write('Connecting to ChromaDB …')
        chroma = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)

        # Drop the stale collection so we start fresh
        self.stdout.write('Dropping existing collection …')
        try:
            chroma.delete_collection('knowledge_base')
            self.stdout.write(self.style.SUCCESS('  Collection deleted.'))
        except Exception as e:
            self.stdout.write(f'  Nothing to delete ({e}).')

        # Recreate it
        _get_collection(chroma)
        self.stdout.write('Collection recreated.')

        # Pre-load the embedding model once (avoids repeated log spam)
        self.stdout.write('Loading embedding model — this may take a minute on first run …')
        from knowledge.embeddings import get_embedder
        get_embedder()
        self.stdout.write(self.style.SUCCESS('  Model ready.'))

        articles = list(Article.objects.select_related('category').all())
        self.stdout.write(f'Indexing {len(articles)} article(s) …')

        for article in articles:
            try:
                _do_index(article)
                self.stdout.write(f'  [OK] {article.pk}: {article.title}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  [FAIL] {article.pk}: {article.title} — {e}')
                )

        self.stdout.write(self.style.SUCCESS('Re-indexing complete.'))
