from http import HTTPStatus

from django.contrib.auth.models import User

import pytest
from model_bakery import baker

from django_ai_assistant.exceptions import AIAssistantNotDefinedError
from django_ai_assistant.helpers.assistants import AIAssistant, register_assistant
from django_ai_assistant.langchain.tools import BaseModel, Field, method_tool
from django_ai_assistant.models import Thread


# Set up


@register_assistant
class TemperatureAssistant(AIAssistant):
    id = "temperature_assistant"  # noqa: A003
    name = "Temperature Assistant"
    description = "A temperature assistant that provides temperature information."
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
    response = client.get("/assistants/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [{"id": "temperature_assistant", "name": "Temperature Assistant"}]


def test_does_not_list_assistants_if_unauthorized():
    # TODO: Implement this test once permissions are in place
    pass


def test_get_assistant_that_exists(client):
    response = client.get("/assistants/temperature_assistant/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"id": "temperature_assistant", "name": "Temperature Assistant"}


def test_get_assistant_that_does_not_exist(client):
    with pytest.raises(AIAssistantNotDefinedError):
        client.get("/assistants/fake_assistant/")


def test_does_not_return_assistant_if_unauthorized():
    # TODO: Implement this test once permissions are in place
    pass


# Threads Views


@pytest.mark.django_db(transaction=True)
def test_list_threads_without_results(authenticated_client):
    response = authenticated_client.get("/threads/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.django_db(transaction=True)
def test_list_threads_with_results(authenticated_client):
    user = User.objects.first()
    thread = baker.make(Thread, created_by=user)
    response = authenticated_client.get("/threads/")

    assert response.status_code == HTTPStatus.OK
    assert response.json()[0].get("id") == thread.id
