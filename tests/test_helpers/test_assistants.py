import sys
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

from django_ai_assistant.exceptions import (
    AIAssistantMisconfiguredError,
)
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
                        "id": "call_jI6UNFQO0vy6fVPwrtRqoM5Y",
                        "type": "tool_call",
                    }
                ],
            ),
            ToolMessage(
                content="32 degrees Celsius",
                name="fetch_current_temperature",
                id="3",
                tool_call_id="call_jI6UNFQO0vy6fVPwrtRqoM5Y",
            ),
            AIMessage(
                content="The current temperature in Recife is 32 degrees Celsius.",
                id="4",
            ),
            HumanMessage(
                content="What about tomorrow?",
                additional_kwargs={},
                response_metadata={},
                id="5",
            ),
            AIMessage(
                content="",
                id="6",
                tool_calls=[
                    {
                        "name": "fetch_forecast_temperature",
                        "args": {"location": "Recife", "dt_str": "2024-06-10"},
                        "id": "call_9BilBWvCVWEmtfQeYknNqSxt",
                        "type": "tool_call",
                    }
                ],
            ),
            ToolMessage(
                content="35 degrees Celsius",
                name="fetch_forecast_temperature",
                id="7",
                tool_call_id="call_9BilBWvCVWEmtfQeYknNqSxt",
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


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Not supported on Python 3.10")
@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@pytest.mark.vcr
async def test_AIAssistant_astream():
    thread = await Thread.objects.acreate(name="Recife Temperature Chat")
    assistant = AIAssistant.get_cls("temperature_assistant")()
    response = "".join(
        [
            stream_response
            async for stream_response in assistant.astream(
                "What is the temperature today in Recife?",
                thread=thread,
            )
        ]
    )
    assert response == "The current temperature in Recife is 32 degrees Celsius."


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
        "You're right next to the American Museum of Natural History, where you can explore fascinating exhibits about dinosaurs, space, and human cultures. Additionally, enjoy a stroll through Central Park to experience its beautiful landscapes and iconic landmarks like Belvedere Castle and Bow Bridge. Don't miss the opportunity to visit both these highlights!"
    )
    assert response_1["input"] == "11 W 53rd St, New York, NY 10019, United States."
    assert response_1["output"] == (
        "You're right by the Museum of Modern Art (MoMA), which houses an impressive collection of modern and contemporary art, including works by Van Gogh and Warhol. Enjoy exploring the vibrant gallery spaces and temporary exhibitions. It's a must-visit for art enthusiasts!"
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


@patch("langchain_openai.ChatOpenAI")
def test_AIAssistant_get_llm_default_temperature(mock_chat_openai):
    class DefaultTempAssistant(AIAssistant):
        id = "default_temp_assistant"  # noqa: A003
        name = "Default Temp Assistant"
        instructions = "Instructions"
        model = "gpt-test"

    assistant = DefaultTempAssistant()
    assistant.get_llm()

    mock_chat_openai.assert_called_once_with(
        model="gpt-test",
        temperature=1.0,
        model_kwargs={},
    )

    AIAssistant.clear_cls_registry()


@patch("langchain_openai.ChatOpenAI")
def test_AIAssistant_get_llm_custom_float_temperature(mock_chat_openai):
    custom_temperature = 0.5

    class CustomFloatTempAssistant(AIAssistant):
        id = "custom_float_temp_assistant"  # noqa: A003
        name = "Custom Float Temp Assistant"
        instructions = "Instructions"
        model = "gpt-test"
        temperature = custom_temperature

    assistant = CustomFloatTempAssistant()
    assistant.get_llm()

    mock_chat_openai.assert_called_once_with(
        model="gpt-test",
        temperature=custom_temperature,
        model_kwargs={},
    )

    AIAssistant.clear_cls_registry()


@patch("langchain_openai.ChatOpenAI")
def test_AIAssistant_get_llm_override_get_temperature_with_float(mock_chat_openai):
    custom_temperature = 0.5

    class OverrideGetFloatTempAssistant(AIAssistant):
        id = "override_get_float_temp_assistant"  # noqa: A003
        name = "Override Get Float Temp Assistant"
        instructions = "Instructions"
        model = "gpt-test"

        def get_temperature(self) -> float | None:
            return custom_temperature

    assistant = OverrideGetFloatTempAssistant()
    assistant.get_llm()

    mock_chat_openai.assert_called_once_with(
        model="gpt-test",
        temperature=custom_temperature,
        model_kwargs={},
    )

    AIAssistant.clear_cls_registry()


@patch("langchain_openai.ChatOpenAI")
def test_AIAssistant_get_llm_custom_none_temperature(mock_chat_openai):
    class CustomNoneTempAssistant(AIAssistant):
        id = "custom_none_temp_assistant"  # noqa: A003
        name = "Custom None Temp Assistant"
        instructions = "Instructions"
        model = "gpt-test"
        temperature = None

    assistant = CustomNoneTempAssistant()
    assistant.get_llm()

    mock_chat_openai.assert_called_once_with(
        model="gpt-test",
        model_kwargs={},
    )
    _, call_kwargs = mock_chat_openai.call_args
    assert "temperature" not in call_kwargs

    AIAssistant.clear_cls_registry()


@patch("langchain_openai.ChatOpenAI")
def test_AIAssistant_get_llm_override_get_temperature_with_none(mock_chat_openai):
    class OverrideGetNoneTempAssistant(AIAssistant):
        id = "override_get_none_temp_assistant"  # noqa: A003
        name = "Override Get None Temp Assistant"
        instructions = "Instructions"
        model = "gpt-test"

        def get_temperature(self) -> float | None:
            return None

    assistant = OverrideGetNoneTempAssistant()
    assistant.get_llm()

    mock_chat_openai.assert_called_once_with(
        model="gpt-test",
        model_kwargs={},
    )
    _, call_kwargs = mock_chat_openai.call_args
    assert "temperature" not in call_kwargs

    AIAssistant.clear_cls_registry()


@patch("langchain_openai.ChatOpenAI")
def test_AIAssistant_get_llm_openai_provider(mock_chat_openai):
    class OpenaiAIAssistant(AIAssistant):
        id = "override_anthropic_assistant"  # noqa: A003
        name = "Override OpenAI Assistant"
        instructions = "Instructions"
        model = "gpt-test"

    assistant = OpenaiAIAssistant(provider="openai")
    assistant.get_llm()

    mock_chat_openai.assert_called_once_with(
        model="gpt-test",
        temperature=1.0,
        model_kwargs={},
    )

    AIAssistant.clear_cls_registry()


@patch("langchain_anthropic.ChatAnthropic")
def test_AIAssistant_get_llm_anthropic_provider(mock_chat_anthropic):
    class AnthropicAIAssistant(AIAssistant):
        id = "override_anthropic_assistant"  # noqa: A003
        name = "Override Anthropic Assistant"
        instructions = "Instructions"
        model = "gpt-test"

    assistant = AnthropicAIAssistant(provider="anthropic")
    assistant.get_llm()

    mock_chat_anthropic.assert_called_once_with(
        model="gpt-test",
        temperature=1.0,
        model_kwargs={},
    )

    AIAssistant.clear_cls_registry()


@patch("langchain_google_genai.ChatGoogleGenerativeAI")
def test_AIAssistant_get_llm_google_provider(mock_chat_google):
    class GoogleAIAssistant(AIAssistant):
        id = "override_google_assistant"  # noqa: A003
        name = "Override Google Assistant"
        instructions = "Instructions"
        model = "gpt-test"

    assistant = GoogleAIAssistant(provider="google")
    assistant.get_llm()

    mock_chat_google.assert_called_once_with(
        model="gpt-test",
        temperature=1.0,
        model_kwargs={},
    )

    AIAssistant.clear_cls_registry()


def test_AIAssistant_get_llm_invalid_provider():
    class InvalidAIAssistant(AIAssistant):
        id = "override_invalid_assistant"  # noqa: A003
        name = "Override Invalid Assistant"
        instructions = "Instructions"
        model = "gpt-test"

    assistant = InvalidAIAssistant(provider="invalid")
    with pytest.raises(AIAssistantMisconfiguredError):
        assistant.get_llm()


def test_AIAssistant_get_llm_uninstalled_provider(monkeypatch):
    class UninstalledAIAssistant(AIAssistant):
        id = "override_uninstalled_assistant"  # noqa: A003
        name = "Override Uninstalled Assistant"
        instructions = "Instructions"
        model = "gpt-test"

    assistant = UninstalledAIAssistant(provider="uninstalled")

    # Simulates a scenario where the user tries to use a valid provider
    # that isn't installed with lib (i.e.: user tries to access the
    # openai provider, but langchain_openai isn't installed)
    from django_ai_assistant.helpers import assistants

    monkeypatch.setattr(
        assistants,
        "PROVIDER_LLM_LOOKUP",
        {
            "uninstalled": {
                "langchain_module": "test_module",
                "llm_class": "UninstalledChat",
            },
        },
    )

    with pytest.raises(ImportError):
        assistant.get_llm()


def test_AIAssistant_get_llm_invalid_llm_class_for_provider(monkeypatch):
    class InvalidClassAIAssistant(AIAssistant):
        id = "override_invalid_class_assistant"  # noqa: A003
        name = "Override Invalid Class Assistant"
        instructions = "Instructions"
        model = "gpt-test"

    assistant = InvalidClassAIAssistant(provider="openai")

    from django_ai_assistant.helpers import assistants

    monkeypatch.setattr(
        assistants,
        "PROVIDER_LLM_LOOKUP",
        {
            "openai": {
                "langchain_module": "math",
                "llm_class": "NotExistingClass",
            },
        },
    )

    with pytest.raises(ImportError):
        assistant.get_llm()


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
