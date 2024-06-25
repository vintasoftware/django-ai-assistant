from importlib import metadata

from django_ai_assistant.helpers.assistants import (  # noqa
    AIAssistant,
)
from django_ai_assistant.langchain.tools import (  # noqa
    BaseModel,
    BaseTool,
    Field,
    StructuredTool,
    Tool,
    method_tool,
    tool,
)


PACKAGE_NAME = __package__ or "django-ai-assistant"
VERSION = __version__ = metadata.version(PACKAGE_NAME)
