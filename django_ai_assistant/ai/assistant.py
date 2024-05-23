from collections.abc import Callable
from typing import Any

from ..conf import settings
from ..models import Assistant
from .function_tool import FunctionTool


def create_assistant(
    name: str, instructions: str, fns: list[Callable[..., Any]], model: str = "gpt-4o"
):
    client = settings.call_fn("CLIENT_INIT_FN")
    fns_tools = [FunctionTool.from_defaults(fn=fn) for fn in fns]
    tools = [t.metadata.to_openai_tool() for t in fns_tools]
    assistant = client.beta.assistants.create(
        instructions=instructions,
        name=name,
        tools=tools,
        model=model,
    )
    Assistant.objects.create(
        name=name,
        openai_id=assistant.id,
    )
    return assistant


def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b
