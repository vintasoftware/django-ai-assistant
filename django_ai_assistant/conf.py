from typing import Any

from django.conf import settings as dj_settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string


PREFIX = "AI_ASSISTANT_"


DEFAULTS = {
    "CLIENT_INIT_FN": "django_ai_assistant.ai.client.init_openai",
    "CAN_CREATE_THREAD_FN": "django_ai_assistant.permissions.allow_all",
    "CAN_VIEW_THREAD_FN": "django_ai_assistant.permissions.allow_all",
    "CAN_CREATE_MESSAGE_FN": "django_ai_assistant.permissions.allow_all",
    "CAN_RUN_ASSISTANT": "django_ai_assistant.permissions.allow_all",
    "API_IMPORT_PATH": "django_ai_assistant.views.api",
}


class Settings:
    def __getattr__(self, name: str):
        if name not in DEFAULTS:
            msg = "'%s' object has no attribute '%s'"
            raise AttributeError(msg % (self.__class__.__name__, name))

        value = self.get_setting(name)

        # Cache the result
        setattr(self, name, value)
        return value

    def get_setting(self, setting: str):
        django_setting = f"{PREFIX}{setting}"

        return getattr(dj_settings, django_setting, DEFAULTS[setting])

    def change_setting(self, setting: str, value: Any, enter: bool, **kwargs):
        if not setting.startswith(PREFIX):
            return
        setting = setting[len(PREFIX) :]  # strip 'AI_ASSISTANT_'

        # ensure a valid app setting is being overridden
        if setting not in DEFAULTS:
            return

        # if exiting, delete value to repopulate
        if enter:
            setattr(self, setting, value)
        else:
            delattr(self, setting)

    def call_fn(self, name: str, **kwargs):
        dotted_path = self.get_setting(name)
        fn = import_string(dotted_path)
        return fn(**kwargs)


settings = Settings()
setting_changed.connect(settings.change_setting)
