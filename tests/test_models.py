from django.conf import settings
from django.db import models

import pytest

from django_ai_assistant.exceptions import (
    AIAssistantPrimaryKeyTypeNotInListError,
)
from django_ai_assistant.models import get_id_field


@pytest.fixture()
def use_fake_auto_setting(settings):
    settings.AI_ASSISTANT_PRIMARY_KEY_FIELD = "auto"


@pytest.fixture()
def use_fake_uuid_setting(settings):
    settings.AI_ASSISTANT_PRIMARY_KEY_FIELD = "uuid"


@pytest.fixture()
def use_fake_string_setting(settings):
    settings.AI_ASSISTANT_PRIMARY_KEY_FIELD = "string"


def test_get_id_field_returns_type_int_if_primary_key_field_is_auto(use_fake_auto_setting):
    assert get_id_field() == int


def test_get_id_field_returns_class_UUIDField_if_primary_key_field_is_uuid(use_fake_uuid_setting):
    assert isinstance(get_id_field(), models.UUIDField)


def test_get_id_field_returns_class_CharField_if_primary_key_field_is_string(
    use_fake_string_setting,
):
    assert isinstance(get_id_field(), models.CharField)


def test_assert_raises_AIAssistantPrimaryKeyTypeNotInList_if_primary_key_field_is_invalid():
    settings.AI_ASSISTANT_PRIMARY_KEY_FIELD = "invalid"
    with pytest.raises(AIAssistantPrimaryKeyTypeNotInListError):
        get_id_field()
