import markdown as md
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe

from .forms import ArticleForm, CategoryForm
from .models import Article, Category


@login_required
def catalog_view(request):
    query = request.GET.get('q', '').strip()
    categories = Category.objects.prefetch_related('articles').all()
    articles = None
    if query:
        articles = Article.objects.filter(title__icontains=query).select_related('category').order_by('-updated_at')
    return render(request, 'knowledge/catalog.html', {
        'categories': categories,
        'articles': articles,
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
