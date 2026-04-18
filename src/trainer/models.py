from django.conf import settings
from django.db import models


class TrainerTask(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    scenario_description = models.TextField(verbose_name='Описание сценария')
    points_reward = models.IntegerField(default=20, verbose_name='Баллы за выполнение')
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    class Meta:
        verbose_name = 'Задание тренажёра'
        verbose_name_plural = 'Задания тренажёра'
        ordering = ['title']

    def __str__(self):
        return self.title


class TrainerSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'На проверке'
        ACCEPTED = 'accepted', 'Принято'
        REVISION = 'revision', 'Требует доработки'

    task = models.ForeignKey(TrainerTask, on_delete=models.CASCADE, related_name='submissions', verbose_name='Задание')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions', verbose_name='Сотрудник')
    headline = models.CharField(max_length=300, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    build_version = models.CharField(max_length=100, verbose_name='Версия билда')
    expected_result = models.TextField(verbose_name='Ожидаемый результат')
    actual_result = models.TextField(verbose_name='Фактический результат')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='Статус')

    class Meta:
        verbose_name = 'Ответ на задание'
        verbose_name_plural = 'Ответы на задания'
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.user} — {self.task.title} [{self.get_status_display()}]'


class Review(models.Model):
    class Result(models.TextChoices):
        ACCEPTED = 'accepted', 'Принято'
        REVISION = 'revision', 'Требует доработки'

    submission = models.OneToOneField(TrainerSubmission, on_delete=models.CASCADE, related_name='review', verbose_name='Ответ')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name='Наставник')
    result = models.CharField(max_length=20, choices=Result.choices, verbose_name='Результат')
    comment = models.TextField(verbose_name='Комментарий')
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Проверка'
        verbose_name_plural = 'Проверки'

    def __str__(self):
        return f'Проверка {self.submission} — {self.get_result_display()}'
