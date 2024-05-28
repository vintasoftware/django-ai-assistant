from datetime import datetime
from typing import Any, List, Literal

from django.shortcuts import render
from django.utils import timezone

from ninja import Field, ModelSchema, NinjaAPI, Schema

from .exceptions import AIUserNotAllowedError
from .helpers.assistants import (
    assistants_generator,
    create_thread_message_as_user,
    run_assistant_as_user,
    thread_messages_generator,
    threads_generator,
)
from .helpers.assistants import (
    create_thread as ai_create_thread,
)
from .models import Assistant, Thread


api = NinjaAPI()


def is_htmx_request(request):
    return request.headers.get("HX-Request") == "true"


@api.exception_handler(AIUserNotAllowedError)
def ai_user_not_allowed_handler(request, exc):
    return api.create_response(
        request,
        {"message": str(exc)},
        status=403,
    )


class AssistantSchema(ModelSchema):
    class Meta:
        model = Assistant
        fields = (
            "openai_id",
            "name",
            "created_at",
            "updated_at",
        )


@api.get("assistants/", response=List[AssistantSchema])
def list_assistants(request):
    data = list(assistants_generator(user=request.user, request=request, view=None))
    if is_htmx_request(request):
        return render(request, "assistants/list.html", {"assistants": data})
    return data


class ThreadSchema(ModelSchema):
    class Meta:
        model = Thread
        fields = (
            "openai_id",
            "name",
            "created_at",
            "updated_at",
        )


class ThreadSchemaIn(Schema):
    name: str = Field(default_factory=lambda: timezone.now().strftime("%Y-%m-%d %H:%M"))


@api.get("threads/", response=List[ThreadSchema])
def list_threads(request):
    data = list(threads_generator(user=request.user, request=request, view=None))
    if is_htmx_request(request):
        return render(request, "threads/list.html", {"threads": data})
    return data


@api.post("threads/", response=ThreadSchema)
def create_thread(request, payload: ThreadSchemaIn):
    name = payload.name
    thread, _ = ai_create_thread(name=name, user=request.user, request=request, view=None)
    if is_htmx_request(request):
        threads = list(threads_generator(user=request.user, request=request, view=None))
        return render(request, "threads/list.html", {"threads": threads})
    return thread


class TextSchema(Schema):
    # TODO: Improve annotations type. It will be used for RAG.
    annotations: List[Any]
    value: str


class ThreadMessageContentSchema(Schema):
    text: TextSchema
    type: Literal["text"]  # noqa: A003


class ThreadMessagesSchemaOut(Schema):
    openai_id: str
    openai_thread_id: str
    content: List[ThreadMessageContentSchema]
    role: Literal["user", "assistant"]
    created_at: str


class ThreadMessagesSchemaIn(Schema):
    assistant_id: str
    content: str


@api.get("threads/{openai_thread_id}/messages/", response=List[ThreadMessagesSchemaOut])
def list_thread_messages(request, openai_thread_id: str):
    data = [
        {
            "openai_id": message.id,
            "openai_thread_id": message.thread_id,
            "content": message.content,
            "role": message.role,
            "created_at": datetime.utcfromtimestamp(message.created_at).isoformat(),
        }
        for message in thread_messages_generator(
            openai_thread_id=openai_thread_id, user=request.user, request=request, view=None
        )
    ]
    if is_htmx_request(request):
        return render(request, "messages/list.html", {"messages": data})
    return data


@api.post("threads/{openai_thread_id}/messages/", response=ThreadMessagesSchemaOut)
def create_thread_message(request, openai_thread_id: str, payload: ThreadMessagesSchemaIn):
    assistant = Assistant.objects.get(openai_id=payload.assistant_id)
    thread = Thread.objects.get(openai_id=openai_thread_id)

    message = create_thread_message_as_user(
        openai_thread_id=openai_thread_id,
        content=payload.content,
        user=request.user,
        request=request,
        view=None,
    )
    run_assistant_as_user(
        assistant=assistant,
        thread=thread,
        user=request.user,
        request=request,
        view=None,
    )
    if is_htmx_request(request):
        messages = list(
            thread_messages_generator(
                openai_thread_id=openai_thread_id, user=request.user, request=request, view=None
            )
        )
        return render(request, "messages/list.html", {"messages": messages})

    return {
        "openai_id": message.id,
        "openai_thread_id": message.thread_id,
        "content": message.content,
        "role": message.role,
        "created_at": datetime.utcfromtimestamp(message.created_at).isoformat(),
    }
