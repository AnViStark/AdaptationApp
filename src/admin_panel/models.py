from django.db import models


class SystemSettings(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name='Ключ')
    value = models.TextField(verbose_name='Значение')

    class Meta:
        verbose_name = 'Настройка системы'
        verbose_name_plural = 'Настройки системы'

    def __str__(self):
        return f'{self.key} = {self.value}'

    @classmethod
    def get(cls, key, default=''):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set(cls, key, value):
        obj, _ = cls.objects.update_or_create(key=key, defaults={'value': value})
        return obj
