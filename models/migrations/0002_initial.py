# Generated by Django 5.1.7 on 2025-04-02 06:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('models', '0001_initial'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='premiumsubscription',
            name='transaction',
            field=models.ForeignKey(blank=True, max_length=100, null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.transaction', unique=True),
        ),
        migrations.AddField(
            model_name='premiumsubscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='premium_subscriptions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.ForeignKey(blank=True, default=3, null=True, on_delete=django.db.models.deletion.SET_NULL, to='models.role'),
        ),
        migrations.AddField(
            model_name='song',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='playlistsong',
            name='song',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='models.song'),
        ),
        migrations.AddField(
            model_name='playbackhistory',
            name='song',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='models.song'),
        ),
        migrations.AddField(
            model_name='songplayhistory',
            name='song',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='play_history', to='models.song'),
        ),
        migrations.AddField(
            model_name='songplayhistory',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='premiumsubscription',
            unique_together={('user', 'transaction')},
        ),
        migrations.AlterUniqueTogether(
            name='playlistsong',
            unique_together={('playlist', 'song')},
        ),
    ]
