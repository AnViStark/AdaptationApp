import logging

import markdown as md
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe

from .forms import ArticleForm, CategoryForm
from .models import Article, Category

logger = logging.getLogger(__name__)


def _clean_snippet(text: str, max_len: int = 220) -> str:
    """Trim whitespace and truncate chunk text for display."""
    text = ' '.join(text.split())
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] + '…'
    return text


def _semantic_search(query: str, n: int = 5, distance_threshold: float = 0.25,
                     relative_gap: int = 3, exclude_pks: set = None):
    """Search via ChromaDB embeddings.

    Returns list of dicts:
        {'article': Article, 'similarity': int (0-100), 'snippet': str}

    distance_threshold: absolute cosine distance cutoff (lower = stricter).
    relative_gap: max percentage-point drop from the top result allowed.
                  E.g. top=81%, gap=3 → cutoff=78%; results at 77% are dropped.
    exclude_pks: PKs already in keyword results — shown there instead.
    """
    try:
        import chromadb
        from django.conf import settings

        from knowledge.embeddings import embed_query
        from knowledge.signals import _get_collection

        query_embedding = embed_query(query)
        chroma = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        collection = _get_collection(chroma)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n * 4, 40),
            include=['metadatas', 'distances', 'documents'],
        )
        metas     = results['metadatas'][0] if results['metadatas']  else []
        distances = results['distances'][0] if results['distances']  else []
        documents = results['documents'][0] if results['documents']  else []

        exclude_pks = exclude_pks or set()
        seen_pks: dict[int, dict] = {}  # pk → {dist, snippet}

        for meta, dist, doc in zip(metas, distances, documents):
            if dist > distance_threshold:
                continue
            pk_str = meta.get('article_id')
            if not pk_str:
                continue
            pk = int(pk_str)
            if pk in exclude_pks or pk in seen_pks:
                continue
            seen_pks[pk] = {'dist': dist, 'snippet': _clean_snippet(doc)}
            if len(seen_pks) >= n:
                break

        if not seen_pks:
            return []

        # Relative gap filter: keep only results within `relative_gap`% of the top score
        best_sim = round((1 - min(info['dist'] for info in seen_pks.values())) * 100)
        cutoff_sim = best_sim - relative_gap

        articles_by_pk = {
            a.pk: a
            for a in Article.objects.filter(pk__in=seen_pks).select_related('category')
        }
        return [
            {
                'article': articles_by_pk[pk],
                'similarity': round((1 - info['dist']) * 100),
                'snippet': info['snippet'],
            }
            for pk, info in seen_pks.items()
            if pk in articles_by_pk
            and round((1 - info['dist']) * 100) > cutoff_sim
        ]
    except Exception as e:
        logger.debug('Semantic search unavailable: %s', e)
        return []


@login_required
def catalog_view(request):
    query = request.GET.get('q', '').strip()
    categories = Category.objects.prefetch_related('articles').all()

    text_articles = None
    semantic_articles = None

    if query:
        # Keyword search: exact matches in title and content
        text_articles = list(
            Article.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).select_related('category').order_by('-updated_at')[:20]
        )
        text_pks = {a.pk for a in text_articles}

        # Semantic search: meaning-based, excludes keyword matches to avoid duplicates
        semantic_articles = _semantic_search(
            query, n=5, distance_threshold=0.25, relative_gap=3, exclude_pks=text_pks
        )

    return render(request, 'knowledge/catalog.html', {
        'categories': categories,
        'text_articles': text_articles,
        'semantic_articles': semantic_articles,
        'query': query,
    })


@login_required
def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = category.articles.select_related('created_by').order_by('-updated_at')
    return render(request, 'knowledge/category.html', {
        'category': category,
        'articles': articles,
    })


@login_required
def article_view(request, slug):
    article = get_object_or_404(Article, slug=slug)
    content_html = mark_safe(md.markdown(article.content, extensions=['extra', 'toc']))
    can_edit = request.user.role in ('admin', 'hr')
    return render(request, 'knowledge/article.html', {
        'article': article,
        'content_html': content_html,
        'can_edit': can_edit,
    })


@login_required
def article_create_view(request):
    if request.user.role not in ('admin', 'hr'):
        raise PermissionDenied
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.created_by = request.user
            article.save()
            messages.success(request, 'Статья создана.')
            return redirect('knowledge:article', slug=article.slug)
    else:
        form = ArticleForm()
    return render(request, 'knowledge/article_form.html', {
        'form': form,
        'page_title': 'Новая статья',
    })


@login_required
def article_edit_view(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.user.role not in ('admin', 'hr'):
        raise PermissionDenied
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья обновлена.')
            return redirect('knowledge:article', slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'knowledge/article_form.html', {
        'form': form,
        'page_title': 'Редактировать статью',
        'article': article,
    })


@login_required
def article_delete_view(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.user.role not in ('admin', 'hr'):
        raise PermissionDenied
    if request.method == 'POST':
        category_slug = article.category.slug
        article.delete()
        messages.success(request, 'Статья удалена.')
        return redirect('knowledge:category', slug=category_slug)
    return render(request, 'knowledge/article_confirm_delete.html', {'article': article})


@login_required
def category_list_view(request):
    if request.user.role not in ('admin', 'hr'):
        raise PermissionDenied
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория создана.')
            return redirect('knowledge:category_list')
    categories = Category.objects.all().order_by('name')
    return render(request, 'knowledge/category_list.html', {
        'categories': categories,
        'form': form,
    })


@login_required
def category_edit_view(request, slug):
    if request.user.role not in ('admin', 'hr'):
        raise PermissionDenied
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория обновлена.')
            return redirect('knowledge:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'knowledge/category_form.html', {
        'form': form, 'category': category, 'page_title': 'Редактировать категорию',
    })


@login_required
def category_delete_view(request, slug):
    if request.user.role not in ('admin', 'hr'):
        raise PermissionDenied
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        if category.articles.exists():
            messages.error(request, 'Нельзя удалить категорию со статьями. Сначала удалите или перенесите статьи.')
            return redirect('knowledge:category_list')
        category.delete()
        messages.success(request, 'Категория удалена.')
        return redirect('knowledge:category_list')
    return render(request, 'knowledge/category_confirm_delete.html', {'category': category})
