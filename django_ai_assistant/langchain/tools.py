from langchain_core.tools import (  # noqa
    BaseTool,
    StructuredTool,
    Tool,
    tool,
)
from pydantic.v1 import BaseModel, Field  # noqa


def method_tool(*args, **kwargs):
    # If there's one arg and no kwargs, the decorator is being using like `@method_tool`
    # instead of `@method_tool(...)`
    if len(args) == 1 and len(kwargs) == 0:
        decorated_method = args[0]
        decorated_method._is_tool = True
        return decorated_method

    def decorator(decorated_method):
        decorated_method._is_tool = True
        decorated_method._tool_maker_args = args
        decorated_method._tool_maker_kwargs = kwargs
        return decorated_method

    return decorator
