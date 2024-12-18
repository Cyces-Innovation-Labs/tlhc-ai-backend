# Generated by Django 5.0.1 on 2024-12-03 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tamabot", "0003_remove_message_message_id_remove_thread_thread_id_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="message",
            name="good_or_bad",
        ),
        migrations.AddField(
            model_name="message",
            name="dislike",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="message",
            name="like",
            field=models.BooleanField(default=False),
        ),
    ]