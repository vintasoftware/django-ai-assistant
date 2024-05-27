import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from inspect import signature
from typing import Any

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo


AsyncCallable = Callable[..., Awaitable[Any]]


def sync_to_async(fn: Callable[..., Any]) -> AsyncCallable:
    """Sync to async."""

    async def _async_wrapped_fn(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))

    return _async_wrapped_fn


def create_schema_from_function(
    name: str,
    func: Callable[..., Any],
    additional_fields: list[tuple[str, type, Any] | tuple[str, type]] | None = None,
) -> type[BaseModel]:
    """Create schema from function."""
    fields = {}
    params = signature(func).parameters
    for param_name in params:
        param_type = params[param_name].annotation
        param_default = params[param_name].default

        if param_type is params[param_name].empty:
            param_type = Any

        if param_default is params[param_name].empty:
            # Required field
            fields[param_name] = (param_type, FieldInfo())
        elif isinstance(param_default, FieldInfo):
            # Field with pydantic.Field as default value
            fields[param_name] = (param_type, param_default)
        else:
            fields[param_name] = (param_type, FieldInfo(default=param_default))

    additional_fields = additional_fields or []
    for field_info in additional_fields:
        if len(field_info) == 3:
            field_name, field_type, field_default = field_info
            fields[field_name] = (field_type, FieldInfo(default=field_default))
        elif len(field_info) == 2:
            # Required field has no default value
            field_name, field_type = field_info
            fields[field_name] = (field_type, FieldInfo())
        else:
            raise ValueError(
                f"Invalid additional field info: {field_info}. " "Must be a tuple of length 2 or 3."
            )

    return create_model(name, **fields)


class DefaultToolFnSchema(BaseModel):
    """Default tool function Schema."""

    input: str  # noqa: A003


@dataclass
class ToolMetadata:
    description: str
    name: str | None = None
    fn_schema: type[BaseModel] | None = DefaultToolFnSchema
    return_direct: bool = False

    def get_parameters_dict(self) -> dict:
        if self.fn_schema is None:
            parameters = {
                "type": "object",
                "properties": {
                    "input": {"title": "input query string", "type": "string"},
                },
                "required": ["input"],
            }
        else:
            parameters = self.fn_schema.model_json_schema()
            parameters = {
                k: v
                for k, v in parameters.items()
                if k in ["type", "properties", "required", "definitions"]
            }
        return parameters

    @property
    def fn_schema_str(self) -> str:
        """Get fn schema as string."""
        if self.fn_schema is None:
            raise ValueError("fn_schema is None.")
        parameters = self.get_parameters_dict()
        return json.dumps(parameters)

    def get_name(self) -> str:
        """Get name."""
        if self.name is None:
            raise ValueError("name is None.")
        return self.name

    def to_openai_tool(self) -> dict[str, Any]:
        """To OpenAI tool."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_dict(),
            },
        }


class ToolOutput(BaseModel):
    """Tool output."""

    content: str
    tool_name: str
    raw_input: dict[str, Any]
    raw_output: Any
    is_error: bool = False

    def __str__(self) -> str:
        """String."""
        return str(self.content)


class FunctionTool:
    """Function Tool.

    A tool that takes in a function.

    """

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        fn: Callable[..., Any],
        metadata: ToolMetadata,
        async_fn: AsyncCallable | None = None,
    ) -> None:
        self._fn = fn
        if async_fn is not None:
            self._async_fn = async_fn
        else:
            self._async_fn = sync_to_async(self._fn)
        self._metadata = metadata

    @classmethod
    def from_defaults(
        cls,
        fn: Callable[..., Any],
        name: str | None = None,
        description: str | None = None,
        return_direct: bool = False,
        fn_schema: type[BaseModel] | None = None,
        async_fn: AsyncCallable | None = None,
        tool_metadata: ToolMetadata | None = None,
    ) -> "FunctionTool":
        if tool_metadata is None:
            name = name or fn.__name__
            docstring = fn.__doc__
            description = description or f"{name}{signature(fn)}\n{docstring}"
            if fn_schema is None:
                fn_schema = create_schema_from_function(f"{name}", fn, additional_fields=None)
            tool_metadata = ToolMetadata(
                name=name,
                description=description,
                fn_schema=fn_schema,
                return_direct=return_direct,
            )
        return cls(fn=fn, metadata=tool_metadata, async_fn=async_fn)

    @property
    def metadata(self) -> ToolMetadata:
        """Metadata."""
        return self._metadata

    @property
    def fn(self) -> Callable[..., Any]:
        """Function."""
        return self._fn

    @property
    def async_fn(self) -> AsyncCallable:
        """Async function."""
        return self._async_fn

    def __call__(self, *args: Any, **kwargs: Any) -> ToolOutput:
        return self.call(*args, **kwargs)

    def call(self, *args: Any, **kwargs: Any) -> ToolOutput:
        """Call."""
        tool_output = self._fn(*args, **kwargs)
        return ToolOutput(
            content=str(tool_output),
            tool_name=self.metadata.name,  # pyright: ignore[reportArgumentType]
            raw_input={"args": args, "kwargs": kwargs},
            raw_output=tool_output,
        )

    async def acall(self, *args: Any, **kwargs: Any) -> ToolOutput:
        """Call."""
        tool_output = await self._async_fn(*args, **kwargs)
        return ToolOutput(
            content=str(tool_output),
            tool_name=self.metadata.name,  # pyright: ignore[reportArgumentType]
            raw_input={"args": args, "kwargs": kwargs},
            raw_output=tool_output,
        )


def call_tool(tool: FunctionTool, arguments: dict) -> ToolOutput:
    """Call a tool with arguments."""
    try:
        if len(tool.metadata.get_parameters_dict()["properties"]) == 1 and len(arguments) == 1:
            try:
                single_arg = arguments[next(iter(arguments))]
                return tool(single_arg)
            except Exception:
                # some tools will REQUIRE kwargs, so try it
                return tool(**arguments)
        else:
            return tool(**arguments)
    except Exception as e:
        return ToolOutput(
            content="Encountered error: " + str(e),
            tool_name=tool.metadata.name,  # pyright: ignore[reportArgumentType]
            raw_input=arguments,
            raw_output=str(e),
            is_error=True,
        )
