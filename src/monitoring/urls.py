from django.urls import path

from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.monitoring_view, name='index'),
    path('employee/<int:user_id>/', views.employee_detail_view, name='employee_detail'),
]
