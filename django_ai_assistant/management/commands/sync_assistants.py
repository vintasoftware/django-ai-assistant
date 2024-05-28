import traceback

from django.core.management.base import BaseCommand, CommandError

from django_ai_assistant.helpers.assistants import sync_assistants


class Command(BaseCommand):
    help = "Sync AIAssistant classes with OpenAI Assistants"  # noqa: A003

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            open_ai_ids = sync_assistants()
        except Exception:
            traceback.print_exc()
            raise CommandError("Failed to create OpenAI Assistant. Check traceback above.")  # noqa: B904

        self.stdout.write(
            self.style.SUCCESS(f"Successfully synced OpenAI Assistants: {open_ai_ids}")
        )
