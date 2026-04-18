from django.urls import path

from . import route_views as views

app_name = 'routes'

urlpatterns = [
    path('', views.route_list_view, name='list'),
    path('create/', views.route_create_view, name='create'),
    path('<int:pk>/edit/', views.route_edit_view, name='edit'),
    path('<int:pk>/delete/', views.route_delete_view, name='delete'),
    path('assign/', views.route_assign_view, name='assign'),
    # Stage management
    path('stage/add/<int:template_pk>/', views.stage_create_view, name='stage_create'),
    path('stage/<int:pk>/delete/', views.stage_delete_view, name='stage_delete'),
    path('stage/<int:pk>/move/<str:direction>/', views.stage_move_view, name='stage_move'),
    # Task management
    path('task/add/<int:stage_pk>/', views.task_create_view, name='task_create'),
    path('task/<int:pk>/delete/', views.task_delete_view, name='task_delete'),
]
