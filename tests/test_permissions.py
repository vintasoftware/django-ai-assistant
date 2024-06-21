from django.contrib.auth.models import User

import pytest
from model_bakery import baker

from django_ai_assistant.models import Thread
from django_ai_assistant.permissions import owns_thread


@pytest.fixture()
def superuser(db):
    return User.objects.create_superuser(username="superuser", password="password")


@pytest.fixture()
def regular_user(db):
    return User.objects.create_user(username="regular", password="password")


@pytest.mark.django_db()
def test_owns_thread(superuser, regular_user):
    thread = baker.make(Thread, name="AAA")
    assert owns_thread(superuser, thread)
    assert not owns_thread(regular_user, thread)

    thread = baker.make(Thread, name="CCC", created_by=superuser)
    assert owns_thread(superuser, thread)
    assert not owns_thread(regular_user, thread)

    thread = baker.make(Thread, name="BBB", created_by=regular_user)
    assert owns_thread(superuser, thread)
    assert owns_thread(regular_user, thread)
