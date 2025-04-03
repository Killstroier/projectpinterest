from django import forms
from .models import Photo, TagPost, Category

class PhotoForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=TagPost.objects.all(), required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    class Meta:
        model = Photo
        fields = ['title', 'description', 'image', 'category', 'tags']
