import pytest
from langchain_core.messages import AIMessage, HumanMessage, messages_to_dict

from django_ai_assistant.helpers.assistants import AIAssistant
from django_ai_assistant.models import Thread
from django_ai_assistant.tools import BaseModel, Field, method_tool


class TemperatureAssistant(AIAssistant):
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


@pytest.mark.django_db(transaction=True)
@pytest.mark.vcr
def test_AIAssistant_invoke():
    thread = Thread.objects.create(name="Recife Temperature Chat")

    assistant = TemperatureAssistant()
    response_0 = assistant.invoke(
        {"input": "What is the temperature today in Recife?"},
        thread_id=thread.id,
    )
    response_1 = assistant.invoke(
        {"input": "What about tomorrow?"},
        thread_id=thread.id,
    )

    assert response_0 == {
        "history": [],
        "input": "What is the temperature today in Recife?",
        "output": "The current temperature in Recife today is 32 degrees Celsius.",
    }
    assert response_1 == {
        "history": [
            HumanMessage(content="What is the temperature today in Recife?"),
            AIMessage(content="The current temperature in Recife today is 32 degrees Celsius."),
        ],
        "input": "What about tomorrow?",
        "output": "The forecasted temperature in Recife for tomorrow, June 10, 2024, is "
        "expected to be 35 degrees Celsius.",
    }
    assert list(
        thread.messages.order_by("created_at").values_list("message", flat=True)
    ) == messages_to_dict(
        [
            HumanMessage(content="What is the temperature today in Recife?"),
            AIMessage(content="The current temperature in Recife today is 32 degrees Celsius."),
            HumanMessage(content="What about tomorrow?"),
            AIMessage(
                content="The forecasted temperature in Recife for tomorrow, June 10, 2024, is "
                "expected to be 35 degrees Celsius."
            ),
        ]
    )
