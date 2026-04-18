from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='adaptation.UserTaskProgress')
def on_task_completed(sender, instance, **kwargs):
    if instance.completed:
        check_achievements(instance.route.user)


@receiver(post_save, sender='trainer.Review')
def on_review_saved(sender, instance, **kwargs):
    if instance.result == 'accepted':
        check_achievements(instance.submission.user)


def check_achievements(user):
    """Award any newly unlocked achievements to user."""
    from .models import Achievement, UserAchievement
    from adaptation.models import UserTaskProgress, AdaptationRoute

    already_earned = set(
        UserAchievement.objects.filter(user=user).values_list('achievement__condition_key', flat=True)
    )

    def _award(key):
        if key in already_earned:
            return
        try:
            achievement = Achievement.objects.get(condition_key=key)
            UserAchievement.objects.get_or_create(user=user, achievement=achievement)
        except Achievement.DoesNotExist:
            pass

    completed_tasks = UserTaskProgress.objects.filter(
        route__user=user, completed=True,
    ).count()

    # First task completed
    if completed_tasks >= 1:
        _award('first_task')

    # First stage fully completed
    from adaptation.models import Stage
    routes = AdaptationRoute.objects.filter(user=user, is_active=True)
    for route in routes:
        for stage in route.template.stages.all():
            task_ids = list(stage.tasks.values_list('id', flat=True))
            if not task_ids:
                continue
            done = UserTaskProgress.objects.filter(
                route=route, task_id__in=task_ids, completed=True,
            ).count()
            if done == len(task_ids):
                _award('first_stage')
                break

    # Entire route completed
    for route in routes:
        total = route.total_tasks()
        done = route.completed_tasks()
        if total > 0 and done == total:
            _award('route_complete')
            break

    # First accepted trainer submission
    from trainer.models import TrainerSubmission
    accepted = TrainerSubmission.objects.filter(user=user, status='accepted').exists()
    if accepted:
        _award('first_bugreport')

    # Points milestones
    if user.points >= 100:
        _award('points_100')
    if user.points >= 500:
        _award('points_500')
