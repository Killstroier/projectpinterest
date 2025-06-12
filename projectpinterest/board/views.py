from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.urls import reverse_lazy
from django.db.models import Q
from .forms import PhotoForm, UploadFileForm
from .models import Photo, Category, TagPost, Comment
import uuid, os
from .utils import DataMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.http import JsonResponse, HttpResponseForbidden


class IndexView(DataMixin, ListView):
    model = Photo
    template_name = 'board/index.html'
    context_object_name = 'posts'
    paginate_by = 6  # пагинация

    def get_queryset(self):
        filter_status = self.request.GET.get('filter')
        base_queryset = Photo.objects.select_related('category').prefetch_related('tags')

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
        return Photo.objects.select_related('category').prefetch_related('tags')

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
    permission_required = 'board.can_edit'
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

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


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


@permission_required('board.can_publish_photo', raise_exception=True)
def publish_photo(request, post_slug):
    photo = get_object_or_404(Photo, slug=post_slug)
    photo.is_published = Photo.Status.PUBLISHED
    photo.save()
    return redirect('post', post_slug=photo.slug)


@login_required
def add_comment(request, photo_id):
    if request.method == 'POST':
        photo = get_object_or_404(Photo, id=photo_id)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                photo=photo,
                author=request.user,
                content=content
            )
            messages.success(request, 'Комментарий успешно добавлен!')
        return redirect('post', post_slug=photo.slug)
    return redirect('home')

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if not comment.can_edit(request.user):
        return HttpResponseForbidden("У вас нет прав для редактирования этого комментария")
    
    if request.method == 'POST':
        comment.content = request.POST.get('content')
        comment.save()
        messages.success(request, 'Комментарий успешно обновлен!')
        return redirect('post', post_slug=comment.photo.slug)
    
    return render(request, 'board/edit_comment.html', {'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if not comment.can_edit(request.user):
        return HttpResponseForbidden("У вас нет прав для удаления этого комментария")
    
    photo_slug = comment.photo.slug
    comment.delete()
    messages.success(request, 'Комментарий удален!')
    return redirect('post', post_slug=photo_slug)

@login_required
def like_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if request.user in photo.likes.all():
        photo.likes.remove(request.user)
        liked = False
    else:
        photo.likes.add(request.user)
        photo.dislikes.remove(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'total_likes': photo.total_likes(),
        'total_dislikes': photo.total_dislikes()
    })

@login_required
def dislike_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if request.user in photo.dislikes.all():
        photo.dislikes.remove(request.user)
        disliked = False
    else:
        photo.dislikes.add(request.user)
        photo.likes.remove(request.user)
        disliked = True
    return JsonResponse({
        'disliked': disliked,
        'total_likes': photo.total_likes(),
        'total_dislikes': photo.total_dislikes()
    })

@login_required
def edit_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if not photo.can_edit(request.user):
        return HttpResponseForbidden("У вас нет прав для редактирования этого поста")
    
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('post', post_slug=photo.slug)
        else:
            # If the form is not valid, re-render the page with errors
            return render(request, 'board/photo_edit.html', {'photo': photo, 'form': form})
    
    # For GET request, create an unbound form with instance data
    form = PhotoForm(instance=photo)
    return render(request, 'board/photo_edit.html', {'photo': photo, 'form': form})

@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if not photo.can_edit(request.user):
        return HttpResponseForbidden("У вас нет прав для удаления этого поста")
    
    photo.delete()
    messages.success(request, 'Пост успешно удален!')
    return redirect('home')
