from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import AdaptationRoute, UserTaskProgress


def _get_active_route(user):
    """Возвращает активный маршрут пользователя или None."""
    return AdaptationRoute.objects.filter(user=user, is_active=True).select_related('template', 'mentor').first()


def _build_stages_data(route):
    """
    Собирает список этапов с заданиями и прогрессом.
    Возвращает (stages_data, current_stage_data).
    """
    all_stages = route.template.stages.prefetch_related('tasks').all()
    progress_map = {
        p.task_id: p
        for p in UserTaskProgress.objects.filter(route=route)
    }

    stages_data = []
    current_stage = None

    for stage in all_stages:
        tasks_data = []
        for task in stage.tasks.all():
            prog = progress_map.get(task.id)
            tasks_data.append({
                'task': task,
                'progress': prog,
                'completed': prog.completed if prog else False,
            })

        total = len(tasks_data)
        done = sum(1 for t in tasks_data if t['completed'])
        percent = round(done / total * 100) if total > 0 else 0

        if total > 0 and done == total:
            status = 'done'
        elif done > 0:
            status = 'current'
        else:
            status = 'pending'

        stage_dict = {
            'stage': stage,
            'tasks': tasks_data,
            'total': total,
            'done': done,
            'percent': percent,
            'status': status,
        }
        stages_data.append(stage_dict)

        if current_stage is None and status in ('current', 'pending'):
            current_stage = stage_dict

    # Если все этапы завершены — показываем последний как «завершённый»
    if current_stage is None and stages_data:
        current_stage = stages_data[-1]

    return stages_data, current_stage


def _get_points_per_task():
    try:
        from admin_panel.models import SystemSettings
        setting = SystemSettings.objects.filter(key='points_per_task').first()
        if setting:
            return int(setting.value)
    except Exception:
        pass
    return 10


def _calculate_level(points):
    """Уровень растёт каждые 100 баллов."""
    return max(1, points // 100 + 1)


@login_required
def adaptation_view(request):
    route = _get_active_route(request.user)

    if route is None:
        return render(request, 'adaptation/no_route.html')

    stages_data, current_stage = _build_stages_data(route)

    context = {
        'route': route,
        'stages_data': stages_data,
        'current_stage': current_stage,
        'total_tasks': route.total_tasks(),
        'completed_tasks': route.completed_tasks(),
        'progress_percent': route.progress_percent(),
    }
    return render(request, 'adaptation/adaptation.html', context)


@require_POST
@login_required
def complete_task_view(request, task_id):
    """AJAX-эндпоинт: отмечает задание выполненным и начисляет баллы."""
    route = _get_active_route(request.user)
    if route is None:
        return JsonResponse({'error': 'Маршрут не найден'}, status=404)

    progress = get_object_or_404(UserTaskProgress, route=route, task_id=task_id)

    if progress.completed:
        return JsonResponse({
            'already_done': True,
            'points': request.user.points,
            'level': request.user.level,
        })

    # Отмечаем выполненным
    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save(update_fields=['completed', 'completed_at'])

    # Начисляем баллы
    pts = _get_points_per_task()
    user = request.user
    user.points += pts
    user.level = _calculate_level(user.points)
    user.save(update_fields=['points', 'level'])

    return JsonResponse({
        'success': True,
        'points': user.points,
        'level': user.level,
        'points_added': pts,
    })
