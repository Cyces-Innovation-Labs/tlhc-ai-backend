# Generated by Django 5.0.1 on 2025-01-02 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tamabot", "0007_thread_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="thread",
            name="last_conversation",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
