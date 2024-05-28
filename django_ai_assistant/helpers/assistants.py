from collections.abc import Callable
from typing import Any, Protocol, cast

from django.http import HttpRequest
from django.views import View

from openai import OpenAI

from django_ai_assistant.ai.function_calling import EventHandler
from django_ai_assistant.ai.function_tool import FunctionTool
from django_ai_assistant.conf import settings
from django_ai_assistant.exceptions import AIUserNotAllowedError
from django_ai_assistant.models import Assistant, Thread
from django_ai_assistant.permissions import can_create_thread, can_run_assistant


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
    openai_ids = []

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
        openai_ids.append(openai_assistant.id)

    return openai_ids


def get_class_from_slug(django_assistant: Assistant):
    return assistant_cls_registry.get(django_assistant.slug)


def run_assistant(assistant: Assistant, thread: Thread, client: OpenAI | None = None):
    if not client:
        client = cast(OpenAI, settings.call_fn("CLIENT_INIT_FN"))

    assistant_cls = get_class_from_slug(assistant)
    if not assistant_cls:
        # TODO: make custom exception in .exceptions.py
        raise Exception(f"Assistant class not found: {assistant.slug}")

    fns_tools, __ = get_tools(assistant_cls)
    event_handler = EventHandler(client, fns_tools)
    with client.beta.threads.runs.stream(
        thread_id=thread.openai_id, assistant_id=assistant.openai_id, event_handler=event_handler
    ) as stream:
        stream.until_done()
    return stream


def run_assistant_as_user(
    assistant: Assistant,
    thread: Thread,
    user: Any,
    client: OpenAI | None = None,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    if not can_run_assistant(assistant=assistant, user=user, request=request, view=view):
        raise AIUserNotAllowedError("User is not allowed to use this assistant")
    if not client:
        client = cast(OpenAI, settings.call_fn("CLIENT_INIT_FN"))

    return run_assistant(assistant=assistant, thread=thread, client=client)


def assistants_generator(
    user: Any,
    client: OpenAI | None = None,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    for assistant in Assistant.objects.all():
        if can_run_assistant(assistant=assistant, user=user, request=request, view=view):
            yield assistant


def create_thread(
    name: str,
    user: Any,
    client: OpenAI | None = None,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    if not can_create_thread(user=user, request=request, view=view):
        raise AIUserNotAllowedError("User is not allowed to create threads")
    if not client:
        client = cast(OpenAI, settings.call_fn("CLIENT_INIT_FN"))

    openai_thread = client.beta.threads.create(metadata={"name": name})
    Thread.objects.create(name=name, created_by=user, openai_id=openai_thread.id)
    return openai_thread


def threads_generator(
    user: Any,
    client: OpenAI | None = None,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    # TODO: have more permissions for threads?
    yield from Thread.objects.filter(created_by=user)


def thread_messages_generator(
    openai_thread_id: str,
    user: Any,
    client: OpenAI | None = None,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    # TODO: have more permissions for threads? View thread permission?
    if not client:
        client = cast(OpenAI, settings.call_fn("CLIENT_INIT_FN"))

    thread = Thread.objects.get(openai_id=openai_thread_id)
    if user != thread.created_by:
        raise AIUserNotAllowedError("User is not allowed to view messages in this thread")

    yield from client.beta.threads.messages.list(thread_id=openai_thread_id)


def create_thread_message_as_user(
    openai_thread_id: str,
    content: str,
    user: Any,
    client: OpenAI | None = None,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    # TODO: have more permissions for threads? View thread permission?
    if not client:
        client = cast(OpenAI, settings.call_fn("CLIENT_INIT_FN"))

    thread = Thread.objects.get(openai_id=openai_thread_id)
    if user != thread.created_by:
        raise AIUserNotAllowedError("User is not allowed to create messages in this thread")

    return client.beta.threads.messages.create(
        thread_id=openai_thread_id, role="user", content=content
    )
