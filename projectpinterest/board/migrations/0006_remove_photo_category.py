# Generated by Django 5.1.6 on 2025-04-11 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0005_category_husband_tagpost_women_alter_photo_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='category',
        ),
    ]
