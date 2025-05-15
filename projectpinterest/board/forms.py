from django import forms
from .models import Photo, Category, TagPost
import re
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class PhotoForm(forms.ModelForm):
    """
    ModelForm для работы с постами.
    Включает обработку фотографий, категорий и тегов.
    """
    title = forms.CharField(
        label="Заголовок",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите заголовок поста'
        }),
        help_text="Заголовок должен содержать от 5 до 50 символов"
    )
    
    description = forms.CharField(
        label="Описание",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Введите описание поста'
        }),
        required=False,
        help_text="Подробное описание поста (необязательно)"
    )
    
    slug = forms.SlugField(
        label="URL-идентификатор",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'url-identificator'
        }),
        help_text="Используйте только латинские буквы, цифры, дефисы и подчеркивания"
    )
    
    image = forms.ImageField(
        label="Изображение",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Рекомендуемый размер: не менее 800x600 пикселей"
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=TagPost.objects.all(),
        label="Теги",
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
        help_text="Выберите один или несколько тегов (удерживайте Ctrl для выбора нескольких)"
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Категория",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Выберите категорию для поста"
    )
    
    class Meta:
        model = Photo
        fields = ['title', 'image', 'description', 'is_published', 'slug', 'category', 'tags']
        widgets = {
            'is_published': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'is_published': 'Статус публикации',
        }
        help_texts = {
            'is_published': 'Выберите "Опубликовано" для показа поста на сайте',
        }

    def clean_title(self):
        """Валидация заголовка"""
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError("Заголовок должен содержать минимум 5 символов")
        if len(title) > 50:
            raise forms.ValidationError("Длина заголовка не должна превышать 50 символов")
        return title
    
    def clean_slug(self):
        """Валидация слага"""
        slug = self.cleaned_data['slug']
        # Если слаг не задан, генерируем его из заголовка
        if not slug and 'title' in self.cleaned_data:
            slug = slugify(self.cleaned_data['title'])
        
        # Проверяем уникальность слага 
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            # Когда редактируем существующий пост, исключаем его из проверки
            qs = Photo.objects.filter(slug=slug).exclude(pk=instance.pk)
        else:
            # Для нового поста просто проверяем наличие слага в БД
            qs = Photo.objects.filter(slug=slug)
            
        if qs.exists():
            raise forms.ValidationError(f'URL-идентификатор "{slug}" уже используется. Пожалуйста, выберите другой.')
            
        return slug


class PhotoAddForm(forms.Form):
    """
    Форма для создания новых постов (не использует ModelForm).
    """
    title = forms.CharField(
        label="Заголовок",
        max_length=200,
        min_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите заголовок поста'
        }),
        help_text="Заголовок должен содержать от 5 до 200 символов"
    )
    
    slug = forms.SlugField(
        label="URL-идентификатор",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'url-identificator'
        }),
        help_text="Используйте только латинские буквы, цифры, дефисы и подчеркивания"
    )
    
    image = forms.ImageField(
        label="Изображение",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Рекомендуемый размер: не менее 800x600 пикселей"
    )
    
    description = forms.CharField(
        label="Описание",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Введите описание поста'
        }),
        required=False,
        help_text="Подробное описание поста (необязательно)"
    )
    
    is_published = forms.BooleanField(
        label="Опубликовано",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Отметьте, чтобы опубликовать пост"
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Категория",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Выберите категорию для поста"
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=TagPost.objects.all(),
        label="Теги",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text="Выберите один или несколько тегов (удерживайте Ctrl для выбора нескольких)"
    )

    def clean_title(self):
        """Валидация заголовка"""
        title = self.cleaned_data['title']
        if not re.match(r'^[\w\s-]+$', title, flags=re.U):
            raise ValidationError("Заголовок: только буквы, цифры, пробел, подчёркивание и дефис")
        return title
    
    def clean_slug(self):
        """Валидация слага"""
        slug = self.cleaned_data['slug']
        # Если слаг не задан, генерируем его из заголовка
        if not slug and 'title' in self.cleaned_data:
            slug = slugify(self.cleaned_data['title'])
            
        # Проверяем уникальность слага
        if Photo.objects.filter(slug=slug).exists():
            raise ValidationError(f'URL-идентификатор "{slug}" уже используется. Пожалуйста, выберите другой.')
            
        return slug
    
    
class UploadFileForm(forms.Form):
    """
    Форма для загрузки файлов.
    """
    file = forms.FileField(
        label="Файл",
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Выберите файл для загрузки"
    )
