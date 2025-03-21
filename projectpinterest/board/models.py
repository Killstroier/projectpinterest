from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Пользовательский менеджер для выбора только опубликованных записей
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Photo.Status.PUBLISHED)

class Photo(models.Model):
    # Перечисление для статуса публикации
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    # Поле slug для формирования красивых URL; для первоначальной миграции разрешаем пустоту,
    # чтобы затем заполнить слаг и обновить модель (после заполнения можно убрать blank и default)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL", blank=True, default='')
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='photos/', verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления")
    # Используем choices для поля публикации с перечислением
    is_published = models.BooleanField(choices=Status.choices, default=Status.DRAFT, verbose_name="Публикация")

    # Явно задаём стандартный менеджер и наш пользовательский
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})
