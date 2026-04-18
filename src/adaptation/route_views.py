from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
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
    tmpl = get_object_or_404(AdaptationTemplate, pk=pk)

    if request.method == 'POST' and 'save_template' in request.POST:
        form = TemplateForm(request.POST, instance=tmpl)
        if form.is_valid():
            form.save()
            messages.success(request, 'Шаблон обновлён.')
            return redirect('routes:edit', pk=tmpl.pk)
    else:
        form = TemplateForm(instance=tmpl)

    stages = tmpl.stages.prefetch_related('tasks').all()
    stage_form = StageForm(initial={'order': tmpl.stages.count()})
    task_form = TaskForm()

    return render(request, 'adaptation/routes/route_edit.html', {
        'tmpl': tmpl,
        'form': form,
        'stages': stages,
        'stage_form': stage_form,
        'task_form': task_form,
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


# ─── Assign route ────────────────────────────────────────────────────────────

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
