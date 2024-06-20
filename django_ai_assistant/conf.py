from typing import Any

from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string


PREFIX = "AI_ASSISTANT_"


DEFAULTS = {
    "INIT_API_FN": "django_ai_assistant.api.views.init_api",
    "CAN_CREATE_THREAD_FN": "django_ai_assistant.permissions.allow_all",
    "CAN_VIEW_THREAD_FN": "django_ai_assistant.permissions.owns_thread",
    "CAN_UPDATE_THREAD_FN": "django_ai_assistant.permissions.owns_thread",
    "CAN_DELETE_THREAD_FN": "django_ai_assistant.permissions.owns_thread",
    "CAN_CREATE_MESSAGE_FN": "django_ai_assistant.permissions.owns_thread",
    "CAN_UPDATE_MESSAGE_FN": "django_ai_assistant.permissions.owns_thread",
    "CAN_DELETE_MESSAGE_FN": "django_ai_assistant.permissions.owns_thread",
    "CAN_RUN_ASSISTANT": "django_ai_assistant.permissions.allow_all",
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

        return getattr(settings, django_setting, DEFAULTS[setting])

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


app_settings = Settings()
setting_changed.connect(app_settings.change_setting)
