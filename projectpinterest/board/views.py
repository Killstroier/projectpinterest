from django.shortcuts import render, get_object_or_404, redirect
from .models import Photo
from .forms import PhotoForm

def index(request):
    # Используем менеджер published для выбора только опубликованных постов
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

def about(request):
    data = {
        'title': 'О сайте',
    }
    return render(request, 'board/about.html', data)
