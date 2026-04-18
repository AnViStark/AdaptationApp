from django.shortcuts import render


def home_view(request):
    context = {}

    if request.user.is_authenticated and request.user.role == 'employee':
        # Пробуем получить прогресс маршрута для виджета
        try:
            from adaptation.models import AdaptationRoute
            route = AdaptationRoute.objects.filter(
                user=request.user, is_active=True
            ).select_related('template').first()
            if route:
                context['route'] = route
                context['route_total'] = route.total_tasks()
                context['route_done'] = route.completed_tasks()
                context['route_percent'] = route.progress_percent()
        except Exception:
            pass

    return render(request, 'home.html', context)
