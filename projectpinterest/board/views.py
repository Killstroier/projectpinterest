from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .forms import PhotoAddForm, PhotoForm, UploadFileForm
from .models import Photo, Category, TagPost
import uuid, os
from datetime import datetime


# Главная страница с фильтром по статусу
def index(request):
    """
    Главная страница с фильтрацией постов по статусу (опубликованные, черновики, все)
    """
    filter_status = request.GET.get('filter')
    
    # Базовый QuerySet с оптимизацией запросов
    base_queryset = Photo.objects.select_related('category', 'stats').prefetch_related('tags')
    
    # Применяем фильтрацию в зависимости от параметра
    if filter_status == 'draft':
        posts = base_queryset.filter(is_published=Photo.Status.DRAFT)
        title = 'Черновики'
    elif filter_status == 'published':
        posts = base_queryset.filter(is_published=Photo.Status.PUBLISHED)
        title = 'Опубликованные'
    elif filter_status == 'all':
        posts = base_queryset.all()
        title = 'Все посты'
    else:
        # По умолчанию показываем только опубликованные
        posts = base_queryset.filter(is_published=Photo.Status.PUBLISHED)
        title = 'Опубликованные'

    data = {
        'title': title,
        'posts': posts,
        'filter_status': filter_status or 'published',
    }
    return render(request, 'board/index.html', data)


def about(request):
    """Страница "О нас"."""
    data = {
        'title': 'О сайте',
    }
    return render(request, 'board/about.html', data)


# Страница для показа одного поста
def show_post(request, post_slug):
    """
    Детальный просмотр поста с увеличением счетчика просмотров.
    """
    # Оптимизируем запрос с select_related и prefetch_related
    post = get_object_or_404(
        Photo.objects.select_related('category', 'stats').prefetch_related('tags'),
        slug=post_slug
    )
    
    # Увеличиваем счетчик просмотров
    post.increment_views()
    
    return render(request, 'board/post.html', {'post': post})


# Редактирование поста
def photo_edit(request, post_slug):
    """
    Редактирование существующего поста.
    """
    photo = get_object_or_404(Photo, slug=post_slug)
    
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            edited_photo = form.save()
            messages.success(request, f'Пост "{edited_photo.title}" успешно обновлен.')
            return redirect(edited_photo.get_absolute_url())
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = PhotoForm(instance=photo)
    
    return render(request, 'board/photo_edit.html', {
        'form': form, 
        'photo': photo,
        'title': f'Редактирование: {photo.title}'
    })


# Удаление поста
def photo_delete(request, post_slug):
    """
    Удаление поста с подтверждением.
    """
    photo = get_object_or_404(Photo, slug=post_slug)
    
    if request.method == 'POST':
        title = photo.title
        photo.delete()
        messages.success(request, f'Пост "{title}" успешно удален.')
        return redirect('home')
    
    return render(request, 'board/photo_delete_confirm.html', {
        'photo': photo,
        'title': f'Удаление: {photo.title}'
    })


# Создание нового поста
def photo_create(request):
    """
    Создание нового поста с использованием ModelForm.
    """
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            new_photo = form.save()
            messages.success(request, f'Пост "{new_photo.title}" успешно создан.')
            return redirect(new_photo.get_absolute_url())
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = PhotoForm()
    
    return render(request, 'board/photo_create.html', {
        'form': form,
        'title': 'Создание нового поста'
    })


def photo_create_manual(request):
    """
    Альтернативный метод создания поста с использованием Form (не ModelForm).
    """
    if request.method == 'POST':
        form = PhotoAddForm(request.POST, request.FILES)
        if form.is_valid():
            # Создаем новый пост с данными из формы
            photo = Photo.objects.create(
                title = form.cleaned_data['title'],
                slug  = form.cleaned_data['slug'],
                image = form.cleaned_data.get('image'),
                description = form.cleaned_data['description'],
                is_published = form.cleaned_data['is_published'],
                category = form.cleaned_data['category'],
            )
            # Добавляем теги к посту
            photo.tags.set(form.cleaned_data['tags'])
            
            messages.success(request, f'Пост "{photo.title}" успешно создан.')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = PhotoAddForm()
    
    return render(request, 'board/photo_create.html', {
        'form': form,
        'title': 'Создание нового поста (ручной метод)'
    })


def photo_create_modelform(request):
    """
    Создание нового поста с использованием ModelForm (альтернативная версия).
    """
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save()
            messages.success(request, f'Пост "{photo.title}" успешно создан.')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = PhotoForm()
    
    return render(request, 'board/photo_create_modelform.html', {
        'form': form,
        'title': 'Создание нового поста (ModelForm)'
    })


def upload_file(request):
    """
    Загрузка файла без создания поста.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = handle_uploaded_file(form.cleaned_data['file'])
            messages.success(request, f'Файл "{filename}" успешно загружен.')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, выберите корректный файл.')
    else:
        form = UploadFileForm()
    
    context = {
        'title': 'Загрузка файла',
        'form': form,
    }
    return render(request, 'board/upload_file.html', context)


def handle_uploaded_file(f):
    """
    Обработка загруженного файла.
    Создает уникальное имя файла и сохраняет его в папке uploads.
    """
    name = f.name
    ext = ''
    if '.' in name:
        ext = name[name.rindex('.'):]
        name = name[:name.rindex('.')]
    
    # Создаем папку uploads, если ее нет
    upload_dir = 'media/uploads'
    os.makedirs(upload_dir, exist_ok=True)
    
    # Генерируем уникальное имя файла
    suffix = str(uuid.uuid4())
    filename = f"{name}_{suffix}{ext}"
    filepath = f"{upload_dir}/{filename}"
    
    # Сохраняем файл
    with open(filepath, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    return filename
