# board/admin.py
from django.contrib import admin, messages
from .models import Photo, Category, TagPost
from django.utils.html import format_html


class TagsFilter(admin.SimpleListFilter):
    title = 'Наличие тэгов'
    parameter_name = 'has_tags'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'С тэгами'),
            ('no',  'Без тэгов'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'yes':
            return queryset.exclude(tags__isnull=True).distinct()
        if val == 'no':
            return queryset.filter(tags__isnull=True)
        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display       = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')
    search_fields      = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering           = ('name',)
    list_per_page      = 20


@admin.register(TagPost)
class TagPostAdmin(admin.ModelAdmin):
    list_display       = ('id', 'tag', 'slug')
    list_display_links = ('id', 'tag')
    search_fields      = ('tag',)
    prepopulated_fields = {'slug': ('tag',)}
    ordering           = ('tag',)
    list_per_page      = 20


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    # Базовый список полей
    list_display       = (
        'id', 'title', 'category', 'is_published',
        'image_preview', 'description',
        'created_at', 'views', 'total_likes', 'total_dislikes'
    )
    list_display_links = ('id', 'title')
    list_editable      = ('is_published', 'category')
    ordering           = ('-created_at', 'title')
    list_per_page      = 10

    # 8. пользовательские действия
    actions = ('make_published', 'make_draft')

    @admin.action(description="Опубликовать выбранные фотографии")
    def make_published(self, request, queryset):
        updated = queryset.update(is_published=Photo.Status.PUBLISHED)
        self.message_user(
            request,
            f"Успешно опубликовано {updated} фотографий",
            messages.SUCCESS
        )

    @admin.action(description="Снять с публикации выбранные фотографии")
    def make_draft(self, request, queryset):
        updated = queryset.update(is_published=Photo.Status.DRAFT)
        self.message_user(
            request,
            f"Снято с публикации {updated} фотографий",
            messages.WARNING
        )

    # 9. поиск и фильтрация
    search_fields = (
        'title', 'description',
        'category__name', 'tags__tag'
    )
    list_filter   = (
        'category', 'is_published', 'created_at',
        TagsFilter,
    )

    # 10. настройка форм добавления/редактирования
    

    # включаем related_select, чтобы stats не делал N+1 запросов
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category').prefetch_related('tags')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:80px;"/>',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Превью'
    image_preview.admin_order_field = 'image'


