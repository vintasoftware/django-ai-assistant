import json
from typing import Any

from django.conf import settings
from django.db import models
from django.db.models import F, Index, Manager


class Thread(models.Model):
    """Thread model. A thread is a collection of messages between a user and the AI assistant.
    Also called conversation or session."""

    messages: Manager["Message"]
    name = models.CharField(max_length=255, blank=True)
    """Name of the thread. Can be blank."""
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="ai_assistant_threads",
        null=True,
    )
    """User who created the thread. Can be null. Set to null/None when user is deleted."""
    created_at = models.DateTimeField(auto_now_add=True)
    """Date and time when the thread was created.
    Automatically set when the thread is created."""
    updated_at = models.DateTimeField(auto_now=True)
    """Date and time when the thread was last updated.
    Automatically set when the thread is updated."""

    class Meta:
        verbose_name = "Thread"
        verbose_name_plural = "Threads"
        ordering = ("-created_at",)
        indexes = (Index(F("created_at").desc(), name="thread_created_at_desc"),)

    def __str__(self) -> str:
        """Return the name of the thread as the string representation of the thread."""
        return self.name

    def __repr__(self) -> str:
        """Return the string representation of the thread like '<Thread name>'"""
        return f"<Thread {self.name}>"


class Message(models.Model):
    """Message model. A message is a text that is part of a thread.
    A message can be sent by a user or the AI assistant.\n
    The message data is stored as a JSON field called `message`."""

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    """Thread to which the message belongs."""
    thread_id: Any  # noqa: A003
    message = models.JSONField()
    """Message content. This is a serialized Langchain `BaseMessage` that was serialized
    with `message_to_dict` and can be deserialized with `messages_from_dict`."""
    created_at = models.DateTimeField(auto_now_add=True)
    """Date and time when the message was created.
    Automatically set when the message is created."""
    # TODO: add created_by field

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ("created_at",)
        indexes = (Index(F("created_at"), name="message_created_at"),)

    def __str__(self) -> str:
        """Return internal message data from `message` attribute
        as the string representation of the message."""
        return json.dumps(self.message)

    def __repr__(self) -> str:
        """Return the string representation of the message like '<Message id at thread_id>'"""
        return f"<Message {self.id} at {self.thread_id}>"
