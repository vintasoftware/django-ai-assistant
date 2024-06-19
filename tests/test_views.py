from http import HTTPStatus

from django.contrib.auth.models import User
from django.urls import reverse

import pytest
from model_bakery import baker

from django_ai_assistant.exceptions import AIAssistantNotDefinedError, AIUserNotAllowedError
from django_ai_assistant.helpers.assistants import AIAssistant, register_assistant
from django_ai_assistant.helpers.use_cases import create_thread_message_as_user
from django_ai_assistant.langchain.tools import BaseModel, Field, method_tool
from django_ai_assistant.models import Thread


# Set up


@register_assistant
class TemperatureAssistant(AIAssistant):
    id = "temperature_assistant"  # noqa: A003
    name = "Temperature Assistant"
    instructions = "You are a temperature bot."
    model = "gpt-4o"

    def get_instructions(self):
        return self.instructions + " Today is 2024-06-09."

    @method_tool
    def fetch_current_temperature(self, location: str) -> str:
        """Fetch the current temperature data for a location"""
        return "32 degrees Celsius"

    class FetchForecastTemperatureInput(BaseModel):
        location: str
        dt_str: str = Field(description="Date in the format 'YYYY-MM-DD'")

    @method_tool(args_schema=FetchForecastTemperatureInput)
    def fetch_forecast_temperature(self, location: str, dt_str: str) -> str:
        """Fetch the forecast temperature data for a location"""
        return "35 degrees Celsius"


@pytest.fixture
def authenticated_client(client):
    User.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")
    return client


# Assistant Views


def test_list_assistants_with_results(client):
    response = client.get(reverse("django_ai_assistant:assistants_list"))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [{"id": "temperature_assistant", "name": "Temperature Assistant"}]


def test_does_not_list_assistants_if_unauthorized():
    # TODO: Implement this test once permissions are in place
    pass


def test_get_assistant_that_exists(client):
    response = client.get(
        reverse(
            "django_ai_assistant:assistant_detail", kwargs={"assistant_id": "temperature_assistant"}
        )
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"id": "temperature_assistant", "name": "Temperature Assistant"}


def test_get_assistant_that_does_not_exist(client):
    with pytest.raises(AIAssistantNotDefinedError):
        client.get(
            reverse(
                "django_ai_assistant:assistant_detail", kwargs={"assistant_id": "fake_assistant"}
            )
        )


def test_does_not_return_assistant_if_unauthorized():
    # TODO: Implement this test once permissions are in place
    pass


# Threads Views

# GET


@pytest.mark.django_db(transaction=True)
def test_list_threads_without_results(authenticated_client):
    response = authenticated_client.get(reverse("django_ai_assistant:threads_list_create"))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.django_db(transaction=True)
def test_list_threads_with_results(authenticated_client):
    user = User.objects.first()
    baker.make(Thread, created_by=user, _quantity=2)
    response = authenticated_client.get(reverse("django_ai_assistant:threads_list_create"))

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 2


@pytest.mark.django_db(transaction=True)
def test_does_not_list_other_users_threads(authenticated_client):
    baker.make(Thread)
    response = authenticated_client.get(reverse("django_ai_assistant:threads_list_create"))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.django_db(transaction=True)
def test_gets_specific_thread(authenticated_client):
    thread = baker.make(Thread, created_by=User.objects.first())
    response = authenticated_client.get(
        reverse("django_ai_assistant:thread_detail_update_delete", kwargs={"thread_id": thread.id})
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json().get("id") == thread.id


def test_does_not_list_threads_if_unauthorized():
    # TODO: Implement this test once permissions are in place
    pass


# POST


@pytest.mark.django_db(transaction=True)
def test_create_thread(authenticated_client):
    response = authenticated_client.post(
        reverse("django_ai_assistant:threads_list_create"), data={}, content_type="application/json"
    )

    thread = Thread.objects.first()

    assert response.status_code == HTTPStatus.OK
    assert response.json().get("id") == thread.id


def test_cannot_create_thread_if_unauthorized():
    # TODO: Implement this test once permissions are in place
    pass


# PATCH


@pytest.mark.django_db(transaction=True)
def test_update_thread(authenticated_client):
    thread = baker.make(Thread, created_by=User.objects.first())
    response = authenticated_client.patch(
        reverse("django_ai_assistant:thread_detail_update_delete", kwargs={"thread_id": thread.id}),
        data={"name": "New name"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK
    assert Thread.objects.filter(id=thread.id).first().name == "New name"


@pytest.mark.django_db(transaction=True)
def test_cannot_update_other_users_threads(authenticated_client):
    thread = baker.make(Thread)
    response = authenticated_client.patch(
        reverse("django_ai_assistant:thread_detail_update_delete", kwargs={"thread_id": thread.id}),
        data={"name": "New name"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert Thread.objects.filter(id=thread.id).first().name != "New name"


def test_cannot_update_thread_if_unauthorized():
    # TODO: Implement this test once permissions are in place
    pass


# DELETE


@pytest.mark.django_db(transaction=True)
def test_delete_thread(authenticated_client):
    thread = baker.make(Thread, created_by=User.objects.first())
    response = authenticated_client.delete(
        reverse("django_ai_assistant:thread_detail_update_delete", kwargs={"thread_id": thread.id})
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not Thread.objects.filter(id=thread.id).exists()


@pytest.mark.django_db(transaction=True)
def test_cannot_delete_other_users_threads(authenticated_client):
    thread = baker.make(Thread)
    response = authenticated_client.delete(
        reverse("django_ai_assistant:thread_detail_update_delete", kwargs={"thread_id": thread.id})
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert Thread.objects.filter(id=thread.id).exists()


def test_cannot_delete_thread_if_unauthorized():
    # TODO: Implement this test once permissions are in place
    pass


# Threads Messages Views (will need VCR)

# GET


@pytest.mark.django_db(transaction=True)
@pytest.mark.vcr
def test_list_thread_messages(authenticated_client):
    thread = baker.make(Thread, created_by=User.objects.first())
    create_thread_message_as_user(thread.id, "Hello", User.objects.first())
    response = authenticated_client.get(
        reverse("django_ai_assistant:messages_list_create", kwargs={"thread_id": thread.id})
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db(transaction=True)
@pytest.mark.vcr
def test_does_not_list_thread_messages_if_not_thread_user(authenticated_client):
    with pytest.raises(AIUserNotAllowedError):
        thread = baker.make(Thread)
        create_thread_message_as_user(thread.id, "Hello", User.objects.create())
        authenticated_client.get(
            reverse("django_ai_assistant:messages_list_create", kwargs={"thread_id": thread.id})
        )


# POST

# @pytest.mark.django_db(transaction=True)
# def test_create_thread_message(authenticated_client):
#     create_thread_message
