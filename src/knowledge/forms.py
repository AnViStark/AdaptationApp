from django import forms

from .models import Article, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Название категории'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Правила компании'}),
        }


class ArticleForm(forms.ModelForm):
    new_category = forms.CharField(
        required=False,
        label='Новая категория (если нет нужной)',
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Введите название новой категории'}),
    )

    class Meta:
        model = Article
        fields = ['title', 'category', 'content']
        labels = {
            'title': 'Заголовок',
            'category': 'Категория',
            'content': 'Содержимое (Markdown)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название статьи'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'rows': 20, 'class': 'form-control font-monospace'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Category is not required at field level — clean() handles the combined validation
        self.fields['category'].required = False

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category', '').strip()

        if not category and not new_category:
            raise forms.ValidationError('Выберите существующую или введите новую категорию.')

        # Resolve new_category → real Category object HERE, before _post_clean()
        # runs model-level validation (category is non-nullable FK, can't be None).
        if not category and new_category:
            cat, _ = Category.objects.get_or_create(name=new_category)
            cleaned_data['category'] = cat

        return cleaned_data
