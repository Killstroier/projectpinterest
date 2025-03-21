from django.shortcuts import render, get_object_or_404, redirect
from .models import Photo
from .forms import PhotoForm


def index(request):
    filter_status = request.GET.get('filter')
    if filter_status == 'draft':
        posts = Photo.objects.filter(is_published=Photo.Status.DRAFT)
    elif filter_status == 'published':
        posts = Photo.published.all()
    elif filter_status == 'all':
        posts = Photo.objects.all()
    else:
        # По умолчанию показываем только опубликованные
        posts = Photo.published.all()

    data = {
        'title': 'Главная страница',
        'posts': posts,
    }
    return render(request, 'board/index.html', data)


def show_post(request, post_slug):
    # Получаем пост по слагу; если не найден – генерируется 404
    post = get_object_or_404(Photo, slug=post_slug)
    data = {
        'title': post.title,
        'post': post,
    }
    return render(request, 'board/post.html', data)


def photo_create(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            # Если слаг не задан, можно автогенерировать (например, на основе title)
            if not new_post.slug:
                from django.utils.text import slugify
                new_post.slug = slugify(new_post.title)
            new_post.save()
            return redirect(new_post.get_absolute_url())
        else:
            # Вывод ошибок в консоль для отладки
            print(form.errors)
    else:
        form = PhotoForm()
    return render(request, 'board/photo_create.html', {'form': form})


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


def photo_delete(request, post_slug):
    photo = get_object_or_404(Photo, slug=post_slug)
    if request.method == 'POST':
        photo.delete()
        return redirect('home')  # После удаления возвращаемся на главную
    return render(request, 'board/photo_delete_confirm.html', {'photo': photo})


def about(request):
    data = {
        'title': 'О сайте',
    }
    return render(request, 'board/about.html', data)
