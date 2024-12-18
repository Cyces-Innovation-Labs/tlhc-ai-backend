# Generated by Django 5.0.1 on 2024-12-18 14:16

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tamabot', '0004_remove_message_good_or_bad_message_dislike_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='tag',
            field=models.CharField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('first_name', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('last_name', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('user_id', models.IntegerField(unique=True)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('feedback', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('feedback_given_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tamabot.adminuser')),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_thread_feedbacks', to='tamabot.thread')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
