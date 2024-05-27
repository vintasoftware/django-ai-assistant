from collections.abc import Callable
from typing import Any, Protocol

from openai import OpenAI

from ..conf import settings
from ..models import Assistant
from .function_calling import EventHandler
from .function_tool import FunctionTool


class AIAssistant(Protocol):
    name: str
    instructions: str
    fns: tuple[Callable[..., Any], ...]
    model: str = "gpt-4o"


assistant_cls_registry: dict[str, type[AIAssistant]] = {}


def register_assistant(cls: type[AIAssistant]):
    assistant_cls_registry[cls.__name__] = cls
    return cls


def get_tools(assistant_cls: type[AIAssistant]):
    fns_tools = [FunctionTool.from_defaults(fn=fn) for fn in assistant_cls.fns]
    tools = [t.metadata.to_openai_tool() for t in fns_tools]
    return fns_tools, tools


def sync_assistants(model: str = "gpt-4o"):
    # TODO: fix to really sync: update what exists, create what doesn't

    client = settings.call_fn("CLIENT_INIT_FN")
    assistant_open_ids = []

    for slug, assistant_cls in assistant_cls_registry.items():
        __, tools = get_tools(assistant_cls)
        openai_assistant = client.beta.assistants.create(
            instructions=assistant_cls.instructions,
            name=assistant_cls.name,
            tools=tools,
            model=model,
        )
        Assistant.objects.create(
            slug=slug,
            name=assistant_cls.name,
            openai_id=openai_assistant.id,
        )
        assistant_open_ids.append(openai_assistant.id)

    return assistant_open_ids


def get_class_from_slug(django_assistant: Assistant):
    return assistant_cls_registry.get(django_assistant.slug)


def run_assistant(client: OpenAI, openai_thread_id: str, openai_assistant_id: str):
    django_assistant = Assistant.objects.get(openai_id=openai_assistant_id)
    assistant_cls = get_class_from_slug(django_assistant)
    if not assistant_cls:
        # TODO: make custom exception in .exceptions.py
        return Exception("Assistant class not found")

    fns_tools, __ = get_tools(assistant_cls)
    event_handler = EventHandler(client, fns_tools)
    with client.beta.threads.runs.stream(
        thread_id=openai_thread_id, assistant_id=openai_assistant_id, event_handler=event_handler
    ) as stream:
        stream.until_done()
    return stream
