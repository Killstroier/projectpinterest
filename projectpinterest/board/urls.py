from django.urls import path, register_converter
from . import views
from .converters import FourDigitYearConverter


# Регистрируем конвертер с именем 'yyyy'
register_converter(FourDigitYearConverter, 'yyyy')

urlpatterns = [
    path('archive/<yyyy:year>/', views.archive, name='archive'),
    path('photo/<int:photo_id>/', views.photo_detail, name='photo_detail'),
    path('create/', views.photo_create, name='photo_create'),
    path('redirect/', views.redirect_example, name='redirect_example'),
    path('about/', views.about, name='about')
]
