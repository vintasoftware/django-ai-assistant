import json
import uuid
from typing import Any

from django.conf import settings
from django.db import models
from django.db.models import F, Index, Manager

from django_ai_assistant.exceptions import AIAssistantPrimaryKeyTypeNotInListError


def get_id_field():
    if settings.AI_ASSISTANT_PRIMARY_KEY_FIELD == "auto":
        return int
    elif settings.AI_ASSISTANT_PRIMARY_KEY_FIELD == "uuid":
        return models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    elif settings.AI_ASSISTANT_PRIMARY_KEY_FIELD == "string":
        return models.CharField(primary_key=True, max_length=255)
    else:
        raise AIAssistantPrimaryKeyTypeNotInListError


class Thread(models.Model):
    id: Any = get_id_field()  # noqa: A003
    messages: Manager["Message"]
    name = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="ai_assistant_threads",
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Thread"
        verbose_name_plural = "Threads"
        ordering = ("-created_at",)
        indexes = (Index(F("created_at").desc(), name="thread_created_at_desc"),)

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return f"<Thread {self.name}>"


class Message(models.Model):
    id: Any = get_id_field()  # noqa: A003
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    thread_id: int  # noqa: A003 NEED TO LOOK AT THIS TOMORROW
    message = models.JSONField()  # langchain BaseMessage
    created_at = models.DateTimeField(auto_now_add=True)
    # TODO: add created_by field

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ("created_at",)
        indexes = (Index(F("created_at"), name="message_created_at"),)

    def __str__(self):
        return json.dumps(self.message)

    def __repr__(self) -> str:
        return f"<Message {self.id} at {self.thread_id}>"
