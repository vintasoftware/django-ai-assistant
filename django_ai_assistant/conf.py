from django.conf import settings as dj_settings
from django.core.signals import setting_changed


PREFIX = "AI_ASSISTANT_"


DEFAULTS = {
    "CLIENT_INIT_FN": None,
    "USER_CAN_CREATE_THREAD_FN": None,
    "USER_CAN_CREATE_MESSAGE_FN": None,
}


class Settings:
    def __getattr__(self, name):
        if name not in DEFAULTS:
            msg = "'%s' object has no attribute '%s'"
            raise AttributeError(msg % (self.__class__.__name__, name))

        value = self.get_setting(name)

        # Cache the result
        setattr(self, name, value)
        return value

    def get_setting(self, setting):
        django_setting = f"{PREFIX}{setting}"

        return getattr(dj_settings, django_setting, DEFAULTS[setting])

    def change_setting(self, setting, value, enter, **kwargs):
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


settings = Settings()
setting_changed.connect(settings.change_setting)
