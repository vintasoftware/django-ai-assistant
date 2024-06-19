from typing import Any

from django.http import HttpRequest

from django_ai_assistant.conf import app_settings
from django_ai_assistant.models import Message, Thread


def _get_default_kwargs(user: Any, request: HttpRequest | None):
    return {
        "user": user,
        "request": request,
    }


def can_create_thread(
    user: Any,
    request: HttpRequest | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_CREATE_THREAD_FN",
        **_get_default_kwargs(user, request),
        **kwargs,
    )


def can_view_thread(
    thread: Thread,
    user: Any,
    request: HttpRequest | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_VIEW_THREAD_FN",
        **_get_default_kwargs(user, request),
        thread=thread,
        **kwargs,
    )


def can_update_thread(
    thread: Thread,
    user: Any,
    request: HttpRequest | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_UPDATE_THREAD_FN",
        **_get_default_kwargs(user, request),
        thread=thread,
        **kwargs,
    )


def can_delete_thread(
    thread: Thread,
    user: Any,
    request: HttpRequest | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_DELETE_THREAD_FN",
        **_get_default_kwargs(user, request),
        thread=thread,
        **kwargs,
    )


def can_create_message(
    thread,
    user: Any,
    request: HttpRequest | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_CREATE_MESSAGE_FN",
        **_get_default_kwargs(user, request),
        thread=thread,
        **kwargs,
    )


def can_update_message(
    message: Message,
    user: Any,
    request: HttpRequest | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_UPDATE_MESSAGE_FN",
        **_get_default_kwargs(user, request),
        message=message,
        thread=message.thread,
        **kwargs,
    )


def can_delete_message(
    message: Message,
    user: Any,
    request: HttpRequest | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_DELETE_MESSAGE_FN",
        **_get_default_kwargs(user, request),
        message=message,
        thread=message.thread,
        **kwargs,
    )


def can_run_assistant(
    assistant_cls,
    user: Any,
    request: HttpRequest | None = None,
    **kwargs,
) -> bool:
    return app_settings.call_fn(
        "CAN_RUN_ASSISTANT",
        **_get_default_kwargs(user, request),
        assistant_cls=assistant_cls,
        **kwargs,
    )


def allow_all(**kwargs) -> bool:
    return True


def owns_thread(user: Any, thread: Thread, **kwargs) -> bool:
    if user.is_superuser:
        return True

    return thread.created_by == user
