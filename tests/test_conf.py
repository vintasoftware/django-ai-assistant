from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

import pytest

from django_ai_assistant.conf import DEFAULTS, PREFIX, Settings


@pytest.fixture
def settings():
    return Settings()


def test_getattr_existing_setting(settings):
    assert settings.INIT_API_FN == DEFAULTS["INIT_API_FN"]


def test_getattr_non_existing_setting(settings):
    with pytest.raises(AttributeError):
        settings.NON_EXISTING_SETTING  # noqa: B018


def test_get_setting_default(settings):
    assert settings.get_setting("INIT_API_FN") == DEFAULTS["INIT_API_FN"]


@override_settings(AI_ASSISTANT_INIT_API_FN="custom.module.init_api")
def test_get_setting_override(settings):
    assert settings.get_setting("INIT_API_FN") == "custom.module.init_api"


def test_change_setting_enter(settings):
    settings.change_setting(f"{PREFIX}INIT_API_FN", "new.value", enter=True)
    assert settings.INIT_API_FN == "new.value"


def test_change_setting_exit(settings):
    settings.change_setting(f"{PREFIX}INIT_API_FN", "new.value", enter=True)
    assert settings.INIT_API_FN == "new.value"
    settings.change_setting(f"{PREFIX}INIT_API_FN", None, enter=False)
    assert settings.INIT_API_FN == DEFAULTS["INIT_API_FN"]


def test_change_setting_invalid_prefix(settings):
    settings.change_setting("INVALID_PREFIX_SETTING", "value", enter=True)
    assert not hasattr(settings, "SETTING")


def test_change_setting_invalid_setting(settings):
    settings.change_setting(f"{PREFIX}INVALID_SETTING", "value", enter=True)
    assert not hasattr(settings, "INVALID_SETTING")


def test_call_fn(settings):
    result = settings.call_fn("INIT_API_FN")
    assert result


@override_settings(AI_ASSISTANT_INIT_API_FN="django.core.exceptions.ImproperlyConfigured")
def test_call_fn_override(settings):
    result = settings.call_fn("INIT_API_FN")

    assert isinstance(result, ImproperlyConfigured)
