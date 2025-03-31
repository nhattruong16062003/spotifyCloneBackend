# Generated by Django 5.1.7 on 2025-03-31 05:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0002_delete_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='PremiumPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duration_days', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='premium_end',
        ),
        migrations.RemoveField(
            model_name='user',
            name='premium_start',
        ),
        migrations.CreateModel(
            name='PremiumSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField()),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='models.premiumplan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='premium_subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
