from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('mentees/', views.mentees_view, name='mentees'),
    path('mentees/<int:user_id>/', views.mentee_detail_view, name='mentee_detail'),
]
