# Generated by Django 5.1.7 on 2025-04-01 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
    ]
