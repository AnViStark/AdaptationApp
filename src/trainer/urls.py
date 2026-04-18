from django.urls import path

from . import views

app_name = 'trainer'

urlpatterns = [
    path('', views.task_list_view, name='list'),
    path('<int:pk>/', views.task_detail_view, name='detail'),
    path('review/<int:submission_id>/', views.review_view, name='review'),
]
