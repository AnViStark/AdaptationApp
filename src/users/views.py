from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        error = 'Неверный email или пароль.'

    return render(request, 'registration/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    from django.contrib.auth import update_session_auth_hash
    user = request.user
    pw_error = None
    pw_success = False

    if request.method == 'POST' and 'change_password' in request.POST:
        old_pw = request.POST.get('old_password', '')
        new_pw = request.POST.get('new_password', '')
        new_pw2 = request.POST.get('new_password2', '')
        if not user.check_password(old_pw):
            pw_error = 'Неверный текущий пароль.'
        elif new_pw != new_pw2:
            pw_error = 'Новые пароли не совпадают.'
        elif len(new_pw) < 8:
            pw_error = 'Пароль должен содержать не менее 8 символов.'
        else:
            user.set_password(new_pw)
            user.save()
            update_session_auth_hash(request, user)
            pw_success = True

    ctx = {'user_obj': user, 'pw_error': pw_error, 'pw_success': pw_success}

    if user.role == 'employee':
        from adaptation.models import AdaptationRoute, UserTaskProgress
        from gamification.models import UserAchievement
        route = AdaptationRoute.objects.filter(user=user, is_active=True).select_related('template', 'mentor').first()
        achievements = UserAchievement.objects.filter(user=user).select_related('achievement').order_by('-earned_at')
        recent_tasks = UserTaskProgress.objects.filter(
            route__user=user, completed=True,
        ).select_related('task').order_by('-completed_at')[:10]
        ctx.update({'route': route, 'achievements': achievements, 'recent_tasks': recent_tasks})

    elif user.role == 'mentor':
        from adaptation.models import AdaptationRoute
        mentees = AdaptationRoute.objects.filter(mentor=user, is_active=True).select_related('user')
        ctx['mentees'] = mentees

    return render(request, 'users/profile.html', ctx)


@login_required
def mentees_view(request):
    if request.user.role != 'mentor':
        raise PermissionDenied
    from adaptation.models import AdaptationRoute
    routes = (
        AdaptationRoute.objects
        .filter(mentor=request.user, is_active=True)
        .select_related('user', 'template')
        .order_by('user__first_name', 'user__last_name')
    )
    mentees_data = []
    for route in routes:
        mentees_data.append({
            'route': route,
            'user': route.user,
            'percent': route.progress_percent(),
            'done': route.completed_tasks(),
            'total': route.total_tasks(),
        })
    return render(request, 'users/mentees.html', {'mentees_data': mentees_data})


@login_required
def mentee_detail_view(request, user_id):
    if request.user.role != 'mentor':
        raise PermissionDenied
    from adaptation.models import AdaptationRoute
    from trainer.models import TrainerSubmission

    # Only show if this user is actually a mentee of current mentor
    route = get_object_or_404(
        AdaptationRoute.objects.select_related('user', 'template', 'mentor'),
        user_id=user_id,
        mentor=request.user,
        is_active=True,
    )
    employee = route.user

    # Build stage progress (read-only)
    stages_data = []
    for stage in route.template.stages.prefetch_related('tasks').all():
        task_rows = []
        for task in stage.tasks.all():
            progress = route.task_progress.filter(task=task).first()
            task_rows.append({
                'task': task,
                'completed': progress.completed if progress else False,
                'completed_at': progress.completed_at if progress else None,
            })
        done_count = sum(1 for t in task_rows if t['completed'])
        stages_data.append({
            'stage': stage,
            'tasks': task_rows,
            'done': done_count,
            'total': len(task_rows),
        })

    # Pending trainer submissions
    pending_submissions = TrainerSubmission.objects.filter(
        user=employee,
        status=TrainerSubmission.Status.PENDING,
    ).select_related('task').order_by('-submitted_at')

    # Reviewed submissions
    reviewed_submissions = TrainerSubmission.objects.filter(
        user=employee,
    ).exclude(
        status=TrainerSubmission.Status.PENDING,
    ).select_related('task', 'review').order_by('-submitted_at')[:5]

    return render(request, 'users/mentee_detail.html', {
        'employee': employee,
        'route': route,
        'stages_data': stages_data,
        'pending_submissions': pending_submissions,
        'reviewed_submissions': reviewed_submissions,
    })
