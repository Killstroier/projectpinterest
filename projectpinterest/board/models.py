from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
import os

def upload_to_photos(instance, filename):
    """
    Генерирует путь для загрузки фотографий.
    Создает уникальный путь на основе слага и UUID.
    """
    name, ext = os.path.splitext(filename)
    return f"photos/{instance.slug}/{uuid.uuid4().hex}{ext}"

# Модель для категорий
class Category(models.Model):
    class Meta:
        verbose_name = "Категории"
        verbose_name_plural = "Категории"
        ordering = ['name']
    
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название категории')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL-идентификатор')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

# Модель для тегов
class TagPost(models.Model):
    class Meta:
        verbose_name = "Теги"
        verbose_name_plural = "Теги"
        ordering = ['tag']
    
    tag = models.CharField(max_length=100, db_index=True, verbose_name='Название тэга')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL-идентификатор')

    def __str__(self):
        return self.tag

class Comment(models.Model):
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']

    photo = models.ForeignKey('Photo', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(verbose_name='Содержание комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return f'Комментарий от {self.author.username} к {self.photo.title}'

    def can_edit(self, user):
        return user == self.author or user.groups.filter(name='Moderators').exists()

# Модель для постов с ForeignKey к категории и ManyToMany к тегам
class Photo(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'
    
    class Meta:
        verbose_name = "Доска для постов"
        verbose_name_plural = "Доска для постов"
        ordering = ['-created_at']
        permissions = [
            ("can_publish_photo", "Может публиковать фото"),
        ]

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, null=True, db_index=True, verbose_name='URL-идентификатор')
    description = models.TextField(blank=True, verbose_name='Описание поста')
    image = models.ImageField(upload_to=upload_to_photos, verbose_name='Изображение')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, verbose_name='Категория', related_name='photos')
    tags = models.ManyToManyField(TagPost, blank=True, verbose_name='Тэги', related_name='photos')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos', verbose_name='Автор', default=1)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(choices=Status.choices, default=Status.DRAFT, verbose_name='Статус')
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    likes = models.ManyToManyField(User, related_name='liked_photos', blank=True, verbose_name='Лайки')
    dislikes = models.ManyToManyField(User, related_name='disliked_photos', blank=True, verbose_name='Дизлайки')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})
    
    def increment_views(self):
        """Увеличивает счетчик просмотров поста"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    def can_edit(self, user):
        return user == self.author or user.groups.filter(name='Moderators').exists()