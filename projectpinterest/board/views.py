from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from django.http import HttpResponse, HttpResponseNotFound, Http404
from .models import Photo
from .forms import PhotoForm

menu = [
    {'title': "О сайте", 'url_name': 'about'},
    {'title': "Добавить фото", 'url_name': 'photo_create'},  # Для дальнейших расширений
]

# Пример публикаций (для демонстрации работы цикла for и фильтров)
posts = [
    {'id': 1, 'title': 'Природа', 'content': 'Описание природы и красоты окружающего мира. Здесь можно рассказать о пейзажах, лесах, реках и горах.', 'is_published': True},
    {'id': 2, 'title': 'Город', 'content': 'Описание городской жизни, архитектуры, динамики мегаполиса и его жителей.', 'is_published': True},
    {'id': 3, 'title': 'Искусство', 'content': 'Описание произведений искусства, выставок, галерей и творческих встреч.', 'is_published': False},
]

def index(request):
    data = {
        'title': 'Главная страница',
        'menu': menu,  # Передаём данные меню
        'posts': posts, # Передаём все посты
    }
    return render(request, 'board/index.html', data)

def about(request):
    data = {
        'title': 'О сайте',
        'menu': menu,
    }
    return render(request, 'board/about.html', data)


def home(request):
    return render(request, 'home.html')


def archive(request, year):
    # Здесь можно, например, отфильтровать фотографии по году создания
    return render(request, 'archive.html', {'year': year})


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


def photo_detail(request, photo_id):
    # Если фотография с указанным ID не найдена, будет вызван 404
    photo = get_object_or_404(Photo, pk=photo_id)
    return render(request, 'photo_detail.html', {'photo': photo})


def photo_create(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            new_photo = form.save(commit=False)
            # Если требуется, можно назначить автора (например, request.user)
            new_photo.save()
            return redirect('photo_detail', photo_id=new_photo.id)
    else:
        form = PhotoForm()
    return render(request, 'photo_create.html', {'form': form})


def redirect_example(request):
    # Пример перенаправления: перенаправляем на детальную страницу фото с id=1
    return redirect('photo_detail', photo_id=1)


def event_detail(request, event_date):
    date_if = '2023-01-01'
    if event_date > datetime.strptime(date_if, '%Y-%m-%d'):
        return redirect('/')
    return HttpResponse(f"<h1>Архив за {event_date}</h1>")


