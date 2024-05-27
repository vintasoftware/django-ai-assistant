import json
import logging
from typing import override

from openai import AssistantEventHandler, OpenAI
from openai.types.beta.assistant_stream_event import ThreadRunRequiresAction
from openai.types.beta.threads.run import Run

from .function_tool import FunctionTool, call_tool


logger = logging.getLogger(__name__)


class EventHandler(AssistantEventHandler):
    tools_by_name: dict[str, FunctionTool]

    def __init__(self, client: OpenAI, tools: list[FunctionTool]) -> None:
        self.client = client
        self.tools_by_name = {tool.metadata.name: tool for tool in tools}  # pyright: ignore[reportAttributeAccessIssue]
        super().__init__()

    @override
    def on_event(self, event: ThreadRunRequiresAction):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == "thread.run.requires_action":
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, run: Run, run_id: str):
        output_str_list = []

        for tool_call in run.required_action.submit_tool_outputs.tool_calls:  # type: ignore[reportOptionalMemberAccess]
            if tool_call.type != "function":
                # TODO: raise custom exception
                raise Exception(f"Unexpected tool_call.type={tool_call.type}")
            tool = self.tools_by_name[tool_call.function.name]
            try:
                # TODO: check how properly handle empty arguments:
                #       search for .function.arguments in llamaindex
                if tool_call.function.arguments == "":
                    tool_kwargs = {}
                else:
                    tool_kwargs = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                raise Exception(
                    f"Failed to parse tool arguments: {tool_call.function.arguments}"
                ) from e

            # TODO: Check if the EventHandler is eating exceptions:
            logger.info(
                "Calling tool '%(tool_name)s' with arguments: %(tool_kwargs)s",
                {
                    "tool_name": tool.metadata.name,
                    "tool_kwargs": tool_kwargs,
                },
            )
            output = call_tool(tool, tool_kwargs)
            logger.debug(
                "Tool output of '%(tool_name)s' with arguments: %(tool_kwargs)s : %(output)s",
                {
                    "tool_name": tool.metadata.name,
                    "tool_kwargs": tool_kwargs,
                    "output": output,
                },
            )
            output_str_list.append({"tool_call_id": tool_call.id, "output": str(output)})

        # Submit all tool_outputs at the same time
        self.submit_tool_outputs(output_str_list, run)

    def submit_tool_outputs(self, tool_outputs, run):
        # Use the submit_tool_outputs_stream helper
        with self.client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=run.thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(client=self.client, tools=list(self.tools_by_name.values())),
        ) as stream:
            # TODO: handle streaming
            for _text in stream.text_deltas:
                pass
