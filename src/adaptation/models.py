from django.conf import settings
from django.db import models
from django.utils import timezone


class AdaptationTemplate(models.Model):
    """Шаблон маршрута адаптации — многоразовая заготовка для назначения новичкам."""

    ROLE_CHOICES = [
        ('employee', 'Новый сотрудник'),
        ('mentor', 'Наставник'),
        ('hr', 'Кадровая служба'),
        ('admin', 'Администратор'),
        ('', 'Любая роль'),
    ]

    name = models.CharField(max_length=200, verbose_name='Название')
    target_role = models.CharField(max_length=20, blank=True, choices=ROLE_CHOICES, verbose_name='Целевая роль')
    department = models.CharField(max_length=100, blank=True, verbose_name='Отдел')
    project = models.CharField(max_length=100, blank=True, verbose_name='Проект')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_templates',
        verbose_name='Создал',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Шаблон маршрута'
        verbose_name_plural = 'Шаблоны маршрутов'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def stage_count(self):
        return self.stages.count()

    def task_count(self):
        return Task.objects.filter(stage__template=self).count()


class Stage(models.Model):
    """Этап внутри шаблона маршрута."""

    template = models.ForeignKey(
        AdaptationTemplate,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name='Шаблон',
    )
    title = models.CharField(max_length=200, verbose_name='Название этапа')
    order = models.IntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Этап'
        verbose_name_plural = 'Этапы'
        ordering = ['order']

    def __str__(self):
        return f'{self.template.name} — {self.title}'


class Task(models.Model):
    """Задание внутри этапа."""

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='tasks', verbose_name='Этап')
    title = models.CharField(max_length=200, verbose_name='Название задания')
    description = models.TextField(blank=True, verbose_name='Описание')
    article = models.ForeignKey(
        'knowledge.Article',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='Статья базы знаний',
    )
    trainer_task = models.ForeignKey(
        'trainer.TrainerTask',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adaptation_tasks',
        verbose_name='Задание тренажёра',
    )
    order = models.IntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['order']

    def __str__(self):
        return self.title


class AdaptationRoute(models.Model):
    """Конкретный маршрут, назначенный конкретному сотруднику."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='route',
        verbose_name='Сотрудник',
    )
    template = models.ForeignKey(
        AdaptationTemplate,
        on_delete=models.PROTECT,
        verbose_name='Шаблон',
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentees',
        verbose_name='Наставник',
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_routes',
        verbose_name='Назначил',
    )
    started_at = models.DateField(default=timezone.now, verbose_name='Дата начала')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Маршрут адаптации'
        verbose_name_plural = 'Маршруты адаптации'
        ordering = ['-started_at']

    def __str__(self):
        return f'Маршрут {self.user} — {self.template.name}'

    def total_tasks(self):
        return self.task_progress.count()

    def completed_tasks(self):
        return self.task_progress.filter(completed=True).count()

    def progress_percent(self):
        total = self.total_tasks()
        if total == 0:
            return 0
        return round(self.completed_tasks() / total * 100)


class UserTaskProgress(models.Model):
    """Прогресс выполнения конкретного задания конкретным сотрудником."""

    route = models.ForeignKey(
        AdaptationRoute,
        on_delete=models.CASCADE,
        related_name='task_progress',
        verbose_name='Маршрут',
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name='Задание',
    )
    completed = models.BooleanField(default=False, verbose_name='Выполнено')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата выполнения')

    class Meta:
        verbose_name = 'Прогресс задания'
        verbose_name_plural = 'Прогресс заданий'
        unique_together = ('route', 'task')

    def __str__(self):
        status = 'выполнено' if self.completed else 'не выполнено'
        return f'{self.route.user} — {self.task.title} [{status}]'
