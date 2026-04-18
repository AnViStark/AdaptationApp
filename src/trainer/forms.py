from django import forms

from .models import Review, TrainerSubmission


class BugReportForm(forms.ModelForm):
    class Meta:
        model = TrainerSubmission
        fields = ['headline', 'description', 'build_version', 'expected_result', 'actual_result']
        labels = {
            'headline': 'Заголовок баг-репорта',
            'description': 'Описание',
            'build_version': 'Версия билда',
            'expected_result': 'Ожидаемый результат',
            'actual_result': 'Фактический результат',
        }
        widgets = {
            'headline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Краткое описание бага',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Подробное описание проблемы',
            }),
            'build_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'например: 1.0.0.123',
            }),
            'expected_result': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Что должно было произойти',
            }),
            'actual_result': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Что произошло на самом деле',
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['result', 'comment']
        labels = {
            'result': 'Результат проверки',
            'comment': 'Комментарий',
        }
        widgets = {
            'result': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Подробный комментарий для сотрудника…',
            }),
        }
