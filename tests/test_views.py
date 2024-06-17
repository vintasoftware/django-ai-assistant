from http import HTTPStatus

from django.test import Client, TestCase

import pytest

from django_ai_assistant.exceptions import AIAssistantNotDefinedError
from django_ai_assistant.helpers.assistants import AIAssistant, register_assistant
from django_ai_assistant.tools import BaseModel, Field, method_tool


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


# Assistant Views


class AssistantViewsTests(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_list_assistants_with_results(self):
        response = self.client.get("/assistants/")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == [{"id": "temperature_assistant", "name": "Temperature Assistant"}]

    def test_does_not_list_assistants_if_unauthorized(self):
        # TODO: Implement this test once permissions are in place
        pass

    def test_get_assistant_that_exists(self):
        response = self.client.get("/assistants/temperature_assistant/")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"id": "temperature_assistant", "name": "Temperature Assistant"}

    def test_get_assistant_that_does_not_exist(self):
        with pytest.raises(AIAssistantNotDefinedError):
            self.client.get("/assistants/fake_assistant/")

    def test_does_not_return_assistant_if_unauthorized(self):
        # TODO: Implement this test once permissions are in place
        pass


# Threads Views

# Up next
