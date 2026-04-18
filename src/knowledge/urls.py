from django.urls import path, re_path

from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('categories/', views.category_list_view, name='category_list'),
    re_path(r'^category/(?P<slug>[-\w]+)/$', views.category_view, name='category'),
    re_path(r'^category/(?P<slug>[-\w]+)/edit/$', views.category_edit_view, name='category_edit'),
    re_path(r'^category/(?P<slug>[-\w]+)/delete/$', views.category_delete_view, name='category_delete'),
    re_path(r'^article/(?P<slug>[-\w]+)/$', views.article_view, name='article'),
    path('create/', views.article_create_view, name='create'),
    re_path(r'^article/(?P<slug>[-\w]+)/edit/$', views.article_edit_view, name='edit'),
    re_path(r'^article/(?P<slug>[-\w]+)/delete/$', views.article_delete_view, name='delete'),
]
