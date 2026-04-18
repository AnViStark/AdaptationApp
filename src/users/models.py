from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = 'employee', 'Новый сотрудник'
        MENTOR = 'mentor', 'Наставник'
        HR = 'hr', 'Кадровая служба'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        verbose_name='Роль',
    )
    department = models.CharField(max_length=100, blank=True, verbose_name='Отдел')
    project = models.CharField(max_length=100, blank=True, verbose_name='Проект')
    start_date = models.DateField(null=True, blank=True, verbose_name='Дата начала')
    points = models.IntegerField(default=0, verbose_name='Баллы')
    level = models.IntegerField(default=1, verbose_name='Уровень')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE

    @property
    def is_mentor(self):
        return self.role == self.Role.MENTOR

    @property
    def is_hr(self):
        return self.role == self.Role.HR

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN
