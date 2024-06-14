from typing import Any

from django.http import HttpRequest
from django.views import View

from django_ai_assistant.conf import app_settings
from django_ai_assistant.models import Message, Thread


def _get_default_kwargs(user: Any, request: HttpRequest | None, view: View | None):
    if view and not request:
        request = view.request
    return {
        "user": user,
        "request": request,
        "view": view if view else None,
    }


def can_create_thread(
    user: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_CREATE_THREAD_FN",
        **_get_default_kwargs(user, request, view),
    )


def can_delete_thread(
    thread: Thread,
    user: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_DELETE_THREAD_FN",
        **_get_default_kwargs(user, request, view),
        thread=thread,
    )


def can_create_message(
    thread,
    user: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_CREATE_MESSAGE_FN",
        **_get_default_kwargs(user, request, view),
        thread=thread,
    )


def can_delete_message(
    message: Message,
    user: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_DELETE_MESSAGE_FN",
        **_get_default_kwargs(user, request, view),
        message=message,
        thread=message.thread,
    )


def can_run_assistant(
    assistant_cls,
    user: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_RUN_ASSISTANT",
        **_get_default_kwargs(user, request, view),
        assistant_cls=assistant_cls,
    )


def allow_all(**kwargs) -> bool:
    return True


def owns_thread(user: Any, thread: Thread, **kwargs) -> bool:
    if user.is_superuser:
        return True

    return thread.created_by == user
