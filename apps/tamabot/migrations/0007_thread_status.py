# Generated by Django 5.0.1 on 2024-12-23 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tamabot', '0006_thread_categories_thread_is_book_couch'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='status',
            field=models.CharField(blank=True, choices=[('approved', 'Approved'), ('rejected', 'Rejected')], default=None, max_length=512, null=True),
        ),
    ]
