from functools import wraps

from django_ai_assistant.helpers.formatters import cast_id
from django_ai_assistant.models import Message, Thread


def with_cast_id(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread_id = kwargs.get("thread_id")
        message_id = kwargs.get("message_id")

        if thread_id:
            thread_id = cast_id(thread_id, Thread)
            kwargs["thread_id"] = thread_id

        if message_id:
            message_id = cast_id(message_id, Message)
            kwargs["message_id"] = message_id

        return func(*args, **kwargs)

    return wrapper
