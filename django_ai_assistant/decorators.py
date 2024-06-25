import uuid
from functools import wraps


def _cast_id(item_id, model):
    if isinstance(item_id, str) and "UUID" in model._meta.pk.get_internal_type():
        return uuid.UUID(item_id)
    return item_id


# Decorator to cast ids to the correct type when using workaround UUIDAutoField
def with_cast_id(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from django_ai_assistant.models import Message, Thread

        thread_id = kwargs.get("thread_id")
        message_id = kwargs.get("message_id")
        message_ids = kwargs.get("message_ids")

        if thread_id:
            thread_id = _cast_id(thread_id, Thread)
            kwargs["thread_id"] = thread_id

        if message_id:
            message_id = _cast_id(message_id, Message)
            kwargs["message_id"] = message_id

        if message_ids:
            message_ids = [_cast_id(message_id, Message) for message_id in message_ids]
            kwargs["message_ids"] = message_ids

        return func(*args, **kwargs)

    return wrapper
