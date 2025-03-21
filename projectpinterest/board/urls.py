from django.urls import path, register_converter
from . import views
from .converters import FourDigitYearConverter


# Регистрируем конвертер с именем 'yyyy'
register_converter(FourDigitYearConverter, 'yyyy')

urlpatterns = [
    path('', views.index, name='home'),
    path('archive/<yyyy:year>/', views.archive, name='archive'),
    path('post/<slug:post_slug>/', views.show_post, name='post'),
    path('create/', views.photo_create, name='photo_create'),
    path('about/', views.about, name='about'),
]
