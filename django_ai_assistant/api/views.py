from typing import Any, List

from django.http import Http404
from django.shortcuts import get_object_or_404

from langchain_core.messages import message_to_dict
from ninja import NinjaAPI
from ninja.operation import Operation
from ninja.security import django_auth

from django_ai_assistant import PACKAGE_NAME, VERSION
from django_ai_assistant.api.schemas import (
    Assistant,
    Thread,
    ThreadIn,
    ThreadMessage,
    ThreadMessageIn,
)
from django_ai_assistant.conf import app_settings
from django_ai_assistant.decorators import with_cast_id
from django_ai_assistant.exceptions import AIAssistantNotDefinedError, AIUserNotAllowedError
from django_ai_assistant.helpers import use_cases
from django_ai_assistant.models import Message as MessageModel
from django_ai_assistant.models import Thread as ThreadModel


class API(NinjaAPI):
    # Force "operationId" to be like "ai_delete_thread"
    def get_openapi_operation_id(self, operation: Operation) -> str:
        name = operation.view_func.__name__
        return ("ai_" + name).replace(".", "_")


def init_api():
    return API(
        title=PACKAGE_NAME,
        version=VERSION,
        urls_namespace="django_ai_assistant",
        # Add auth to all endpoints
        auth=django_auth,
        csrf=True,
    )


api = app_settings.call_fn("INIT_API_FN")


@api.exception_handler(AIUserNotAllowedError)
def ai_user_not_allowed_handler(request, exc):
    return api.create_response(
        request,
        {"message": str(exc)},
        status=403,
    )


@api.exception_handler(AIAssistantNotDefinedError)
def ai_assistant_not_defined_handler(request, exc):
    return api.create_response(
        request,
        {"message": str(exc)},
        status=404,
    )


@api.get("assistants/", response=List[Assistant], url_name="assistants_list")
def list_assistants(request):
    return list(use_cases.get_assistants_info(user=request.user, request=request))


@api.get("assistants/{assistant_id}/", response=Assistant, url_name="assistant_detail")
def get_assistant(request, assistant_id: str):
    return use_cases.get_single_assistant_info(
        assistant_id=assistant_id, user=request.user, request=request
    )


@api.get("threads/", response=List[Thread], url_name="threads_list_create")
def list_threads(request, assistant_id: str | None = None):
    return list(use_cases.get_threads(user=request.user, assistant_id=assistant_id))


@api.post("threads/", response=Thread, url_name="threads_list_create")
def create_thread(request, payload: ThreadIn):
    name = payload.name
    assistant_id = payload.assistant_id
    return use_cases.create_thread(
        name=name, assistant_id=assistant_id, user=request.user, request=request
    )


@api.get("threads/{thread_id}/", response=Thread, url_name="thread_detail_update_delete")
@with_cast_id
def get_thread(request, thread_id: Any):
    try:
        thread = use_cases.get_single_thread(
            thread_id=thread_id, user=request.user, request=request
        )
    except ThreadModel.DoesNotExist:
        raise Http404(f"No Thread with id={thread_id} found") from None
    return thread


@api.patch("threads/{thread_id}/", response=Thread, url_name="thread_detail_update_delete")
@with_cast_id
def update_thread(request, thread_id: Any, payload: ThreadIn):
    thread = get_object_or_404(ThreadModel, id=thread_id)
    name = payload.name
    return use_cases.update_thread(thread=thread, name=name, user=request.user, request=request)


@api.delete("threads/{thread_id}/", response={204: None}, url_name="thread_detail_update_delete")
@with_cast_id
def delete_thread(request, thread_id: Any):
    thread = get_object_or_404(ThreadModel, id=thread_id)
    use_cases.delete_thread(thread=thread, user=request.user, request=request)
    return 204, None


@api.get(
    "threads/{thread_id}/messages/",
    response=List[ThreadMessage],
    url_name="messages_list_create",
)
@with_cast_id
def list_thread_messages(request, thread_id: Any):
    thread = get_object_or_404(ThreadModel, id=thread_id)
    messages = use_cases.get_thread_messages(thread=thread, user=request.user, request=request)
    return [message_to_dict(m)["data"] for m in messages]


# TODO: Support content streaming
@api.post(
    "threads/{thread_id}/messages/",
    response={201: None},
    url_name="messages_list_create",
)
@with_cast_id
def create_thread_message(request, thread_id: Any, payload: ThreadMessageIn):
    thread = ThreadModel.objects.get(id=thread_id)

    use_cases.create_message(
        assistant_id=payload.assistant_id,
        thread=thread,
        user=request.user,
        content=payload.content,
        request=request,
    )
    return 201, None


@api.delete(
    "threads/{thread_id}/messages/{message_id}/", response={204: None}, url_name="messages_delete"
)
@with_cast_id
def delete_thread_message(request, thread_id: Any, message_id: Any):
    message = get_object_or_404(MessageModel, id=message_id, thread_id=thread_id)
    use_cases.delete_message(
        message=message,
        user=request.user,
        request=request,
    )
    return 204, None
