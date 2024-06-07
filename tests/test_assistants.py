import json
from typing import Generator, override

import openai_responses
import pytest
from langchain_core.messages import AIMessage, HumanMessage, messages_to_dict
from openai.types.chat import ChatCompletionChunk
from openai_responses import OpenAIMock
from openai_responses.ext.httpx import Request, Response
from openai_responses.streaming import Event, EventStream

from django_ai_assistant.helpers.assistants import AIAssistant
from django_ai_assistant.models import Thread
from django_ai_assistant.tools import BaseModel, Field, tool


class WeatherAssistant(AIAssistant):
    name = "Weather Assistant"
    description = "A weather assistant that provides weather information."
    instructions = "You are a weather bot."
    model = "gpt-4o"

    @tool
    def fetch_current_weather(self, location: str) -> dict:
        """Fetch the current weather data for a location"""
        return {}

    class FetchForecastWeatherInput(BaseModel):
        location: str
        dt_str: str = Field(description="Date in the format 'YYYY-MM-DD'")

    @tool(args_schema=FetchForecastWeatherInput)
    def fetch_forecast_weather(self, location: str, dt_str: str) -> dict:
        """Fetch the forecast weather data for a location"""
        return {}


class CreateChatCompletionEventStream(EventStream):
    @override
    def generate(self) -> Generator[Event, None, None]:
        chunk = ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": 1694268190,
                "model": "gpt-4o",
                "system_fingerprint": "fp_44709d6fcb",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": ""},
                        "logprobs": None,
                        "finish_reason": None,
                    }
                ],
            }
        )
        yield self.event(None, chunk)

        chunk = ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": 1694268190,
                "model": "gpt-4o",
                "system_fingerprint": "fp_44709d6fcb",
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": "The weather in New York City is 72 degrees Fahrenheit."
                        },
                        "logprobs": None,
                        "finish_reason": None,
                    }
                ],
            }
        )
        yield self.event(None, chunk)

        chunk = ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": 1694268190,
                "model": "gpt-4o",
                "system_fingerprint": "fp_44709d6fcb",
                "choices": [{"index": 0, "delta": {}, "logprobs": None, "finish_reason": "stop"}],
            }
        )
        yield self.event(None, chunk)


def create_chat_completion_response(request: Request) -> Response:
    stream = CreateChatCompletionEventStream()
    return Response(201, content=stream)


@pytest.mark.django_db
@openai_responses.mock()
def test_AIAssistant_invoke(openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = create_chat_completion_response
    thread = Thread.objects.create(name="Test Thread")

    assistant = WeatherAssistant()
    response = assistant.invoke(
        {"input": "What is the weather in New York?"},
        thread_id=thread.id,
    )

    assert openai_mock.chat.completions.create.route.call_count == 1
    assert response == {
        "history": [],
        "input": "What is the weather in New York?",
        "output": "The weather in New York City is 72 degrees Fahrenheit.",
    }
    assert list(
        thread.messages.order_by("created_at").values_list("message", flat=True)
    ) == messages_to_dict(
        [
            HumanMessage(content="What is the weather in New York?"),
            AIMessage(content="The weather in New York City is 72 degrees Fahrenheit."),
        ]
    )


@pytest.mark.django_db
@openai_responses.mock()
def test_AIAssistant_invoke_request_body(openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = create_chat_completion_response
    thread = Thread.objects.create(name="Test Thread")

    assistant = WeatherAssistant()
    assistant.invoke(
        {"input": "What is the weather in New York?"},
        thread_id=thread.id,
    )
    assert openai_mock.chat.completions.create.route.call_count == 1
    assert openai_mock.chat.completions.create.route.calls[0].request.content != b""
    assert json.loads(openai_mock.chat.completions.create.route.calls[0].request.content) == {
        "messages": [
            {"content": "You are a weather bot.", "role": "system"},
            {"content": "What is the weather in New York?", "role": "user"},
        ],
        "model": "gpt-4o",
        "n": 1,
        "stream": True,
        "temperature": 1.0,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "fetch_current_weather",
                    "description": "Fetch the current weather data for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": ["location"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_forecast_weather",
                    "description": "Fetch the forecast weather data for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "dt_str": {
                                "description": "Date in the format 'YYYY-MM-DD'",
                                "type": "string",
                            },
                        },
                        "required": ["location", "dt_str"],
                    },
                },
            },
        ],
    }
