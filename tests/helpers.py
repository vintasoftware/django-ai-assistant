from django.contrib.auth.models import User

from django_ai_assistant.models import Message, Thread


def create_thread(
    name: str | None = None, user: User | None = None, message: str | None = None
) -> Thread:
    name = name or "Test Thread"
    user = user or User.objects.create_user(username="test_user")
    message = message or "Test Message"

    thread = Thread.objects.create(name=name, created_by=user)

    Message.objects.create(message={"content": message}, thread=thread)

    thread.refresh_from_db()

    return thread
