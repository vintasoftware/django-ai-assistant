import functools

from langchain_core.tools import (  # noqa
    BaseTool,
    StructuredTool,
    Tool,
    tool,
)
from pydantic.v1 import BaseModel, Field  # noqa


def wrapped_partial(func, *args, **kwargs):
    partial_func = functools.partial(func, *args, **kwargs)
    functools.update_wrapper(partial_func, func)
    return partial_func
