import json
from typing import Any, Sequence, cast

from django.conf import settings
from django.db import models
from django.db.models import F, Index, Manager

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    messages_from_dict,
)


class Thread(models.Model):
    """Thread model. A thread is a collection of messages between a user and the AI assistant.
    Also called conversation or session."""

    id: Any  # noqa: A003
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
    assistant_id = models.CharField(max_length=255, blank=True)
    """Associated assistant ID. Can be empty."""
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

    def get_messages(self, include_extra_messages: bool = False) -> list[BaseMessage]:
        """
        Get LangChain messages objects from the thread.

        Args:
            include_extra_messages (bool): Whether to include non-chat messages (like tool calls).

        Returns:
            list[BaseMessage]: List of messages
        """

        messages = messages_from_dict(
            cast(
                Sequence[dict[str, BaseMessage]],
                Message.objects.filter(thread=self)
                .order_by("created_at")
                .values_list("message", flat=True),
            )
        )
        if not include_extra_messages:
            messages = [
                m
                for m in messages
                if isinstance(m, HumanMessage | ChatMessage)
                or (isinstance(m, AIMessage) and not m.tool_calls)
            ]
        return cast(list[BaseMessage], messages)


class Message(models.Model):
    """Message model. A message is a text that is part of a thread.
    A message can be sent by a user or the AI assistant.\n
    The message data is stored as a JSON field called `message`."""

    id: Any  # noqa: A003
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    """Thread to which the message belongs."""
    thread_id: Any
    message = models.JSONField()
    """Message content. This is a serialized LangChain `BaseMessage` that was serialized
    with `message_to_dict` and can be deserialized with `messages_from_dict`."""
    created_at = models.DateTimeField(auto_now_add=True)
    """Date and time when the message was created.
    Automatically set when the message is created."""

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
