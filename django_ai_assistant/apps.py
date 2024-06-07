import importlib.util
from importlib import import_module

from django.apps import AppConfig, apps


class AIAssistantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_ai_assistant"

    def ready(self):
        # import all ai_assistants.py files in all other apps to register the assistants:
        # TODO: recursive search for ai_assistants.py files in all apps in nested directories

        for app in apps.get_app_configs():
            try:
                import_module(f"{app.name}.ai_assistants")
            except ModuleNotFoundError:
                # If the module exists but there is an error in it, we want to raise the error:
                if importlib.util.find_spec(f"{app.name}.ai_assistants"):
                    raise
