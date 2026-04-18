import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import RouteAssignForm, StageForm, TaskForm, TemplateForm
from .models import AdaptationRoute, AdaptationTemplate, Stage, Task, UserTaskProgress


def _hr_required(view_func):
    import functools

    @functools.wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role not in ('hr', 'admin'):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


# ─── Templates list ─────────────────────────────────────────────────────────

@_hr_required
def route_list_view(request):
    templates = AdaptationTemplate.objects.select_related('created_by').all()
    return render(request, 'adaptation/routes/route_list.html', {'templates': templates})


# ─── Create template ────────────────────────────────────────────────────────

@_hr_required
def route_create_view(request):
    if request.method == 'POST':
        form = TemplateForm(request.POST)
        if form.is_valid():
            tmpl = form.save(commit=False)
            tmpl.created_by = request.user
            tmpl.save()
            messages.success(request, 'Шаблон создан. Добавьте этапы.')
            return redirect('routes:edit', pk=tmpl.pk)
    else:
        form = TemplateForm()
    return render(request, 'adaptation/routes/route_form.html', {
        'form': form,
        'page_title': 'Новый шаблон',
    })


# ─── Edit template ───────────────────────────────────────────────────────────

@_hr_required
def route_edit_view(request, pk):
    from knowledge.models import Article
    from trainer.models import TrainerTask as TTask

    tmpl = get_object_or_404(AdaptationTemplate, pk=pk)
    stages = tmpl.stages.prefetch_related('tasks__article', 'tasks__trainer_task').order_by('order')

    articles = list(Article.objects.values('pk', 'title').order_by('title'))
    trainer_tasks = list(TTask.objects.filter(is_active=True).values('pk', 'title').order_by('title'))

    initial_state = {
        'template': {
            'pk': tmpl.pk,
            'name': tmpl.name,
            'target_role': tmpl.target_role,
            'department': tmpl.department,
            'project': tmpl.project,
        },
        'stages': [
            {
                'pk': stage.pk,
                'title': stage.title,
                'tasks': [
                    {
                        'pk': task.pk,
                        'title': task.title,
                        'description': task.description,
                        'article_pk': task.article_id,
                        'article_title': task.article.title if task.article else '',
                        'trainer_task_pk': task.trainer_task_id,
                        'trainer_task_title': task.trainer_task.title if task.trainer_task else '',
                    }
                    for task in stage.tasks.all()
                ],
            }
            for stage in stages
        ],
    }

    return render(request, 'adaptation/routes/route_edit.html', {
        'tmpl': tmpl,
        'stages': stages,
        'role_choices': AdaptationTemplate.ROLE_CHOICES,
        'articles_json': json.dumps(articles, ensure_ascii=False),
        'trainer_tasks_json': json.dumps(trainer_tasks, ensure_ascii=False),
        'initial_state_json': json.dumps(initial_state, ensure_ascii=False),
    })


@_hr_required
def route_delete_view(request, pk):
    tmpl = get_object_or_404(AdaptationTemplate, pk=pk)
    if request.method == 'POST':
        # Protect if active routes use this template
        if AdaptationRoute.objects.filter(template=tmpl, is_active=True).exists():
            messages.error(request, 'Нельзя удалить шаблон с активными маршрутами.')
            return redirect('routes:edit', pk=tmpl.pk)
        tmpl.delete()
        messages.success(request, 'Шаблон удалён.')
        return redirect('routes:list')
    return render(request, 'adaptation/routes/confirm_delete.html', {
        'object_name': tmpl.name,
        'cancel_url': reverse('routes:edit', kwargs={'pk': pk}),
    })


# ─── Stage CRUD ──────────────────────────────────────────────────────────────

@_hr_required
def stage_create_view(request, template_pk):
    tmpl = get_object_or_404(AdaptationTemplate, pk=template_pk)
    if request.method == 'POST':
        form = StageForm(request.POST)
        if form.is_valid():
            stage = form.save(commit=False)
            stage.template = tmpl
            stage.save()
    return redirect('routes:edit', pk=template_pk)


@_hr_required
def stage_delete_view(request, pk):
    stage = get_object_or_404(Stage, pk=pk)
    template_pk = stage.template_id
    if request.method == 'POST':
        stage.delete()
    return redirect('routes:edit', pk=template_pk)


@_hr_required
def stage_move_view(request, pk, direction):
    stage = get_object_or_404(Stage, pk=pk)
    stages = list(stage.template.stages.order_by('order'))
    idx = next((i for i, s in enumerate(stages) if s.pk == stage.pk), None)
    if idx is None:
        return redirect('routes:edit', pk=stage.template_id)

    if direction == 'up' and idx > 0:
        stages[idx].order, stages[idx - 1].order = stages[idx - 1].order, stages[idx].order
        stages[idx].save(update_fields=['order'])
        stages[idx - 1].save(update_fields=['order'])
    elif direction == 'down' and idx < len(stages) - 1:
        stages[idx].order, stages[idx + 1].order = stages[idx + 1].order, stages[idx].order
        stages[idx].save(update_fields=['order'])
        stages[idx + 1].save(update_fields=['order'])

    return redirect('routes:edit', pk=stage.template_id)


# ─── Task CRUD ───────────────────────────────────────────────────────────────

@_hr_required
def task_create_view(request, stage_pk):
    stage = get_object_or_404(Stage, pk=stage_pk)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.stage = stage
            task.save()
    return redirect('routes:edit', pk=stage.template_id)


@_hr_required
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    template_pk = task.stage.template_id
    if request.method == 'POST':
        task.delete()
    return redirect('routes:edit', pk=template_pk)


@_hr_required
def stage_edit_view(request, pk):
    stage = get_object_or_404(Stage, pk=pk)
    if request.method == 'POST':
        form = StageForm(request.POST, instance=stage)
        if form.is_valid():
            form.save()
            messages.success(request, 'Этап обновлён.')
    return redirect('routes:edit', pk=stage.template_id)


@_hr_required
def task_edit_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    template_pk = task.stage.template_id
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задание обновлено.')
        return redirect('routes:edit', pk=template_pk)
    form = TaskForm(instance=task)
    return render(request, 'adaptation/routes/task_edit.html', {
        'form': form,
        'task': task,
        'tmpl': task.stage.template,
    })


# ─── Assign route ────────────────────────────────────────────────────────────

@_hr_required
def route_save_view(request, pk):
    """Единая точка сохранения всего редактора маршрута (JSON POST)."""
    tmpl = get_object_or_404(AdaptationTemplate, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)

    # Обновление метаданных шаблона
    tmpl_data = data.get('template', {})
    name = (tmpl_data.get('name') or '').strip()
    if name:
        tmpl.name = name
    tmpl.department = (tmpl_data.get('department') or '').strip()
    tmpl.project = (tmpl_data.get('project') or '').strip()
    valid_roles = [r[0] for r in AdaptationTemplate.ROLE_CHOICES]
    role = tmpl_data.get('target_role', '')
    if role in valid_roles:
        tmpl.target_role = role
    tmpl.save()

    existing_stage_pks = set(tmpl.stages.values_list('pk', flat=True))
    processed_stage_pks = set()

    for order_idx, stage_data in enumerate(data.get('stages', [])):
        title = (stage_data.get('title') or '').strip()
        if not title:
            continue

        stage_pk = stage_data.get('pk')
        if stage_pk and int(stage_pk) in existing_stage_pks:
            stage = Stage.objects.get(pk=stage_pk, template=tmpl)
            stage.title = title
            stage.order = order_idx
            stage.save()
        else:
            stage = Stage.objects.create(template=tmpl, title=title, order=order_idx)
        processed_stage_pks.add(stage.pk)

        existing_task_pks = set(stage.tasks.values_list('pk', flat=True))
        processed_task_pks = set()

        for task_order, task_data in enumerate(stage_data.get('tasks', [])):
            task_title = (task_data.get('title') or '').strip()
            if not task_title:
                continue

            task_pk = task_data.get('pk')
            article_pk = task_data.get('article_pk') or None
            trainer_task_pk = task_data.get('trainer_task_pk') or None
            description = task_data.get('description') or ''

            if task_pk and int(task_pk) in existing_task_pks:
                task = Task.objects.get(pk=task_pk, stage=stage)
                task.title = task_title
                task.description = description
                task.article_id = article_pk
                task.trainer_task_id = trainer_task_pk
                task.order = task_order
                task.save()
                processed_task_pks.add(int(task_pk))
            else:
                Task.objects.create(
                    stage=stage, title=task_title,
                    description=description,
                    article_id=article_pk,
                    trainer_task_id=trainer_task_pk,
                    order=task_order,
                )

        Task.objects.filter(stage=stage, pk__in=existing_task_pks - processed_task_pks).delete()

    Stage.objects.filter(pk__in=existing_stage_pks - processed_stage_pks, template=tmpl).delete()

    # Синхронизируем UserTaskProgress для всех активных маршрутов по этому шаблону:
    # добавляем записи для новых заданий, удалённые задания уже убраны через CASCADE.
    all_tasks = list(Task.objects.filter(stage__template=tmpl))
    active_routes = AdaptationRoute.objects.filter(template=tmpl, is_active=True)
    for route in active_routes:
        existing_ids = set(route.task_progress.values_list('task_id', flat=True))
        new_records = [
            UserTaskProgress(route=route, task=task, completed=False)
            for task in all_tasks
            if task.pk not in existing_ids
        ]
        if new_records:
            UserTaskProgress.objects.bulk_create(new_records)

    return JsonResponse({'ok': True})


@_hr_required
def route_assign_view(request):
    if request.method == 'POST':
        form = RouteAssignForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            tmpl = form.cleaned_data['template']
            mentor = form.cleaned_data.get('mentor')
            started_at = form.cleaned_data['started_at']

            route = AdaptationRoute.objects.create(
                user=user,
                template=tmpl,
                mentor=mentor,
                assigned_by=request.user,
                started_at=started_at,
                is_active=True,
            )

            # Create UserTaskProgress for every task in the template
            tasks = Task.objects.filter(stage__template=tmpl)
            UserTaskProgress.objects.bulk_create([
                UserTaskProgress(route=route, task=task, completed=False)
                for task in tasks
            ])

            messages.success(request, f'Маршрут «{tmpl.name}» назначен пользователю {user}.')
            return redirect('routes:list')
    else:
        form = RouteAssignForm()

    return render(request, 'adaptation/routes/route_assign.html', {'form': form})
