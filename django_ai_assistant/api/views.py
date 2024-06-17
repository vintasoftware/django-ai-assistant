from typing import List

from django.shortcuts import get_object_or_404

from langchain_core.messages import message_to_dict
from ninja import NinjaAPI
from ninja.operation import Operation

from django_ai_assistant import package_name, version
from django_ai_assistant.api.schemas import (
    AssistantSchema,
    ThreadMessagesSchemaIn,
    ThreadMessagesSchemaOut,
    ThreadSchema,
    ThreadSchemaIn,
)
from django_ai_assistant.exceptions import AIUserNotAllowedError
from django_ai_assistant.helpers import assistants
from django_ai_assistant.helpers.assistants import (
    create_message,
    get_assistants_info,
    get_single_assistant_info,
    get_single_thread,
    get_thread_messages,
    get_threads,
)
from django_ai_assistant.models import Message, Thread


class API(NinjaAPI):
    # Force "operationId" to be like "django_ai_assistant_delete_thread"
    def get_openapi_operation_id(self, operation: Operation) -> str:
        name = operation.view_func.__name__
        return (package_name + "_" + name).replace(".", "_")


api = API(title=package_name, version=version, urls_namespace="django_ai_assistant")


@api.exception_handler(AIUserNotAllowedError)
def ai_user_not_allowed_handler(request, exc):
    return api.create_response(
        request,
        {"message": str(exc)},
        status=403,
    )


@api.get("assistants/", response=List[AssistantSchema], url_name="assistants_list")
def list_assistants(request):
    return list(get_assistants_info(user=request.user, request=request))


@api.get("assistants/{assistant_id}/", response=AssistantSchema, url_name="assistant_detail")
def get_assistant(request, assistant_id: str):
    return get_single_assistant_info(assistant_id=assistant_id, user=request.user, request=request)


@api.get("threads/", response=List[ThreadSchema], url_name="threads_list_create")
def list_threads(request):
    return list(get_threads(user=request.user, request=request))


@api.post("threads/", response=ThreadSchema, url_name="threads_list_create")
def create_thread(request, payload: ThreadSchemaIn):
    name = payload.name
    return assistants.create_thread(name=name, user=request.user, request=request)


@api.get("threads/{thread_id}/", response=ThreadSchema, url_name="thread_detail_update_delete")
def get_thread(request, thread_id: str):
    thread = get_single_thread(thread_id=thread_id, user=request.user, request=request)
    return thread


@api.patch("threads/{thread_id}/", response=ThreadSchema, url_name="thread_detail_update_delete")
def update_thread(request, thread_id: str, payload: ThreadSchemaIn):
    thread = get_object_or_404(Thread, id=thread_id)
    name = payload.name
    return assistants.update_thread(thread=thread, name=name, user=request.user, request=request)


@api.delete("threads/{thread_id}/", response={204: None}, url_name="thread_detail_update_delete")
def delete_thread(request, thread_id: str):
    thread = get_object_or_404(Thread, id=thread_id)
    assistants.delete_thread(thread=thread, user=request.user, request=request)
    return 204, None


@api.get(
    "threads/{thread_id}/messages/",
    response=List[ThreadMessagesSchemaOut],
    url_name="messages_list_create",
)
def list_thread_messages(request, thread_id: str):
    messages = get_thread_messages(thread_id=thread_id, user=request.user, request=request)
    return [message_to_dict(m)["data"] for m in messages]


# TODO: Support content streaming
@api.post(
    "threads/{thread_id}/messages/",
    response={201: None},
    url_name="messages_list_create",
)
def create_thread_message(request, thread_id: str, payload: ThreadMessagesSchemaIn):
    thread = Thread.objects.get(id=thread_id)

    create_message(
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
def delete_thread_message(request, thread_id: str, message_id: str):
    message = get_object_or_404(Message, id=message_id, thread_id=thread_id)
    assistants.delete_message(
        message=message,
        user=request.user,
        request=request,
    )
    return 204, None
