import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('icon_name', models.CharField(default='award', max_length=50, verbose_name='Иконка Bootstrap Icons')),
                ('condition_key', models.CharField(max_length=50, unique=True, verbose_name='Ключ условия')),
            ],
            options={'verbose_name': 'Достижение', 'verbose_name_plural': 'Достижения'},
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('earned_at', models.DateTimeField(auto_now_add=True, verbose_name='Получено')),
                ('achievement', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='user_achievements',
                    to='gamification.achievement',
                    verbose_name='Достижение',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='achievements',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Пользователь',
                )),
            ],
            options={'verbose_name': 'Достижение пользователя', 'verbose_name_plural': 'Достижения пользователей'},
        ),
        migrations.AlterUniqueTogether(
            name='userachievement',
            unique_together={('user', 'achievement')},
        ),
    ]
