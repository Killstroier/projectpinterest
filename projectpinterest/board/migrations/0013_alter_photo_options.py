# Generated by Django 5.1.6 on 2025-06-11 10:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0012_alter_photo_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photo',
            options={'ordering': ['-created_at'], 'permissions': [('can_publish_photo', 'Может публиковать фото')], 'verbose_name': 'Доска для постов', 'verbose_name_plural': 'Доска для постов'},
        ),
    ]
