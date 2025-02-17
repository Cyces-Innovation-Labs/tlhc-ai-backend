# Generated by Django 5.0.1 on 2024-12-03 17:41

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tamabot", "0002_message"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="message",
            name="message_id",
        ),
        migrations.RemoveField(
            model_name="thread",
            name="thread_id",
        ),
        migrations.AlterField(
            model_name="message",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="thread",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
