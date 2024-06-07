import abc
import copy
import inspect
import types
from typing import Any, ClassVar, Sequence, cast

from django.conf import settings
from django.http import HttpRequest
from django.views import View

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import ConfigurableFieldSpec
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import BaseTool, Tool

from django_ai_assistant.ai.chat_message_histories import DjangoChatMessageHistory
from django_ai_assistant.exceptions import AIAssistantNotDefinedError, AIUserNotAllowedError
from django_ai_assistant.models import Thread
from django_ai_assistant.permissions import can_create_message, can_create_thread, can_run_assistant


class AIAssistant(abc.ABC):  # noqa: F821
    id: ClassVar[str]  # noqa: A003
    # TODO: id should match the pattern '^[a-zA-Z0-9_-]+$ to support as_tool in OpenAI
    name: str
    instructions: str
    model: str
    temperature: float

    _user: Any | None
    _request: Any | None
    _view: Any | None
    _init_kwargs: dict[str, Any]
    _method_tools: Sequence[BaseTool]

    def __init__(self, *, user=None, request=None, view=None, **kwargs):
        self._user = user
        self._request = request
        self._view = view
        self._init_kwargs = kwargs

        self.temperature = 1.0  # default OpenAI temperature for Assistant

        self._set_method_tools()

    def _set_method_tools(self):
        # Find tool methods (decorated with `@tool`):
        # NOTE: tools are defined in the class context because of the `@tool` decorator,
        # so it is shared between instances.
        methods = inspect.getmembers(self, predicate=lambda m: isinstance(m, BaseTool))
        class_tools = [tool for _, tool in methods]

        # Copy the tools, to avoid sharing self between instances:
        # TODO: find a way to avoid deepcopy, such as dynamically setting self.
        tools = copy.deepcopy(class_tools)

        # Remove self from each tool args_schema:
        for tool in tools:
            if tool.args_schema:
                if isinstance(tool.args_schema.__fields_set__, set):
                    tool.args_schema.__fields_set__.remove("self")
                tool.args_schema.__fields__.pop("self", None)

        # Bind the tool method to tool function:
        # NOTE: tools are defined in the class context because of the `@tool` decorator
        # where the methods are still unbound.
        for tool in tools:
            if hasattr(tool, "func") and tool.func:
                tool.func = types.MethodType(tool.func, self)
            if hasattr(tool, "coroutine") and tool.coroutine:
                tool.coroutine = types.MethodType(tool.coroutine, self)

        self._method_tools = tools

    def get_name(self):
        return self.name

    def get_instructions(self):
        return self.instructions

    def get_model(self):
        return self.model

    def get_temperature(self):
        return self.temperature

    def get_model_kwargs(self):
        return {}

    def get_prompt_template(self):
        instructions = self.get_instructions()
        return ChatPromptTemplate.from_messages(
            [
                ("system", instructions),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

    def get_message_history(self, thread_id: int | None):
        if thread_id is None:
            return InMemoryChatMessageHistory()
        return DjangoChatMessageHistory(thread_id)

    def get_llm(self):
        model = self.get_model()
        temperature = self.get_temperature()
        model_kwargs = self.get_model_kwargs()
        return ChatAnthropic(
            model_name=model,
            temperature=temperature,
            model_kwargs=model_kwargs,
            api_key=settings.ANTHROPIC_API_KEY,
            timeout=None,
            max_retries=2,
        )

    def get_tools(self) -> Sequence[BaseTool]:
        return self._method_tools

    def as_chain(self, thread_id: int | None):
        # Based on:
        # - https://python.langchain.com/v0.2/docs/how_to/qa_chat_history_how_to/
        # - https://python.langchain.com/v0.2/docs/how_to/migrate_agent/#memory
        # TODO: use langgraph instead?
        llm = self.get_llm()
        tools = self.get_tools()
        prompt = self.get_prompt_template()
        tools = cast(Sequence[BaseTool], tools)
        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
        agent_executor = AgentExecutor(
            agent=agent,  # type: ignore[call-arg]
            tools=tools,
        )
        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,  # type: ignore[call-arg]
            # This is needed because in most real world scenarios, a session id is needed
            # It isn't really used here because we are using a simple in memory ChatMessageHistory
            self.get_message_history,
            input_messages_key="input",
            history_messages_key="history",
            history_factory_config=[
                ConfigurableFieldSpec(
                    id="thread_id",  # must match get_message_history kwarg
                    annotation=int,
                    name="Thread ID",
                    description="Unique identifier for the chat thread / conversation / session.",
                    default=None,
                    is_shared=True,
                ),
            ],
        ).with_config({"configurable": {"thread_id": thread_id}})

        return agent_with_chat_history

    def invoke(self, *args, thread_id: int | None, **kwargs):
        chain = self.as_chain(thread_id)
        return chain.invoke(*args, **kwargs)

    def run_as_tool(self, message: str, **kwargs):
        chain = self.as_chain(thread_id=None)
        output = chain.invoke({"input": message}, **kwargs)
        return output["output"]

    def as_tool(self, description) -> BaseTool:
        return Tool.from_function(
            func=self.run_as_tool,
            name=self.id,
            description=description,
        )


ASSISTANT_CLS_REGISTRY: dict[str, type[AIAssistant]] = {}


def register_assistant(cls: type[AIAssistant]):
    ASSISTANT_CLS_REGISTRY[cls.id] = cls
    return cls


def get_assistants_info(
    user: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    return [
        {
            "id": assistant_id,
            "name": assistant_cls.name,
        }
        for assistant_id, assistant_cls in ASSISTANT_CLS_REGISTRY.items()
        if can_run_assistant(assistant_cls=assistant_cls, user=user, request=request, view=view)
    ]


def create_message(
    assistant_id: str,
    thread: Thread,
    user: Any,
    content: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    if not can_create_message(thread=thread, user=user, request=request, view=view):
        raise AIUserNotAllowedError("User is not allowed to create messages in this thread")
    if assistant_id not in ASSISTANT_CLS_REGISTRY:
        raise AIAssistantNotDefinedError(f"Assistant with id={assistant_id} not found")
    assistant_cls = ASSISTANT_CLS_REGISTRY[assistant_id]
    if not can_run_assistant(
        assistant_cls=assistant_cls,
        user=user,
        request=request,
        view=view,
    ):
        raise AIUserNotAllowedError("User is not allowed to use this assistant")

    # TODO: Check if we can separate the message creation from the chain invoke
    assistant = assistant_cls(user=user, request=request, view=view)
    assistant_message = assistant.invoke(
        {"input": content},
        thread_id=thread.id,
    )
    return assistant_message


def create_thread(
    name: str,
    user: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    if not can_create_thread(user=user, request=request, view=view):
        raise AIUserNotAllowedError("User is not allowed to create threads")

    thread = Thread.objects.create(name=name, created_by=user)
    return thread


def get_threads(
    user: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    return list(Thread.objects.filter(created_by=user))


def get_thread_messages(
    thread_id: str,
    user: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
) -> list[BaseMessage]:
    # TODO: have more permissions for threads? View thread permission?
    thread = Thread.objects.get(id=thread_id)
    if user != thread.created_by:
        raise AIUserNotAllowedError("User is not allowed to view messages in this thread")

    return DjangoChatMessageHistory(thread.id).get_messages()


def create_thread_message_as_user(
    thread_id: str,
    content: str,
    user: Any,
    request: HttpRequest | None = None,
    view: View | None = None,
):
    # TODO: have more permissions for threads? View thread permission?
    thread = Thread.objects.get(id=thread_id)
    if user != thread.created_by:
        raise AIUserNotAllowedError("User is not allowed to create messages in this thread")

    DjangoChatMessageHistory(thread.id).add_messages([HumanMessage(content=content)])
