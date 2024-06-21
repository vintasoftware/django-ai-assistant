import uuid

from django_ai_assistant.decorators import _cast_id, with_cast_id
from django_ai_assistant.models import Thread


def test_cast_id_does_not_transform_regular_ids():
    assert isinstance(_cast_id(1, Thread), int)


def test_cast_id_does_not_transform_str_ids(monkeypatch):
    def mock_get_internal_type():
        return "CharField"

    monkeypatch.setattr(Thread._meta.pk, "get_internal_type", mock_get_internal_type)

    assert isinstance(_cast_id("dfjsdjfkndskjf", Thread), str)


def test_cast_id_transforms_uuids(monkeypatch):
    def mock_get_internal_type():
        return "UUIDField"

    monkeypatch.setattr(Thread._meta.pk, "get_internal_type", mock_get_internal_type)

    assert isinstance(_cast_id("c8e6d7f7-7b2e-4d3b-8b9d-5b1d4b1f3e6b", Thread), uuid.UUID)


def test_with_cast_id_transforms_regular_ids():
    @with_cast_id
    def dummy_function(thread_id):
        return thread_id

    assert isinstance(dummy_function(thread_id=1), int)


def test_with_cast_id_transforms_str_ids(monkeypatch):
    def mock_get_internal_type():
        return "CharField"

    monkeypatch.setattr(Thread._meta.pk, "get_internal_type", mock_get_internal_type)

    @with_cast_id
    def dummy_function(thread_id):
        return thread_id

    assert isinstance(dummy_function(thread_id="dfjsdjfkndskjf"), str)


def test_with_cast_id_transforms_uuids(monkeypatch):
    def mock_get_internal_type():
        return "UUIDField"

    monkeypatch.setattr(Thread._meta.pk, "get_internal_type", mock_get_internal_type)

    @with_cast_id
    def dummy_function(thread_id):
        return thread_id

    assert isinstance(dummy_function(thread_id="c8e6d7f7-7b2e-4d3b-8b9d-5b1d4b1f3e6b"), uuid.UUID)
