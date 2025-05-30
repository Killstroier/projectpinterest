from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.urls import reverse_lazy
from django.db.models import Q
from .forms import PhotoAddForm, PhotoForm, UploadFileForm
from .models import Photo, Category, TagPost
import uuid, os
from datetime import datetime
from .utils import DataMixin


class IndexView(DataMixin, ListView):
    model = Photo
    template_name = 'board/index.html'
    context_object_name = 'posts'
    paginate_by = 6  # пагинация

    def get_queryset(self):
        filter_status = self.request.GET.get('filter')
        base_queryset = Photo.objects.select_related('category', 'stats').prefetch_related('tags')

        if filter_status == 'draft':
            return base_queryset.filter(is_published=Photo.Status.DRAFT)
        elif filter_status == 'published':
            return base_queryset.filter(is_published=Photo.Status.PUBLISHED)
        elif filter_status == 'all':
            return base_queryset.all()
        else:
            return base_queryset.filter(is_published=Photo.Status.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_status = self.request.GET.get('filter')

        if filter_status == 'draft':
            title = 'Черновики'
        elif filter_status == 'published':
            title = 'Опубликованные'
        elif filter_status == 'all':
            title = 'Все посты'
        else:
            title = 'Опубликованные'

        # Добавляем логику пагинации в контекст
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        current_page = page_obj.number if page_obj else 1
        page_range = paginator.page_range if paginator else []

        if len(page_range) > 7:
            if current_page <= 4:
                page_range = list(range(1, 8))
            elif current_page >= len(page_range) - 3:
                page_range = list(range(len(page_range) - 6, len(page_range) + 1))
            else:
                page_range = list(range(current_page - 3, current_page + 4))

        return self.get_mixin_context(context, title=title, filter_status=filter_status or 'published',
                                      page_range=page_range, current_page=current_page)


class AboutView(TemplateView):
    """Страница "О нас"."""
    template_name = 'board/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О сайте'
        return context


class PostDetailView(DataMixin, DetailView):
    model = Photo
    template_name = 'board/post.html'
    context_object_name = 'post'
    slug_url_kwarg = 'post_slug'

    def get_queryset(self):
        return Photo.objects.select_related('category', 'stats').prefetch_related('tags')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.increment_views()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context.get('post').title)



class PhotoUpdateView(UpdateView):
    """
    Редактирование существующего поста.
    """
    model = Photo
    form_class = PhotoForm
    template_name = 'board/photo_edit.html'
    slug_url_kwarg = 'post_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.title}'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Пост "{self.object.title}" успешно обновлен.')
        return response


class PhotoDeleteView(DeleteView):
    """
    Удаление поста с подтверждением.
    """
    model = Photo
    template_name = 'board/photo_delete_confirm.html'
    slug_url_kwarg = 'post_slug'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление: {self.object.title}'
        return context

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Пост "{self.object.title}" успешно удален.')
        return response


class PhotoCreateView(DataMixin, CreateView):
    model = Photo
    form_class = PhotoForm
    template_name = 'board/photo_create.html'
    success_url = reverse_lazy('home')
    title_page = 'Создание нового поста'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)



class PhotoCreateManualView(CreateView):
    """
    Альтернативный метод создания поста с использованием Form (не ModelForm).
    """
    model = Photo
    form_class = PhotoAddForm
    template_name = 'board/photo_create.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание нового поста (ручной метод)'
        return context

    def form_valid(self, form):
        photo = Photo.objects.create(
            title=form.cleaned_data['title'],
            slug=form.cleaned_data['slug'],
            image=form.cleaned_data.get('image'),
            description=form.cleaned_data['description'],
            is_published=form.cleaned_data['is_published'],
            category=form.cleaned_data['category'],
        )
        photo.tags.set(form.cleaned_data['tags'])
        messages.success(self.request, f'Пост "{photo.title}" успешно создан.')
        return redirect(self.success_url)


class UploadFileView(FormView):
    """
    Загрузка файла без создания поста.
    """
    form_class = UploadFileForm
    template_name = 'board/upload_file.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка файла'
        return context

    def form_valid(self, form):
        filename = self.handle_uploaded_file(form.cleaned_data['file'])
        messages.success(self.request, f'Файл "{filename}" успешно загружен.')
        return super().form_valid(form)

    def handle_uploaded_file(self, f):
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
