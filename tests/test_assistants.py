from typing import List

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, messages_to_dict
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
            "\n\n"
            "---START OF CONTEXT---\n"
            "{context}"
            "---END OF CONTEXT---\n"
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
    response_0 = assistant.invoke(
        {"input": "What is the temperature today in Recife?"},
        thread_id=thread.id,
    )
    response_1 = assistant.invoke(
        {"input": "What about tomorrow?"},
        thread_id=thread.id,
    )

    messages = thread.messages.order_by("created_at").values_list("message", flat=True)
    messages_ids = thread.messages.order_by("created_at").values_list("id", flat=True)

    assert response_0 == {
        "history": [],
        "input": "What is the temperature today in Recife?",
        "output": "The current temperature in Recife today is 32 degrees Celsius.",
    }
    assert response_1 == {
        "history": [
            HumanMessage(content="What is the temperature today in Recife?", id=messages_ids[0]),
            AIMessage(
                content="The current temperature in Recife today is 32 degrees Celsius.",
                id=messages_ids[1],
            ),
        ],
        "input": "What about tomorrow?",
        "output": "The forecasted temperature in Recife for tomorrow, June 10, 2024, is "
        "expected to be 35 degrees Celsius.",
    }
    assert list(messages) == messages_to_dict(
        [
            HumanMessage(content="What is the temperature today in Recife?", id=messages_ids[0]),
            AIMessage(
                content="The current temperature in Recife today is 32 degrees Celsius.",
                id=messages_ids[1],
            ),
            HumanMessage(content="What about tomorrow?", id=messages_ids[2]),
            AIMessage(
                content="The forecasted temperature in Recife for tomorrow, June 10, 2024, is "
                "expected to be 35 degrees Celsius.",
                id=messages_ids[3],
            ),
        ]
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

    assert response_0 == {
        "history": [],
        "input": "I'm at Central Park W & 79st, New York, NY 10024, United States.",
        "output": "You're right by the American Museum of Natural History, one of the "
        "largest museums in the world, featuring fascinating exhibits on "
        "dinosaurs, human origins, and outer space. Additionally, you're at the "
        "edge of Central Park, a sprawling urban oasis with scenic walking trails, "
        "lakes, and the iconic Central Park Zoo. Enjoy the blend of natural beauty "
        "and cultural richness!",
    }
    assert response_1 == {
        "history": [
            HumanMessage(content=response_0["input"], id=messages_ids[0]),
            AIMessage(content=response_0["output"], id=messages_ids[1]),
        ],
        "input": "11 W 53rd St, New York, NY 10019, United States.",
        "output": "You're at the location of the Museum of Modern Art (MoMA), home to an "
        "extensive collection of modern and contemporary art, including works by "
        "Van Gogh, Picasso, and Warhol. Nearby, you can also visit Rockefeller "
        "Center, known for its impressive architecture and the Top of the Rock "
        "observation deck. These attractions offer a blend of artistic and urban "
        "experiences.",
    }
    assert list(messages) == messages_to_dict(
        [
            HumanMessage(content=response_0["input"], id=messages_ids[0]),
            AIMessage(content=response_0["output"], id=messages_ids[1]),
            HumanMessage(content=response_1["input"], id=messages_ids[2]),
            AIMessage(content=response_1["output"], id=messages_ids[3]),
        ]
    )


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
    assert [t.name for t in assistant._method_tools] == ["tool_d", "tool_c", "tool_b", "tool_a"]
