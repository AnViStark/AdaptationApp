import functools

import requests
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TrainerTaskForm, UserCreateForm
from .models import SystemSettings

User = get_user_model()


def admin_required(view_func):
    """Decorator: login required + role == 'admin'."""
    @functools.wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def index_view(request):
    return render(request, 'admin_panel/index.html')


def _fetch_llm_models(url):
    """Fetch model list from an OpenAI-compatible endpoint. Returns (models, error)."""
    try:
        resp = requests.get(f'{url}/v1/models', timeout=5)
        resp.raise_for_status()
        data = resp.json()
        # OpenAI / LM Studio format
        if 'data' in data:
            return [m['id'] for m in data['data']], None
        # Ollama native format
        if 'models' in data:
            return [m['name'] for m in data['models']], None
        return [], None
    except Exception as e:
        return [], str(e)


@admin_required
def settings_view(request):
    current = {
        'ollama_model': SystemSettings.get('ollama_model', ''),
        'embedding_model': SystemSettings.get('embedding_model', ''),
        'points_per_task': SystemSettings.get('points_per_task', '10'),
        'llm_backend': SystemSettings.get('llm_backend', 'ollama'),
    }

    if request.method == 'POST':
        llm_backend = request.POST.get('llm_backend', 'ollama')
        if llm_backend in ('ollama', 'lmstudio'):
            SystemSettings.set('llm_backend', llm_backend)
            current['llm_backend'] = llm_backend

        ollama_model = request.POST.get('ollama_model', '').strip()
        embedding_model = request.POST.get('embedding_model', '').strip()
        points_per_task = request.POST.get('points_per_task', '10').strip()

        if ollama_model:
            SystemSettings.set('ollama_model', ollama_model)
        if embedding_model:
            SystemSettings.set('embedding_model', embedding_model)
        if points_per_task.isdigit() and int(points_per_task) > 0:
            SystemSettings.set('points_per_task', points_per_task)

        messages.success(request, 'Настройки сохранены.')
        return redirect('admin_panel:settings')

    llm_url = settings.LM_STUDIO_URL if current['llm_backend'] == 'lmstudio' else settings.OLLAMA_URL
    available_models, llm_error = _fetch_llm_models(llm_url)

    backend_label = 'LM Studio' if current['llm_backend'] == 'lmstudio' else 'Ollama'
    if llm_error:
        llm_error = f'Не удалось получить список моделей {backend_label}: {llm_error}'

    return render(request, 'admin_panel/settings.html', {
        'current': current,
        'available_models': available_models,
        'ollama_error': llm_error,
        'ollama_url': settings.OLLAMA_URL,
        'lm_studio_url': settings.LM_STUDIO_URL,
    })


# ─── Users management ────────────────────────────────────────────────────────

@admin_required
def users_view(request):
    users = User.objects.all().order_by('last_name', 'first_name')
    form = UserCreateForm()

    if request.method == 'POST' and 'create_user' in request.POST:
        form = UserCreateForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            user = User.objects.create_user(
                username=d['username'],
                email=d['email'],
                password=d['password'],
                first_name=d['first_name'],
                last_name=d['last_name'],
                role=d['role'],
                department=d.get('department', ''),
            )
            messages.success(request, f'Пользователь {user} создан.')
            return redirect('admin_panel:users')

    return render(request, 'admin_panel/users.html', {'users': users, 'form': form})


@admin_required
def user_toggle_active_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST' and user != request.user:
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        status = 'активирован' if user.is_active else 'деактивирован'
        messages.success(request, f'Пользователь {user} {status}.')
    return redirect('admin_panel:users')


@admin_required
def user_role_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST' and user != request.user:
        new_role = request.POST.get('role')
        if new_role in dict(User.Role.choices):
            user.role = new_role
            user.save(update_fields=['role'])
            messages.success(request, f'Роль пользователя {user} изменена на «{user.get_role_display()}».')
    return redirect('admin_panel:users')


# ─── Trainer tasks management ─────────────────────────────────────────────────

@admin_required
def trainer_view(request):
    from trainer.models import TrainerTask
    tasks = TrainerTask.objects.all()
    return render(request, 'admin_panel/trainer.html', {'tasks': tasks})


@admin_required
def trainer_task_create_view(request):
    if request.method == 'POST':
        form = TrainerTaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задание создано.')
            return redirect('admin_panel:trainer')
    else:
        form = TrainerTaskForm()
    return render(request, 'admin_panel/trainer_form.html', {
        'form': form, 'page_title': 'Новое задание тренажёра',
    })


@admin_required
def trainer_task_edit_view(request, pk):
    from trainer.models import TrainerTask
    task = get_object_or_404(TrainerTask, pk=pk)
    if request.method == 'POST':
        form = TrainerTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задание обновлено.')
            return redirect('admin_panel:trainer')
    else:
        form = TrainerTaskForm(instance=task)
    return render(request, 'admin_panel/trainer_form.html', {
        'form': form, 'page_title': 'Редактировать задание', 'task': task,
    })


@admin_required
def trainer_task_delete_view(request, pk):
    from trainer.models import TrainerTask
    task = get_object_or_404(TrainerTask, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Задание удалено.')
    return redirect('admin_panel:trainer')
