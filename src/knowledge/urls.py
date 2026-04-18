from django.urls import path, re_path

from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    re_path(r'^category/(?P<slug>[-\w]+)/$', views.category_view, name='category'),
    re_path(r'^article/(?P<slug>[-\w]+)/$', views.article_view, name='article'),
    path('create/', views.article_create_view, name='create'),
    re_path(r'^article/(?P<slug>[-\w]+)/edit/$', views.article_edit_view, name='edit'),
]
