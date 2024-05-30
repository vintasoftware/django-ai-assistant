from datetime import datetime
from typing import List

from django.shortcuts import render

from ninja import NinjaAPI

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
from .schemas import (
    AssistantSchema,
    ThreadMessagesSchemaIn,
    ThreadMessagesSchemaOut,
    ThreadSchema,
    ThreadSchemaIn,
)


api = NinjaAPI(urls_namespace="django_ai_assistant")


def is_htmx_request(request):
    return request.headers.get("HX-Request") == "true"


@api.exception_handler(AIUserNotAllowedError)
def ai_user_not_allowed_handler(request, exc):
    return api.create_response(
        request,
        {"message": str(exc)},
        status=403,
    )


@api.get("assistants/", response=List[AssistantSchema], url_name="assistants_list")
def list_assistants(request):
    data = list(assistants_generator(user=request.user, request=request, view=None))
    if is_htmx_request(request):
        return render(request, "assistants/list.html", {"assistants": data})
    return data


@api.get("threads/", response=List[ThreadSchema], url_name="threads_list_create")
def list_threads(request):
    data = list(threads_generator(user=request.user, request=request, view=None))
    if is_htmx_request(request):
        return render(request, "threads/list.html", {"threads": data})
    return data


@api.post("threads/", response=ThreadSchema, url_name="threads_list_create")
def create_thread(request, payload: ThreadSchemaIn):
    name = payload.name
    thread, _ = ai_create_thread(name=name, user=request.user, request=request, view=None)
    if is_htmx_request(request):
        return render(request, "threads/item.html", {"thread": thread})
    return thread


def get_thread_message_context(thread_messages_generator):
    return [
        {
            "openai_id": message.id,
            "openai_thread_id": message.thread_id,
            "content": message.content,
            "role": message.role,
            "created_at": datetime.utcfromtimestamp(message.created_at).isoformat(),
        }
        for message in thread_messages_generator
    ]


@api.get(
    "threads/{openai_thread_id}/messages/",
    response=List[ThreadMessagesSchemaOut],
    url_name="messages_list_create",
)
def list_thread_messages(request, openai_thread_id: str):
    data = get_thread_message_context(
        thread_messages_generator(
            openai_thread_id=openai_thread_id, user=request.user, request=request, view=None
        )
    )

    if is_htmx_request(request):
        # TODO: Refactor to avoid duplicated code
        assistants = list(assistants_generator(user=request.user, request=request, view=None))
        openai_assistant_id = assistants[0].openai_id if assistants else None
        return render(
            request,
            "messages/list.html",
            {
                "openai_assistant_id": openai_assistant_id,
                "openai_thread_id": openai_thread_id,
                "messages": data,
            },
        )
    return data


# TODO: Support content streaming
@api.post(
    "threads/{openai_thread_id}/messages/",
    response=ThreadMessagesSchemaOut,
    url_name="messages_list_create",
)
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
        # TODO: Refactor to avoid duplicated code
        assistants = list(assistants_generator(user=request.user, request=request, view=None))
        openai_assistant_id = assistants[0].openai_id if assistants else None
        messages_context = get_thread_message_context(
            thread_messages_generator(
                openai_thread_id=openai_thread_id, user=request.user, request=request, view=None
            )
        )
        return render(
            request,
            "messages/list.html",
            {
                "openai_assistant_id": openai_assistant_id,
                "openai_thread_id": openai_thread_id,
                "messages": messages_context,
            },
        )

    return {
        "openai_id": message.id,
        "openai_thread_id": message.thread_id,
        "content": message.content,
        "role": message.role,
        "created_at": datetime.utcfromtimestamp(message.created_at).isoformat(),
    }
