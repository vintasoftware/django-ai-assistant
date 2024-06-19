from typing import Any

from django.http import HttpRequest

from langchain_core.messages import BaseMessage, HumanMessage

from django_ai_assistant.exceptions import (
    AIAssistantNotDefinedError,
    AIUserNotAllowedError,
)
from django_ai_assistant.helpers.assistants import ASSISTANT_CLS_REGISTRY
from django_ai_assistant.langchain.chat_message_histories import DjangoChatMessageHistory
from django_ai_assistant.models import Message, Thread
from django_ai_assistant.permissions import (
    can_create_message,
    can_create_thread,
    can_delete_message,
    can_delete_thread,
    can_run_assistant,
    can_view_thread,
)


def get_assistant_cls(
    assistant_id: str,
    user: Any,
    request: HttpRequest | None = None,
):
    if assistant_id not in ASSISTANT_CLS_REGISTRY:
        raise AIAssistantNotDefinedError(f"Assistant with id={assistant_id} not found")
    assistant_cls = ASSISTANT_CLS_REGISTRY[assistant_id]
    if not can_run_assistant(
        assistant_cls=assistant_cls,
        user=user,
        request=request,
    ):
        raise AIUserNotAllowedError("User is not allowed to use this assistant")
    return assistant_cls


def get_single_assistant_info(
    assistant_id: str,
    user: Any,
    request: HttpRequest | None = None,
):
    assistant_cls = get_assistant_cls(assistant_id, user, request)

    return {
        "id": assistant_id,
        "name": assistant_cls.name,
    }


def get_assistants_info(
    user: Any,
    request: HttpRequest | None = None,
):
    return [
        get_assistant_cls(assistant_id=assistant_id, user=user, request=request)
        for assistant_id in ASSISTANT_CLS_REGISTRY.keys()
    ]


def create_message(
    assistant_id: str,
    thread: Thread,
    user: Any,
    content: Any,
    request: HttpRequest | None = None,
):
    assistant_cls = get_assistant_cls(assistant_id, user, request)

    if not can_create_message(thread=thread, user=user, request=request):
        raise AIUserNotAllowedError("User is not allowed to create messages in this thread")

    # TODO: Check if we can separate the message creation from the chain invoke
    assistant = assistant_cls(user=user, request=request)
    assistant_message = assistant.invoke(
        {"input": content},
        thread_id=thread.id,
    )
    return assistant_message


def create_thread(
    name: str,
    user: Any,
    request: HttpRequest | None = None,
):
    if not can_create_thread(user=user, request=request):
        raise AIUserNotAllowedError("User is not allowed to create threads")

    thread = Thread.objects.create(name=name, created_by=user)
    return thread


def get_single_thread(
    thread_id: str,
    user: Any,
    request: HttpRequest | None = None,
):
    thread = Thread.objects.get(id=thread_id)

    if not can_view_thread(thread=thread, user=user, request=request):
        raise AIUserNotAllowedError("User is not allowed to view this thread")

    return thread


def get_threads(
    user: Any,
    request: HttpRequest | None = None,
):
    return list(Thread.objects.filter(created_by=user))


def update_thread(
    thread: Thread,
    name: str,
    user: Any,
    request: HttpRequest | None = None,
):
    if not can_delete_thread(thread=thread, user=user, request=request):
        raise AIUserNotAllowedError("User is not allowed to update this thread")

    thread.name = name
    thread.save()
    return thread


def delete_thread(
    thread: Thread,
    user: Any,
    request: HttpRequest | None = None,
):
    if not can_delete_thread(thread=thread, user=user, request=request):
        raise AIUserNotAllowedError("User is not allowed to delete this thread")

    return thread.delete()


def get_thread_messages(
    thread_id: str,
    user: Any,
    request: HttpRequest | None = None,
) -> list[BaseMessage]:
    # TODO: have more permissions for threads? View thread permission?
    thread = Thread.objects.get(id=thread_id)
    if user != thread.created_by:
        raise AIUserNotAllowedError("User is not allowed to view messages in this thread")

    return DjangoChatMessageHistory(thread.id).get_messages()


def create_thread_message_as_user(
    thread_id: str,
    content: str,
    user: Any,
    request: HttpRequest | None = None,
):
    # TODO: have more permissions for threads? View thread permission?
    thread = Thread.objects.get(id=thread_id)
    if user != thread.created_by:
        raise AIUserNotAllowedError("User is not allowed to create messages in this thread")

    DjangoChatMessageHistory(thread.id).add_messages([HumanMessage(content=content)])


def delete_message(
    message: Message,
    user: Any,
    request: HttpRequest | None = None,
):
    if not can_delete_message(message=message, user=user, request=request):
        raise AIUserNotAllowedError("User is not allowed to delete this message")

    return DjangoChatMessageHistory(thread_id=message.thread_id).remove_messages([str(message.id)])
