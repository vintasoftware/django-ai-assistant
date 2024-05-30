from django.conf import settings
from django.db import models
from django.db.models import F, Index


class Assistant(models.Model):
    id: int  # noqa: A003
    slug = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True)
    openai_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cls_synced_at = models.DateTimeField(null=True, blank=True)
    openai_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Assistant"
        verbose_name_plural = "Assistants"
        ordering = ("-created_at",)
        indexes = (Index(F("created_at").desc(), name="assistant_created_at_desc"),)

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return f"<Assistant {self.name}>"


class Thread(models.Model):
    id: int  # noqa: A003
    name = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="ai_assistant_threads",
        null=True,
    )
    openai_id = models.CharField(max_length=255, unique=True)
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
    id: int  # noqa: A003
    thread_id = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    message = models.JSONField()  # langchain BaseMessage
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ("-created_at",)
        indexes = (Index(F("created_at").desc(), name="message_created_at_desc"),)

    def __str__(self):
        return self.message

    def __repr__(self) -> str:
        return f"<Message {self.id} at {self.thread_id}>"
