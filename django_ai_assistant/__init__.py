from importlib import metadata

from django_ai_assistant.langchain.tools import (  # noqa
    BaseModel,
    BaseTool,
    Field,
    StructuredTool,
    Tool,
    method_tool,
    tool,
)


version = __version__ = metadata.version(__package__)
package_name = __package__
