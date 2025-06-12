from django import template

register = template.Library()

# Простой тег: возвращает список категорий
@register.simple_tag
def get_categories():
    return [
        {'id': 1, 'name': 'Природа'},
        {'id': 2, 'name': 'Город'},
        {'id': 3, 'name': 'Искусство'},
    ]

# Включающий тег: рендерит шаблон со списком категорий
@register.inclusion_tag('board/includes/category_list.html')
def show_categories(cat_selected=0):
    categories = [
        {'id': 1, 'name': 'Природа'},
        {'id': 2, 'name': 'Город'},
        {'id': 3, 'name': 'Искусство'},
    ]
    return {'categories': categories, 'cat_selected': cat_selected}

@register.filter
def can_edit_check(obj, user):
    """
    Проверяет, может ли пользователь редактировать данный объект (пост или комментарий).
    """
    return obj.can_edit(user)
