from typing import List

from django.shortcuts import render

from langchain_core.messages import message_to_dict
from ninja import NinjaAPI

from .exceptions import AIUserNotAllowedError
from .helpers.assistants import (
    create_thread as ai_create_thread,
)
from .helpers.assistants import (
    get_assistants_info,
    get_thread_messages,
    get_threads,
    run_assistant_as_user,
)
from .models import Thread
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
    data = list(get_assistants_info(user=request.user, request=request, view=None))
    if is_htmx_request(request):
        return render(request, "assistants/list.html", {"assistants": data})
    return data


@api.get("threads/", response=List[ThreadSchema], url_name="threads_list_create")
def list_threads(request):
    data = list(get_threads(user=request.user, request=request, view=None))
    if is_htmx_request(request):
        return render(request, "threads/list.html", {"threads": data})
    return data


@api.post("threads/", response=ThreadSchema, url_name="threads_list_create")
def create_thread(request, payload: ThreadSchemaIn):
    name = payload.name
    thread = ai_create_thread(name=name, user=request.user, request=request, view=None)
    if is_htmx_request(request):
        return render(request, "threads/item.html", {"thread": thread})
    return thread


@api.get(
    "threads/{thread_id}/messages/",
    response=List[ThreadMessagesSchemaOut],
    url_name="messages_list_create",
)
def list_thread_messages(request, thread_id: str):
    messages = get_thread_messages(
        thread_id=thread_id, user=request.user, request=request, view=None
    )
    if is_htmx_request(request):
        return render(request, "messages/list.html", {"messages": data})
    return [message_to_dict(m)["data"] for m in messages]


# TODO: Support content streaming
@api.post(
    "threads/{thread_id}/messages/",
    response={201: None},
    url_name="messages_list_create",
)
def create_thread_message(request, thread_id: str, payload: ThreadMessagesSchemaIn):
    thread = Thread.objects.get(id=thread_id)

    run_assistant_as_user(
        assistant_id=payload.assistant_id,
        thread=thread,
        user=request.user,
        content=payload.content,
        request=request,
        view=None,
    )
    if is_htmx_request(request):
        return render(request, "messages/item.html", {"message": message})

    return 201, None
