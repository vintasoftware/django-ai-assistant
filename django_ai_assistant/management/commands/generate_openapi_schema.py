import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from django_ai_assistant.api.views import api


class Command(BaseCommand):
    help = "Generate OpenAPI schema for Django AI Assistant API, and save it to a file"  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="openapi_schema.json",
            help="Path to the output file where the OpenAPI schema will be saved",
        )

    def handle(self, *args, **options):
        try:
            openapi_schema = api.get_openapi_schema()
            openapi_json = json.dumps(openapi_schema, indent=2)
            output_file = Path(options["output"])
            output_file.write_text(openapi_json)
        except Exception as e:
            raise CommandError(f"Failed to generate OpenAPI schema. Original error: {e}") from e

        self.stdout.write(self.style.SUCCESS(f"OpenAPI schema saved to {output_file}"))
