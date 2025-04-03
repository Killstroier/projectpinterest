from django.shortcuts import render, get_object_or_404, redirect
from .models import Photo, Category, TagPost
from .forms import PhotoForm

# Главная страница с фильтром по статусу
def index(request):
    filter_status = request.GET.get('filter')
    if filter_status == 'draft':
        posts = Photo.objects.filter(is_published=Photo.Status.DRAFT)
    elif filter_status == 'published':
        posts = Photo.objects.filter(is_published=Photo.Status.PUBLISHED)
    elif filter_status == 'all':
        posts = Photo.objects.all()
    else:
        posts = Photo.objects.filter(is_published=Photo.Status.PUBLISHED)

    data = {
        'title': 'Главная страница',
        'posts': posts,
    }
    return render(request, 'board/index.html', data)

# Страница для показа одного поста
def show_post(request, post_slug):
    post = get_object_or_404(Photo, slug=post_slug)
    return render(request, 'board/post.html', {'post': post})

# Редактирование поста
def photo_edit(request, post_slug):
    photo = get_object_or_404(Photo, slug=post_slug)
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            edited_photo = form.save()
            return redirect(edited_photo.get_absolute_url())
    else:
        form = PhotoForm(instance=photo)
    return render(request, 'board/photo_edit.html', {'form': form, 'photo': photo})

# Удаление поста
def photo_delete(request, post_slug):
    photo = get_object_or_404(Photo, slug=post_slug)
    if request.method == 'POST':
        photo.delete()
        return redirect('home')  # После удаления возвращаемся на главную
    return render(request, 'board/photo_delete_confirm.html', {'photo': photo})

# Создание нового поста
def photo_create(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            new_photo = form.save()
            return redirect(new_photo.get_absolute_url())
    else:
        form = PhotoForm()
    return render(request, 'board/photo_create.html', {'form': form})
