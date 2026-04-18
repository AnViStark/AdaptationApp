from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100, unique=True, verbose_name='Ключ')),
                ('value', models.TextField(verbose_name='Значение')),
            ],
            options={
                'verbose_name': 'Настройка системы',
                'verbose_name_plural': 'Настройки системы',
            },
        ),
    ]
