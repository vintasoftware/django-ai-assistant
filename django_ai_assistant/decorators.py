from functools import wraps

from django_ai_assistant.helpers.formatters import cast_id


def with_cast_id(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from django_ai_assistant.models import Message, Thread

        thread_id = kwargs.get("thread_id")
        message_id = kwargs.get("message_id")
        message_ids = kwargs.get("message_ids")

        if thread_id:
            thread_id = cast_id(thread_id, Thread)
            kwargs["thread_id"] = thread_id

        if message_id:
            message_id = cast_id(message_id, Message)
            kwargs["message_id"] = message_id

        if message_ids:
            message_ids = [cast_id(message_id, Message) for message_id in message_ids]
            kwargs["message_ids"] = message_ids

        return func(*args, **kwargs)

    return wrapper
