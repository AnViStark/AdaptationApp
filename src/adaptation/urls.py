from django.urls import path

from . import views

app_name = 'adaptation'

urlpatterns = [
    path('', views.adaptation_view, name='index'),
    path('complete/<int:task_id>/', views.complete_task_view, name='complete_task'),
]
