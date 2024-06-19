from http import HTTPStatus

import pytest

from django_ai_assistant.exceptions import AIAssistantNotDefinedError
from django_ai_assistant.helpers.assistants import AIAssistant
from django_ai_assistant.langchain.tools import BaseModel, Field, method_tool


# Set up


@pytest.fixture(scope="module", autouse=True)
def setup_assistants():
    # Clear the registry before the tests in the module
    AIAssistant.clear_registry()

    # Define the assistant class inside the fixture to ensure registration
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

    yield
    # Clear the registry after the tests in the module
    AIAssistant.clear_registry()


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

# Up next
