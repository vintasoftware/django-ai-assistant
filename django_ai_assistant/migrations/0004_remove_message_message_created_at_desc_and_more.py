# Generated by Django 5.0.6 on 2024-06-03 13:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_ai_assistant", "0003_message_delete_assistant_remove_thread_openai_id_and_more"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="message",
            name="message_created_at_desc",
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(models.F("created_at"), name="message_created_at"),
        ),
    ]
