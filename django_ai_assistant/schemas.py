from typing import Any, List, Literal

from django.utils import timezone

from ninja import Field, ModelSchema, Schema

from .models import Assistant, Thread


class AssistantSchema(ModelSchema):
    class Meta:
        model = Assistant
        fields = (
            "openai_id",
            "name",
            "created_at",
            "updated_at",
        )


class ThreadSchema(ModelSchema):
    class Meta:
        model = Thread
        fields = (
            "openai_id",
            "name",
            "created_at",
            "updated_at",
        )


class ThreadSchemaIn(Schema):
    name: str = Field(default_factory=lambda: timezone.now().strftime("%Y-%m-%d %H:%M"))


class TextSchema(Schema):
    # TODO: Improve annotations type. It will be used for RAG.
    annotations: List[Any]
    value: str


class ThreadMessageContentSchema(Schema):
    text: TextSchema
    type: Literal["text"]  # noqa: A003


class ThreadMessagesSchemaOut(Schema):
    openai_id: str
    openai_thread_id: str
    content: List[ThreadMessageContentSchema]
    role: Literal["user", "assistant"]
    created_at: str


class ThreadMessagesSchemaIn(Schema):
    assistant_id: str
    content: str
