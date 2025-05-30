from django.urls import path, register_converter
from . import views
from .converters import FourDigitYearConverter


# Регистрируем конвертер с именем 'yyyy'
register_converter(FourDigitYearConverter, 'yyyy')

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('post/<slug:post_slug>/', views.PostDetailView.as_view(), name='post'),
    path('create_manual/', views.PhotoCreateManualView.as_view(), name='create_manual'),
    path('create/', views.PhotoCreateView.as_view(), name='photo_create'),
    path('upload_file/', views.UploadFileView.as_view(), name='upload_file'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('edit/<slug:post_slug>/', views.PhotoUpdateView.as_view(), name='photo_edit'),
    path('delete/<slug:post_slug>/', views.PhotoDeleteView.as_view(), name='photo_delete'),
]
