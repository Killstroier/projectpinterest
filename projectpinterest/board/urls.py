from django.urls import path, register_converter
from .converters import FourDigitYearConverter
from . import views

register_converter(FourDigitYearConverter, 'yyyy')

urlpatterns = [
    path('archive/<yyyy:year>/', views.archive, name='archive'),
    path('', views.home, name='home'),
]
