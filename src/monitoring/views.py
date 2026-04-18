from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Max
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from adaptation.models import AdaptationRoute, UserTaskProgress

User = get_user_model()


@login_required
def monitoring_view(request):
    if request.user.role not in ('hr', 'admin'):
        raise PermissionDenied

    department_filter = request.GET.get('department', '').strip()

    employees = User.objects.filter(role='employee', is_active=True).order_by('last_name', 'first_name')
    if department_filter:
        employees = employees.filter(department__icontains=department_filter)

    departments = User.objects.filter(role='employee').values_list('department', flat=True).distinct().order_by('department')

    rows = []
    for emp in employees:
        route = AdaptationRoute.objects.filter(user=emp, is_active=True).select_related('template', 'mentor').first()
        if route:
            progress = route.progress_percent()
            mentor = route.mentor
            started_at = route.started_at
            days_in_system = (timezone.now().date() - started_at).days if started_at else None
            last_activity = UserTaskProgress.objects.filter(
                route=route, completed=True,
            ).aggregate(last=Max('completed_at'))['last']
        else:
            progress = 0
            mentor = None
            started_at = None
            days_in_system = None
            last_activity = None

        rows.append({
            'user': emp,
            'route': route,
            'progress': progress,
            'mentor': mentor,
            'days_in_system': days_in_system,
            'last_activity': last_activity,
        })

    return render(request, 'monitoring/monitoring.html', {
        'rows': rows,
        'departments': [d for d in departments if d],
        'department_filter': department_filter,
    })


@login_required
def employee_detail_view(request, user_id):
    if request.user.role not in ('hr', 'admin'):
        raise PermissionDenied
    employee = get_object_or_404(User, pk=user_id, role='employee')
    route = AdaptationRoute.objects.filter(user=employee, is_active=True).select_related('template', 'mentor').first()

    stages_data = []
    if route:
        for stage in route.template.stages.prefetch_related('tasks').all():
            task_rows = []
            for task in stage.tasks.all():
                progress = route.task_progress.filter(task=task).first()
                task_rows.append({
                    'task': task,
                    'completed': progress.completed if progress else False,
                    'completed_at': progress.completed_at if progress else None,
                })
            done = sum(1 for t in task_rows if t['completed'])
            stages_data.append({
                'stage': stage,
                'tasks': task_rows,
                'done': done,
                'total': len(task_rows),
            })

    return render(request, 'monitoring/employee_detail.html', {
        'employee': employee,
        'route': route,
        'stages_data': stages_data,
    })
