from typing import List, TypedDict
from unittest.mock import patch

import pytest
from langchain_core.documents import Document
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
    messages_to_dict,
)
from langchain_core.retrievers import BaseRetriever

from django_ai_assistant.helpers.assistants import AIAssistant
from django_ai_assistant.langchain.tools import BaseModel, Field, method_tool
from django_ai_assistant.models import Thread


@pytest.fixture(scope="module", autouse=True)
def setup_assistants():
    # Clear the registry before the tests in the module
    AIAssistant.clear_cls_registry()

    # Define the assistant class inside the fixture to ensure registration
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

    class TourGuideAssistant(AIAssistant):
        id = "tour_guide_assistant"  # noqa: A003
        name = "Tour Guide Assistant"
        instructions = (
            "You are a tour guide assistant offers information about nearby attractions. "
            "The user is at a location and wants to know what to learn about nearby attractions. "
            "Use the following pieces of context to suggest nearby attractions to the user. "
            "If there are no interesting attractions nearby, "
            "tell the user there's nothing to see where they're at. "
            "Use three sentences maximum and keep your suggestions concise."
        )
        model = "gpt-4o"
        has_rag = True

        def get_retriever(self) -> BaseRetriever:
            return SequentialRetriever(
                sequential_responses=[
                    [
                        Document(page_content="Central Park"),
                        Document(page_content="American Museum of Natural History"),
                    ],
                    [Document(page_content="Museum of Modern Art")],
                ]
            )

    yield
    # Clear the registry after the tests in the module
    AIAssistant.clear_cls_registry()


@pytest.mark.django_db(transaction=True)
@pytest.mark.vcr
def test_AIAssistant_invoke():
    thread = Thread.objects.create(name="Recife Temperature Chat")

    assistant = AIAssistant.get_cls("temperature_assistant")()
    assistant.invoke(
        {"input": "What is the temperature today in Recife?"},
        thread_id=thread.id,
    )
    response = assistant.invoke(
        {"input": "What about tomorrow?"},
        thread_id=thread.id,
    )
    response_messages = messages_to_dict(response["messages"])
    stored_messages = messages_to_dict(thread.get_messages(include_extra_messages=True))

    expected_messages = messages_to_dict(
        [
            HumanMessage(
                content="What is the temperature today in Recife?",
                id="1",
            ),
            AIMessage(
                content="",
                id="2",
                tool_calls=[
                    {
                        "name": "fetch_current_temperature",
                        "args": {"location": "Recife"},
                        "id": "call_mp680g1ciZRb9eaRoWZUpMWG",
                        "type": "tool_call",
                    }
                ],
            ),
            ToolMessage(
                content="32 degrees Celsius",
                name="fetch_current_temperature",
                id="3",
                tool_call_id="call_mp680g1ciZRb9eaRoWZUpMWG",
            ),
            AIMessage(
                content="The current temperature in Recife is 32 degrees Celsius.",
                id="4",
            ),
            HumanMessage(
                content="What about tomorrow?", additional_kwargs={}, response_metadata={}, id="5"
            ),
            AIMessage(
                content="",
                id="6",
                tool_calls=[
                    {
                        "name": "fetch_forecast_temperature",
                        "args": {"location": "Recife", "dt_str": "2024-06-10"},
                        "id": "call_5Y5P4y5m0VFzh5GE0RNeEkyP",
                        "type": "tool_call",
                    }
                ],
            ),
            ToolMessage(
                content="35 degrees Celsius",
                name="fetch_forecast_temperature",
                id="7",
                tool_call_id="call_5Y5P4y5m0VFzh5GE0RNeEkyP",
            ),
            AIMessage(
                content="The forecasted temperature for tomorrow in Recife is 35 degrees Celsius.",
                id="8",
            ),
        ]
    )
    assert response_messages[0]["data"]["type"] == "system"
    assert (
        response_messages[0]["data"]["content"] == "You are a temperature bot. Today is 2024-06-09."
    )
    for attr in ["id", "content", "type", "tool_calls", "tool_call_id"]:
        assert [m["data"].get(attr) for m in list(response_messages[1:])] == [
            m["data"].get(attr) for m in expected_messages
        ]
        assert [m["data"].get(attr) for m in list(stored_messages)] == [
            m["data"].get(attr) for m in expected_messages
        ]


def test_AIAssistant_run_handles_optional_thread_id_param():
    assistant = AIAssistant.get_cls("temperature_assistant")()

    with patch.object(assistant, "invoke") as invoke_spy:
        assistant.run("What is the temperature today in Recife?")

        invoke_spy.assert_called_once_with(
            {"input": "What is the temperature today in Recife?"}, thread_id=None
        )


class SequentialRetriever(BaseRetriever):
    sequential_responses: List[List[Document]]
    response_index: int = 0

    def _get_relevant_documents(self, query: str) -> List[Document]:
        if self.response_index >= len(self.sequential_responses):
            return []
        else:
            self.response_index += 1
            return self.sequential_responses[self.response_index - 1]

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query)


@pytest.mark.django_db(transaction=True)
@pytest.mark.vcr
def test_AIAssistant_with_rag_invoke():
    thread = Thread.objects.create(name="Tour Guide Chat")

    assistant = AIAssistant.get_cls("tour_guide_assistant")()
    response_0 = assistant.invoke(
        {"input": "I'm at Central Park W & 79st, New York, NY 10024, United States."},
        thread_id=thread.id,
    )
    response_1 = assistant.invoke(
        {"input": "11 W 53rd St, New York, NY 10019, United States."},
        thread_id=thread.id,
    )

    messages = thread.messages.order_by("created_at").values_list("message", flat=True)
    messages_ids = thread.messages.order_by("created_at").values_list("id", flat=True)

    assert response_0["input"] == "I'm at Central Park W & 79st, New York, NY 10024, United States."
    assert response_0["output"] == (
        "You are right by the American Museum of Natural History, where you can explore "
        "fascinating exhibits on dinosaurs, space, and human cultures. "
        "In addition, Central Park offers scenic walking paths, boating on the lake, "
        "and the iconic Bethesda Terrace. Enjoy your visit!"
    )
    assert response_1["input"] == "11 W 53rd St, New York, NY 10019, United States."
    assert response_1["output"] == (
        "You're at the Museum of Modern Art, which features an impressive collection of "
        "contemporary and modern artworks, including pieces by Van Gogh and Warhol. "
        "Nearby, you can also visit the iconic Rockefeller Center. "
        "Enjoy the artistic and cultural experiences!"
    )

    expected_messages = messages_to_dict(
        [
            HumanMessage(content=response_0["input"], id=messages_ids[0]),
            AIMessage(content=response_0["output"], id=messages_ids[1]),
            HumanMessage(content=response_1["input"], id=messages_ids[2]),
            AIMessage(content=response_1["output"], id=messages_ids[3]),
        ]
    )

    assert [m["data"]["content"] for m in list(messages)] == [
        m["data"]["content"] for m in expected_messages
    ]
    assert [m["data"]["id"] for m in list(messages)] == [m["data"]["id"] for m in expected_messages]


@pytest.mark.django_db(transaction=True)
def test_AIAssistant_tool_order_same_as_declaration():
    class FooAssistant(AIAssistant):
        id = "foo_assistant"  # noqa: A003
        name = "Foo Assistant"
        instructions = "You are a helpful assistant."
        model = "gpt-4o"

        @method_tool
        def tool_d(self, foo: str, bar: float, baz: int, qux: str) -> str:
            """Tool D"""
            return "DDD"

        @method_tool
        def tool_c(self, foo: str, bar: float, baz: int) -> str:
            """Tool C"""
            return "CCC"

        @method_tool
        def tool_b(self, foo: str, bar: float) -> str:
            """Tool B"""
            return "BBB"

        @method_tool
        def tool_a(self, foo: str) -> str:
            """Tool A"""
            return "AAA"

    assistant = FooAssistant()

    assert hasattr(assistant, "_method_tools")
    assert [t.name for t in assistant._method_tools] == [
        "tool_d",
        "tool_c",
        "tool_b",
        "tool_a",
    ]


@pytest.mark.vcr
def test_AIAssistant_pydantic_structured_output():
    from pydantic import BaseModel

    class OutputSchema(BaseModel):
        name: str
        age: int
        is_student: bool

    class StructuredOutputAssistant(AIAssistant):
        id = "structured_output_assistant"  # noqa: A003
        name = "Structured Output Assistant"
        instructions = "You are a helpful assistant that provides information about people."
        model = "gpt-4o-2024-08-06"
        structured_output = OutputSchema

    assistant = StructuredOutputAssistant()

    # Test invoking the assistant with structured output
    result = assistant.run("Tell me about John who is 30 years old and not a student.")
    assert isinstance(result, OutputSchema)
    assert result.name == "John"
    assert result.age == 30
    assert result.is_student is False


@pytest.mark.vcr
def test_AIAssistant_typeddict_structured_output():
    class OutputSchema(TypedDict):
        title: str
        year: int
        genres: List[str]

    class DictStructuredOutputAssistant(AIAssistant):
        id = "dict_structured_output_assistant"  # noqa: A003
        name = "Dict Structured Output Assistant"
        instructions = "You are a helpful assistant that provides information about movies."
        model = "gpt-4o-2024-08-06"
        structured_output = OutputSchema

    assistant = DictStructuredOutputAssistant()

    # Test invoking the assistant with dict structured output
    result = assistant.run(
        "Provide information about the movie Shrek. "
        "It was released in 2001 and is an animation and comedy movie."
    )

    assert result["title"] == "Shrek"
    assert result["year"] == 2001
    assert result["genres"] == ["Animation", "Comedy"]
