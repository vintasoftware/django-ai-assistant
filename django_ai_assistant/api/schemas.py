from enum import Enum

from django.utils import timezone

from ninja import Field, ModelSchema, Schema

from django_ai_assistant.models import Thread


class AssistantSchema(Schema):
    id: str  # noqa: A003
    name: str


class ThreadSchema(ModelSchema):
    class Meta:
        model = Thread
        fields = (
            "id",
            "name",
            "created_at",
            "updated_at",
        )


class ThreadSchemaIn(Schema):
    name: str = Field(default_factory=lambda: timezone.now().strftime("%Y-%m-%d %H:%M"))


class ThreadMessagesSchemaIn(Schema):
    assistant_id: str
    content: str


class ThreadMessageTypeEnum(str, Enum):
    human = "human"
    ai = "ai"
    generic = "generic"
    system = "system"
    function = "function"
    tool = "tool"


class ThreadMessagesSchemaOut(Schema):
    id: str  # noqa: A003
    type: ThreadMessageTypeEnum  # noqa: A003
    content: str
