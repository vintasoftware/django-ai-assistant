# Generated by Django 5.1.1 on 2024-10-03 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_ai_assistant', '0005_alter_message_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='assistant_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]