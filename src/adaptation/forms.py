from django import forms

from .models import AdaptationTemplate, AdaptationRoute, Stage, Task


class TemplateForm(forms.ModelForm):
    class Meta:
        model = AdaptationTemplate
        fields = ['name', 'target_role', 'department', 'project']
        labels = {
            'name': 'Название шаблона',
            'target_role': 'Целевая роль',
            'department': 'Отдел',
            'project': 'Проект',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Онбординг разработчика'}),
            'target_role': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Необязательно'}),
            'project': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Необязательно'}),
        }


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['title', 'order']
        labels = {'title': 'Название этапа', 'order': 'Порядок'}
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Знакомство с командой'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'article', 'trainer_task', 'order']
        labels = {
            'title': 'Название задания',
            'description': 'Описание',
            'article': 'Статья базы знаний',
            'trainer_task': 'Задание тренажёра',
            'order': 'Порядок',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Прочитать устав компании'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'article': forms.Select(attrs={'class': 'form-select'}),
            'trainer_task': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['article'].required = False
        self.fields['trainer_task'].required = False
        self.fields['article'].empty_label = '— без статьи —'
        self.fields['trainer_task'].empty_label = '— без задания тренажёра —'


class RouteAssignForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=None,
        label='Сотрудник',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    template = forms.ModelChoiceField(
        queryset=AdaptationTemplate.objects.all(),
        label='Шаблон маршрута',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    mentor = forms.ModelChoiceField(
        queryset=None,
        label='Наставник',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
    )
    started_at = forms.DateField(
        label='Дата начала',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    def __init__(self, *args, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        super().__init__(*args, **kwargs)
        # Only employees without an active route
        assigned_user_ids = AdaptationRoute.objects.filter(
            is_active=True,
        ).values_list('user_id', flat=True)
        self.fields['user'].queryset = User.objects.filter(
            role='employee', is_active=True,
        ).exclude(pk__in=assigned_user_ids)
        self.fields['user'].empty_label = '— выберите сотрудника —'
        self.fields['mentor'].queryset = User.objects.filter(role='mentor', is_active=True)
        self.fields['mentor'].empty_label = '— без наставника —'
