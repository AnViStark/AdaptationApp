from django.contrib import admin

from .models import Article, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by', 'updated_at')
    list_filter = ('category',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
