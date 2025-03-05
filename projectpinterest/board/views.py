from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def archive(request, year):
    # Здесь можно, например, фильтровать фотографии по году создания
    return render(request, 'archive.html', {'Год': year})
