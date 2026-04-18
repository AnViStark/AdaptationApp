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
    path('users/<int:user_id>/edit/', views.user_edit_view, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete_view, name='user_delete'),
    # Trainer tasks
    path('trainer/', views.trainer_view, name='trainer'),
    path('trainer/create/', views.trainer_task_create_view, name='trainer_create'),
    path('trainer/<int:pk>/edit/', views.trainer_task_edit_view, name='trainer_edit'),
    path('trainer/<int:pk>/delete/', views.trainer_task_delete_view, name='trainer_delete'),
    # Trainer submissions
    path('submissions/', views.submissions_view, name='submissions'),
    # Achievements
    path('achievements/', views.achievements_view, name='achievements'),
    path('achievements/create/', views.achievement_create_view, name='achievement_create'),
    path('achievements/<int:pk>/edit/', views.achievement_edit_view, name='achievement_edit'),
    path('achievements/<int:pk>/delete/', views.achievement_delete_view, name='achievement_delete'),
    path('achievements/<int:pk>/award/', views.achievement_award_view, name='achievement_award'),
    path('achievements/revoke/<int:pk>/', views.achievement_revoke_view, name='achievement_revoke'),
    # Assigned routes
    path('routes/', views.assigned_routes_view, name='assigned_routes'),
    path('routes/<int:pk>/toggle/', views.assigned_route_deactivate_view, name='route_toggle'),
    path('routes/<int:pk>/delete/', views.assigned_route_delete_view, name='route_delete'),
]
