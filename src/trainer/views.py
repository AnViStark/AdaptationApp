from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BugReportForm, ReviewForm
from .models import Review, TrainerSubmission, TrainerTask


@login_required
def task_list_view(request):
    if request.user.role != 'employee':
        raise PermissionDenied

    tasks = TrainerTask.objects.filter(is_active=True)

    # Map task → user's latest submission
    submissions = TrainerSubmission.objects.filter(
        user=request.user,
        task__in=tasks,
    ).select_related('task').order_by('-submitted_at')

    submission_map = {}
    for sub in submissions:
        if sub.task_id not in submission_map:
            submission_map[sub.task_id] = sub

    task_data = []
    for task in tasks:
        sub = submission_map.get(task.pk)
        task_data.append({
            'task': task,
            'submission': sub,
            'status': sub.status if sub else None,
        })

    return render(request, 'trainer/task_list.html', {'task_data': task_data})


@login_required
def task_detail_view(request, pk):
    if request.user.role != 'employee':
        raise PermissionDenied

    task = get_object_or_404(TrainerTask, pk=pk, is_active=True)

    # Get existing submission (latest)
    submission = TrainerSubmission.objects.filter(
        user=request.user, task=task,
    ).select_related('review').order_by('-submitted_at').first()

    # Can submit if: no submission, or last one was sent back for revision
    can_submit = submission is None or submission.status == TrainerSubmission.Status.REVISION

    form = None
    if can_submit:
        if request.method == 'POST':
            form = BugReportForm(request.POST, instance=submission if submission and submission.status == TrainerSubmission.Status.REVISION else None)
            if form.is_valid():
                sub = form.save(commit=False)
                sub.task = task
                sub.user = request.user
                sub.status = TrainerSubmission.Status.PENDING
                sub.save()
                messages.success(request, 'Баг-репорт отправлен на проверку!')
                return redirect('trainer:detail', pk=pk)
        else:
            initial = {}
            if submission and submission.status == TrainerSubmission.Status.REVISION:
                # Pre-fill with previous values for re-submission
                form = BugReportForm(instance=submission)
            else:
                form = BugReportForm()

    review = getattr(submission, 'review', None) if submission else None

    return render(request, 'trainer/task_detail.html', {
        'task': task,
        'submission': submission,
        'can_submit': can_submit,
        'form': form,
        'review': review,
    })


@login_required
def review_view(request, submission_id):
    if request.user.role != 'mentor':
        raise PermissionDenied

    submission = get_object_or_404(
        TrainerSubmission.objects.select_related('task', 'user'),
        pk=submission_id,
    )

    # Mentor can only review submissions from their mentees
    from adaptation.models import AdaptationRoute
    is_mentee = AdaptationRoute.objects.filter(
        user=submission.user, mentor=request.user, is_active=True,
    ).exists()
    if not is_mentee:
        raise PermissionDenied

    existing_review = getattr(submission, 'review', None)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.submission = submission
            review.mentor = request.user
            review.save()

            # Update submission status
            submission.status = review.result
            submission.save(update_fields=['status'])

            # Award points if accepted
            if review.result == Review.Result.ACCEPTED:
                employee = submission.user
                employee.points += submission.task.points_reward
                employee.level = max(1, employee.points // 100 + 1)
                employee.save(update_fields=['points', 'level'])

            messages.success(request, 'Оценка отправлена.')
            return redirect('users:mentee_detail', user_id=submission.user_id)
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, 'trainer/review.html', {
        'submission': submission,
        'form': form,
        'existing_review': existing_review,
    })
