from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path

from config.views import home_view
from users.views import login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', login_required(home_view), name='home'),
    path('adaptation/', include('adaptation.urls')),
    path('routes/', include('adaptation.route_urls')),
    path('knowledge/', include('knowledge.urls')),
    path('assistant/', include('assistant.urls')),
    path('trainer/', include('trainer.urls')),
    path('monitoring/', include('monitoring.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('', include('users.urls')),
    path('', include('gamification.urls')),
]
