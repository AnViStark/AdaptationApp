from django.urls import path

from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('settings/', views.settings_view, name='settings'),
    # Users
    path('users/', views.users_view, name='users'),
    path('users/<int:user_id>/toggle/', views.user_toggle_active_view, name='user_toggle'),
    path('users/<int:user_id>/role/', views.user_role_view, name='user_role'),
    # Trainer tasks
    path('trainer/', views.trainer_view, name='trainer'),
    path('trainer/create/', views.trainer_task_create_view, name='trainer_create'),
    path('trainer/<int:pk>/edit/', views.trainer_task_edit_view, name='trainer_edit'),
    path('trainer/<int:pk>/delete/', views.trainer_task_delete_view, name='trainer_delete'),
]
