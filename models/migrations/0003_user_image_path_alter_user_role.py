# Generated by Django 5.1.7 on 2025-03-23 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0002_playlist_image_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image_path',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(default='User', max_length=10),
        ),
    ]
