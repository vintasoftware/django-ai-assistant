from collections.abc import Callable
from typing import Any, Protocol, cast

from django.http import HttpRequest
from django.utils import timezone
from django.views import View

from openai import OpenAI
from openai.types.beta import FunctionToolParam

from django_ai_assistant.ai.function_calling import EventHandler
from django_ai_assistant.ai.function_tool import FunctionTool
from django_ai_assistant.conf import settings
from django_ai_assistant.exceptions import AIAssistantClsNotDefinedError, AIUserNotAllowedError
from django_ai_assistant.models import Assistant, Thread
from django_ai_assistant.permissions import can_create_thread, can_run_assistant


class AIAssistant(Protocol):
    name: str
    instructions: str
    fns: tuple[Callable[..., Any], ...]
    model: str = "gpt-4o"


ASSISTANT_DEF_CLS_REGISTRY: dict[str, type[AIAssistant]] = {}


def register_assistant(cls: type[AIAssistant]):
    ASSISTANT_DEF_CLS_REGISTRY[cls.__name__] = cls
    return cls


def get_tools(assistant_def_cls: type[AIAssistant]):
    fns_tools = [FunctionTool.from_defaults(fn=fn) for fn in assistant_def_cls.fns]
    tools = [t.metadata.to_openai_tool() for t in fns_tools]
    return fns_tools, tools


def get_assistant_def_cls(assistant: Assistant):
    return ASSISTANT_DEF_CLS_REGISTRY.get(assistant.slug)


def assistant_def_cls_to_model_attrs(cls: type[AIAssistant]) -> dict[str, Any]:
    return {
        "slug": cls.__name__,
        "name": cls.name,
    }


def sync_assistant_def_cls_with_django_assistant(assistant_def_cls: type[AIAssistant]):
    defaults = assistant_def_cls_to_model_attrs(assistant_def_cls)
    del defaults["slug"]  # already on the kwargs of the update_or_create call
    defaults["cls_synced_at"] = timezone.now()
    return Assistant.objects.update_or_create(
        slug=assistant_def_cls.__name__,
        defaults=defaults,
    )


def assistant_def_cls_to_openai_attrs(cls):
    """
    Convert an assistant class to a dictionary of keyword arguments for OpenAI API calls.
    """
    __, tools = get_tools(cls)
    return {
        "instructions": cls.instructions,
        "name": cls.name,
        "tools": cast(list[FunctionToolParam], tools),
        "model": cls.model,
    }


def create_assistant_in_openai(assistant: Assistant, client: OpenAI | None = None):
    if not client:
        client = cast(OpenAI, settings.call_fn("CLIENT_INIT_FN"))

    assistant_def_cls = get_assistant_def_cls(assistant)
    if not assistant_def_cls:
        raise AIAssistantClsNotDefinedError(f"Assistant class not found: {assistant.slug}")

    openai_assistant = client.beta.assistants.create(
        **assistant_def_cls_to_openai_attrs(assistant_def_cls),
    )
    assistant.openai_id = openai_assistant.id
    assistant.openai_synced_at = timezone.now()
    assistant.save()


def update_assistant_in_openai(assistant: Assistant, client: OpenAI | None = None):
    if not client:
        client = cast(OpenAI, settings.call_fn("CLIENT_INIT_FN"))

    assistant_def_cls = get_assistant_def_cls(assistant)
    if not assistant_def_cls:
        raise AIAssistantClsNotDefinedError(f"Assistant class not found: {assistant.slug}")

    client.beta.assistants.update(
        assistant_id=assistant.openai_id,
        **assistant_def_cls_to_openai_attrs(assistant_def_cls),
    )
    assistant.openai_synced_at = timezone.now()
    assistant.save()


def sync_assistant_in_openai(assistant: Assistant, client: OpenAI | None = None):
    if not assistant.openai_id:
        create_assistant_in_openai(assistant, client)
    else:
        update_assistant_in_openai(assistant, client)


def run_assistant(assistant: Assistant, thread: Thread, client: OpenAI | None = None):
    if not client:
        client = cast(OpenAI, settings.call_fn("CLIENT_INIT_FN"))

    assistant_def_cls = get_assistant_def_cls(assistant)
    if not assistant_def_cls:
        raise AIAssistantClsNotDefinedError(f"Assistant class not found: {assistant.slug}")

    fns_tools, __ = get_tools(assistant_def_cls)
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
    thread = Thread.objects.create(name=name, created_by=user, openai_id=openai_thread.id)
    return thread, openai_thread


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
