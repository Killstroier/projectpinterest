from typing import Optional, Any

menu = [
    {'title': "О сайте", 'url_name': 'about'},
    {'title': "Добавить пост", 'url_name': 'photo_create'},
]

class DataMixin:
    title_page: Optional[str] = None

    def get_mixin_context(self, context: dict, **kwargs: Any) -> dict:
        """
        Добавляет в контекст menu, title и дополнительные данные из kwargs.
        """
        if 'menu' not in context:
            context['menu'] = menu

        if self.title_page and 'title' not in context:
            context['title'] = self.title_page

        if 'cat_selected' not in context:
            context['cat_selected'] = None

        context.update(kwargs)
        return context