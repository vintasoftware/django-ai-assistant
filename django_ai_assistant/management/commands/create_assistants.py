import traceback

from django.core.management.base import BaseCommand, CommandError

from django_ai_assistant.ai.assistant import add, create_assistant, multiply


class Command(BaseCommand):
    help = "Create OpenAI Assistants"  # noqa: A003

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            assistant = create_assistant(
                name="Calculator",
                instructions="You are a calculator bot. Use the provided functions to answer questions.",
                fns=[add, multiply],
            )
        except Exception:
            traceback.print_exc()
            raise CommandError("Failed to create OpenAI Assistant. Check traceback above.")  # noqa: B904

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created OpenAI Assistant: {assistant.id}")
        )
