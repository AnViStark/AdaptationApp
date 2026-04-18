from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from trainer.models import TrainerTask

User = get_user_model()


class UserCreateForm(forms.Form):
    first_name = forms.CharField(
        label='Имя', max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        label='Фамилия', max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    username = forms.CharField(
        label='Логин (username)', max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    role = forms.ChoiceField(
        label='Роль',
        choices=User.Role.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    department = forms.CharField(
        label='Отдел', max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password


class TrainerTaskForm(forms.ModelForm):
    class Meta:
        model = TrainerTask
        fields = ['title', 'scenario_description', 'points_reward', 'is_active']
        labels = {
            'title': 'Название задания',
            'scenario_description': 'Описание сценария',
            'points_reward': 'Баллы за принятие',
            'is_active': 'Активно',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'scenario_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'points_reward': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
