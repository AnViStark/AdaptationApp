"""
Management command: seed_demo
Creates demo data for presentation purposes.
Usage: python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Заполняет базу данных демо-данными для презентации'

    def handle(self, *args, **options):
        self.stdout.write('Создание демо-данных...')
        self._create_users()
        self._create_achievements()
        self._create_knowledge()
        self._create_trainer_tasks()
        self._create_route_template()
        self._assign_routes()
        self.stdout.write(self.style.SUCCESS('\nГотово! Демо-данные созданы.'))
        self.stdout.write('\nДемо-пользователи (email / пароль):')
        self.stdout.write('  admin@targem.ru    / Targem2024!')
        self.stdout.write('  hr@targem.ru       / Targem2024!')
        self.stdout.write('  mentor@targem.ru   / Targem2024!')
        self.stdout.write('  anna@targem.ru     / Targem2024!')
        self.stdout.write('  sergey@targem.ru   / Targem2024!')

    def _create_users(self):
        from users.models import CustomUser

        users_data = [
            dict(username='admin_user', email='admin@targem.ru', first_name='Алексей', last_name='Громов',
                 role='admin', department='IT', is_staff=True, is_superuser=False),
            dict(username='hr_manager', email='hr@targem.ru', first_name='Елена', last_name='Соколова',
                 role='hr', department='Кадры'),
            dict(username='mentor_ivan', email='mentor@targem.ru', first_name='Иван', last_name='Петров',
                 role='mentor', department='QA'),
            dict(username='newbie_anna', email='anna@targem.ru', first_name='Анна', last_name='Смирнова',
                 role='employee', department='QA',
                 start_date=timezone.now().date()),
            dict(username='newbie_sergey', email='sergey@targem.ru', first_name='Сергей', last_name='Козлов',
                 role='employee', department='QA',
                 start_date=timezone.now().date()),
        ]

        for data in users_data:
            email = data['email']
            if CustomUser.objects.filter(email=email).exists():
                self.stdout.write(f'  Пользователь {email} уже существует, пропускаем')
                continue
            is_staff = data.pop('is_staff', False)
            is_superuser = data.pop('is_superuser', False)
            user = CustomUser(**data)
            user.set_password('Targem2024!')
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
            self.stdout.write(f'  Создан: {email}')

    def _create_achievements(self):
        from gamification.models import Achievement

        achievements_data = [
            ('first_task', 'Первый шаг', 'Выполнено первое задание маршрута', 'flag-fill'),
            ('first_stage', 'Этапник', 'Завершён первый этап адаптации', 'layers-fill'),
            ('route_complete', 'Адаптирован', 'Маршрут адаптации пройден полностью', 'trophy-fill'),
            ('first_bugreport', 'Охотник за багами', 'Первый баг-репорт принят наставником', 'bug-fill'),
            ('points_100', 'Сотня', 'Набрано 100 баллов', 'star-fill'),
            ('points_500', 'Профессионал', 'Набрано 500 баллов', 'gem'),
        ]

        for key, name, description, icon in achievements_data:
            obj, created = Achievement.objects.get_or_create(
                condition_key=key,
                defaults={'name': name, 'description': description, 'icon_name': icon},
            )
            if created:
                self.stdout.write(f'  Достижение: {name}')

    def _create_knowledge(self):
        from django.contrib.auth import get_user_model
        from knowledge.models import Article, Category

        User = get_user_model()
        author = User.objects.filter(role='hr').first() or User.objects.filter(is_superuser=True).first()

        categories_data = {
            'Добро пожаловать': [
                ('Правила и ценности Targem Games',
                 '# Правила и ценности\n\n'
                 'Targem Games — международная игровая студия, создающая онлайн-игры.\n\n'
                 '## Наши ценности\n\n'
                 '- **Качество** — мы делаем игры, в которые сами хотим играть\n'
                 '- **Честность** — открытость внутри команды\n'
                 '- **Развитие** — каждый сотрудник растёт вместе с компанией\n\n'
                 '## Рабочий распорядок\n\n'
                 'Рабочий день: с 10:00 до 19:00. Гибкий старт допускается по согласованию с руководителем.\n\n'
                 'Обед: 13:00–14:00 (нефиксированный).\n'),
                ('Структура компании и отделы',
                 '# Структура Targem Games\n\n'
                 '## Основные отделы\n\n'
                 '| Отдел | Чем занимается |\n'
                 '|-------|----------------|\n'
                 '| Разработка | Программирование игровой логики и серверной части |\n'
                 '| QA | Тестирование и контроль качества |\n'
                 '| Геймдизайн | Баланс, механики, контент |\n'
                 '| Арт | Графика, анимации, UI |\n'
                 '| Продюсирование | Планирование и координация |\n\n'
                 '## Как связаться с коллегами\n\n'
                 'Основной мессенджер — **Slack**. Каналы:\n'
                 '- `#general` — общие объявления\n'
                 '- `#qa` — команда тестирования\n'
                 '- `#dev` — разработчики\n'),
            ],
            'Рабочие процессы': [
                ('Как написать баг-репорт',
                 '# Стандарт баг-репорта Targem Games\n\n'
                 'Правильный баг-репорт экономит время всей команды.\n\n'
                 '## Обязательные поля\n\n'
                 '### Заголовок\n'
                 'Краткое описание по формуле: **[Где] [Что] [При каких условиях]**\n\n'
                 'Пример: `[Гараж] Кнопка "Установить" не реагирует на нажатие при отсутствии деталей`\n\n'
                 '### Описание\n'
                 'Подробный контекст: в каком режиме, с каким персонажем, какие действия предшествовали.\n\n'
                 '### Шаги воспроизведения\n'
                 '1. Открыть гараж\n'
                 '2. Выбрать детали\n'
                 '3. Нажать кнопку установки\n\n'
                 '### Ожидаемый результат\n'
                 'Что должно произойти согласно спецификации или логике.\n\n'
                 '### Фактический результат\n'
                 'Что произошло на самом деле.\n\n'
                 '### Версия билда\n'
                 'Найти в настройках → «О программе». Формат: `1.0.0.1234`\n\n'
                 '## Приоритеты\n\n'
                 '| Приоритет | Описание |\n'
                 '|-----------|----------|\n'
                 '| Blocker | Игра не запускается / критические данные теряются |\n'
                 '| Critical | Ключевая функция не работает |\n'
                 '| Major | Заметный сбой, есть обходное решение |\n'
                 '| Minor | Косметика, неточность в тексте |\n'),
                ('Жизненный цикл задачи в Jira',
                 '# Работа с задачами в Jira\n\n'
                 '## Статусы задачи\n\n'
                 '```\nOpen → In Progress → Review → Testing → Done\n```\n\n'
                 '## Правила работы\n\n'
                 '- Берёшь задачу → переводи в **In Progress**\n'
                 '- Сделал → переводи в **Review** и назначай ревьюера\n'
                 '- Исправил баг → прикрепляй скриншот до/после\n\n'
                 '## Оценка задач\n\n'
                 'Используем Story Points по шкале Фибоначчи: 1, 2, 3, 5, 8, 13.\n'),
            ],
            'Игра Crossout': [
                ('Что такое Crossout и наши проекты',
                 '# Crossout — флагманский проект\n\n'
                 'Crossout — постапокалиптическая онлайн-игра, в которой игроки строят бронированные машины '
                 'из деталей и сражаются друг с другом.\n\n'
                 '## Ключевые особенности\n\n'
                 '- Конструктор машин из сотен деталей\n'
                 '- PvP-бои в реальном времени\n'
                 '- Рынок и экономика внутри игры\n'
                 '- Регулярные сезонные обновления\n\n'
                 '## Платформы\n\nPC (Steam), PlayStation 4/5, Xbox One/Series.\n\n'
                 '## Персонаж Вэйд (W.A.D.E.)\n\n'
                 'W.A.D.E. — Rogue Mind, один из ключевых персонажей Crossout. '
                 'Робот с уникальным характером: харизматичный, с чёрным юмором. '
                 'Используется как маскот системы адаптации Targem.\n'),
            ],
        }

        for cat_name, articles in categories_data.items():
            category, _ = Category.objects.get_or_create(name=cat_name)
            for title, content in articles:
                if not Article.objects.filter(title=title).exists():
                    Article.objects.create(
                        category=category,
                        title=title,
                        content=content,
                        created_by=author,
                    )
                    self.stdout.write(f'  Статья: {title}')

    def _create_trainer_tasks(self):
        from trainer.models import TrainerTask

        tasks_data = [
            (
                'Сломанная кнопка в гараже',
                'В игре Crossout ты открываешь гараж и замечаешь, что кнопка «Установить деталь» '
                'перестала работать после последнего обновления. При нажатии ничего не происходит. '
                'Иногда появляется звук клика, но деталь не устанавливается. '
                'Воспроизводится стабильно на всех машинах с деталями типа «Кабина».',
                25,
            ),
            (
                'Искажение текстур на арене',
                'На карте «Пустошь» в режиме PvP наблюдается визуальный артефакт: '
                'текстура дорожного покрытия начинает мерцать при движении со скоростью выше 80 км/ч. '
                'Особенно заметно в зоне D-4 на мини-карте. '
                'Баг появляется только при ультра-настройках графики.',
                20,
            ),
            (
                'Потеря прогресса после выхода из боя',
                'Сотрудник сообщает: после завершения боя в режиме «Рейд» опыт и ресурсы '
                'не засчитываются, если выйти из игры в течение 10 секунд после экрана результатов. '
                'Проблема воспроизводится примерно в 3 из 5 случаев. '
                'Потеря составляет от 50 до 100% наград за бой.',
                30,
            ),
            (
                'Некорректный счётчик побед в профиле',
                'В разделе «Статистика» профиля игрока счётчик «Побед» показывает '
                'значение на 1 больше фактического после ничьих. '
                'Ничья засчитывается как победа. '
                'Баг стабильно воспроизводится: сыграй матч, который завершился ничьей, '
                'и проверь счётчик.',
                15,
            ),
        ]

        for title, scenario, points in tasks_data:
            if not TrainerTask.objects.filter(title=title).exists():  # type: ignore[attr-defined]
                from trainer.models import TrainerTask as TT
                TT.objects.create(title=title, scenario_description=scenario, points_reward=points, is_active=True)
                self.stdout.write(f'  Задание тренажёра: {title}')

    def _create_route_template(self):
        from adaptation.models import AdaptationTemplate, Stage, Task
        from knowledge.models import Article
        from trainer.models import TrainerTask

        if AdaptationTemplate.objects.filter(name='Онбординг QA-специалиста').exists():
            return

        from django.contrib.auth import get_user_model
        User = get_user_model()
        hr = User.objects.filter(role='hr').first()

        tmpl = AdaptationTemplate.objects.create(
            name='Онбординг QA-специалиста',
            target_role='employee',
            department='QA',
            created_by=hr,
        )

        # Stage 1
        s1 = Stage.objects.create(template=tmpl, title='Знакомство с компанией', order=0)
        art_values = Article.objects.filter(title__icontains='ценност').first()
        art_structure = Article.objects.filter(title__icontains='структур').first()
        Task.objects.create(stage=s1, title='Прочитать о ценностях компании', order=0, article=art_values)
        Task.objects.create(stage=s1, title='Изучить структуру отделов', order=1, article=art_structure)
        Task.objects.create(stage=s1, title='Познакомиться с командой QA', order=2)

        # Stage 2
        s2 = Stage.objects.create(template=tmpl, title='Рабочее место и инструменты', order=1)
        art_jira = Article.objects.filter(title__icontains='Jira').first()
        Task.objects.create(stage=s2, title='Настроить рабочее место', order=0)
        Task.objects.create(stage=s2, title='Получить доступы к Jira и Slack', order=1)
        Task.objects.create(stage=s2, title='Изучить процесс работы с задачами', order=2, article=art_jira)

        # Stage 3
        s3 = Stage.objects.create(template=tmpl, title='Первые задания', order=2)
        art_bug = Article.objects.filter(title__icontains='баг-репорт').first()
        tt = TrainerTask.objects.first()
        Task.objects.create(stage=s3, title='Изучить стандарт баг-репортов', order=0, article=art_bug)
        Task.objects.create(stage=s3, title='Пройти первое задание тренажёра', order=1, trainer_task=tt)
        Task.objects.create(stage=s3, title='Провести тест-сессию с наставником', order=2)

        self.stdout.write(f'  Шаблон маршрута: {tmpl.name}')
        return tmpl

    def _assign_routes(self):
        from django.contrib.auth import get_user_model
        from adaptation.models import AdaptationRoute, AdaptationTemplate, Task, UserTaskProgress
        from django.utils import timezone

        User = get_user_model()
        tmpl = AdaptationTemplate.objects.filter(name='Онбординг QA-специалиста').first()
        if not tmpl:
            return

        mentor = User.objects.filter(email='mentor@targem.ru').first()
        hr = User.objects.filter(email='hr@targem.ru').first()
        anna = User.objects.filter(email='anna@targem.ru').first()
        sergey = User.objects.filter(email='sergey@targem.ru').first()

        all_tasks = list(Task.objects.filter(stage__template=tmpl).order_by('stage__order', 'order'))

        for employee, complete_count in [(anna, 4), (sergey, 1)]:
            if not employee:
                continue
            if AdaptationRoute.objects.filter(user=employee, is_active=True).exists():
                self.stdout.write(f'  Маршрут для {employee.email} уже существует')
                continue

            route = AdaptationRoute.objects.create(
                user=employee,
                template=tmpl,
                mentor=mentor,
                assigned_by=hr,
                started_at=timezone.now().date(),
                is_active=True,
            )

            progress_objs = []
            for i, task in enumerate(all_tasks):
                completed = i < complete_count
                progress_objs.append(UserTaskProgress(
                    route=route,
                    task=task,
                    completed=completed,
                    completed_at=timezone.now() if completed else None,
                ))
            UserTaskProgress.objects.bulk_create(progress_objs)

            # Update points
            employee.points = complete_count * 10
            employee.level = max(1, employee.points // 100 + 1)
            employee.save(update_fields=['points', 'level'])

            self.stdout.write(f'  Маршрут назначен: {employee.email} ({complete_count} заданий выполнено)')
