# Generated by Django 5.0.1 on 2025-05-13 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tamabot', '0009_message_therapist'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='chatbot_type',
            field=models.CharField(choices=[('support', 'Support'), ('emotional', 'Emotional')], default='emotional', max_length=512),
        ),
    ]
