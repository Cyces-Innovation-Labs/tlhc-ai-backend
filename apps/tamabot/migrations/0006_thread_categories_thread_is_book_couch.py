# Generated by Django 5.0.1 on 2024-12-18 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tamabot", "0005_thread_tag_adminuser_feedback"),
    ]

    operations = [
        migrations.AddField(
            model_name="thread",
            name="categories",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="thread",
            name="is_book_couch",
            field=models.BooleanField(default=False),
        ),
    ]
