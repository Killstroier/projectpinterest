# Generated by Django 5.1.6 on 2025-06-11 07:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0011_alter_category_options_alter_photo_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photo',
            options={'ordering': ['-created_at'], 'permissions': [('can_edit', 'Возможность редактировать фото'), ('can_delete', 'Возможность удалять фото')], 'verbose_name': 'Доска для постов', 'verbose_name_plural': 'Доска для постов'},
        ),
    ]
