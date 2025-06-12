from django.urls import path, register_converter
from . import views
from .converters import FourDigitYearConverter


# Регистрируем конвертер с именем 'yyyy'
register_converter(FourDigitYearConverter, 'yyyy')

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('post/<slug:post_slug>/', views.PostDetailView.as_view(), name='post'),
    path('create/', views.PhotoCreateView.as_view(), name='photo_create'),
    path('upload_file/', views.UploadFileView.as_view(), name='upload_file'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('edit/<slug:post_slug>/', views.PhotoUpdateView.as_view(), name='photo_edit'),
    path('delete/<slug:post_slug>/', views.PhotoDeleteView.as_view(), name='photo_delete'),
    path('post/<slug:post_slug>/publish/', views.publish_photo, name='publish_photo'),
    path('photo/<int:photo_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('photo/<int:photo_id>/like/', views.like_photo, name='like_photo'),
    path('photo/<int:photo_id>/dislike/', views.dislike_photo, name='dislike_photo'),
    path('photo/<int:photo_id>/edit/', views.edit_photo, name='edit_photo'),
    path('photo/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
]
