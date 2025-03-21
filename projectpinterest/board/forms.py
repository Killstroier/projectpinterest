from django import forms
from .models import Photo

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['Заголовок', 'слаг', 'Описание', 'Изображение', 'Опубликован']
