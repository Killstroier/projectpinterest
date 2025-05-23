from django.urls import path, register_converter
from . import views
from .converters import FourDigitYearConverter


# Регистрируем конвертер с именем 'yyyy'
register_converter(FourDigitYearConverter, 'yyyy')

urlpatterns = [
    path('', views.index, name='home'),
    path('post/<slug:post_slug>/', views.show_post, name='post'),
    path('create_manual/', views.photo_create_manual, name='create_manual'),
    path('create_modelform/', views.photo_create_modelform, name='create_modelform'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('create/', views.photo_create, name='photo_create'),
    path('about/', views.about, name='about'),
    path('edit/<slug:post_slug>/', views.photo_edit, name='photo_edit'),
    path('delete/<slug:post_slug>/', views.photo_delete, name='photo_delete'),
]
