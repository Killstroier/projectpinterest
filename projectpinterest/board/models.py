from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
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

class PhotoStats(models.Model):
    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"
    
    photo = models.OneToOneField(
        'Photo',
        on_delete=models.CASCADE,  # При удалении фото, удаляется и статистика
        related_name='stats'
    )
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')  # Количество просмотров
    likes = models.PositiveIntegerField(default=0, verbose_name='Лайки')  # Количество лайков

    def __str__(self):
        return f"Статистика для: {self.photo.title}"


# Модель для постов с ForeignKey к категории и ManyToMany к тегам
class Photo(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'
    
    class Meta:
        verbose_name = "Доска для постов"
        verbose_name_plural = "Доска для постов"
        ordering = ['-created_at']

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, null=True, db_index=True, verbose_name='URL-идентификатор')
    description = models.TextField(blank=True, verbose_name='Описание поста')
    image = models.ImageField(upload_to=upload_to_photos, verbose_name='Изображение')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, verbose_name='Категория', related_name='photos')
    tags = models.ManyToManyField(TagPost, blank=True, verbose_name='Тэги', related_name='photos')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(choices=Status.choices, default=Status.DRAFT, verbose_name='Статус')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})
    
    def increment_views(self):
        """Увеличивает счетчик просмотров поста"""
        self.stats.views += 1
        self.stats.save(update_fields=['views'])
    
    def toggle_like(self):
        """Переключает состояние лайка (для будущей реализации)"""
        self.stats.likes += 1
        self.stats.save(update_fields=['likes'])


# Сигнал для автоматического создания статистики при создании фото
@receiver(post_save, sender=Photo)
def create_photo_stats(sender, instance, created, **kwargs):
    if created:
        PhotoStats.objects.create(photo=instance)