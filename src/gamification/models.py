from django.conf import settings
from django.db import models


class Achievement(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    icon_name = models.CharField(max_length=50, default='award', verbose_name='Иконка Bootstrap Icons')
    condition_key = models.CharField(max_length=50, unique=True, verbose_name='Ключ условия')

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='Пользователь',
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name='Достижение',
    )
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name='Получено')

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f'{self.user} — {self.achievement.name}'
