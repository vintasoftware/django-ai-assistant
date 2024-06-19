import abc
import inspect
import re
from typing import Any, ClassVar, Sequence, cast

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.tools import (
    format_to_tool_messages,
)
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
from langchain.chains.combine_documents.base import (
    DEFAULT_DOCUMENT_PROMPT,
    DEFAULT_DOCUMENT_SEPARATOR,
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    format_document,
)
from langchain_core.retrievers import (
    BaseRetriever,
    RetrieverOutput,
)
from langchain_core.runnables import (
    ConfigurableFieldSpec,
    Runnable,
    RunnableBranch,
    RunnablePassthrough,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from django_ai_assistant.exceptions import (
    AIAssistantMisconfiguredError,
)
from django_ai_assistant.langchain.tools import Tool
from django_ai_assistant.langchain.tools import tool as tool_decorator


class AIAssistant(abc.ABC):  # noqa: F821
    id: ClassVar[str]  # noqa: A003
    name: str
    instructions: str
    model: str
    temperature: float
    has_rag: bool = False

    _user: Any | None
    _request: Any | None
    _view: Any | None
    _init_kwargs: dict[str, Any]
    _method_tools: Sequence[BaseTool]

    def __init__(self, *, user=None, request=None, view=None, **kwargs):
        if not hasattr(self, "id"):
            raise AIAssistantMisconfiguredError(
                f"Assistant id is not defined at {self.__class__.__name__}"
            )
        if self.id is None:
            raise AIAssistantMisconfiguredError(
                f"Assistant id is None at {self.__class__.__name__}"
            )
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.id):
            # id should match the pattern '^[a-zA-Z0-9_-]+$ to support as_tool in OpenAI
            raise AIAssistantMisconfiguredError(
                f"Assistant id '{self.id}' does not match the pattern '^[a-zA-Z0-9_-]+$'"
                f"at {self.__class__.__name__}"
            )

        self._user = user
        self._request = request
        self._view = view
        self._init_kwargs = kwargs

        self.temperature = 1.0  # default OpenAI temperature for Assistant

        self._set_method_tools()

    def _set_method_tools(self):
        # Find tool methods (decorated with `@method_tool` from django_ai_assistant/tools.py):
        members = inspect.getmembers(
            self,
            predicate=lambda m: inspect.ismethod(m) and getattr(m, "_is_tool", False),
        )
        tool_methods = [m for _, m in members]

        # Sort tool methods by the order they appear in the source code,
        # since this can be meaningful:
        tool_methods.sort(key=lambda m: inspect.getsourcelines(m)[1])

        # Transform tool methods into tool objects:
        tools = []
        for method in tool_methods:
            if hasattr(method, "_tool_maker_args"):
                tool = tool_decorator(
                    *method._tool_maker_args,
                    **method._tool_maker_kwargs,
                )(method)
            else:
                tool = tool_decorator(method)
            tools.append(cast(BaseTool, tool))

        # Remove self from each tool args_schema:
        for tool in tools:
            if tool.args_schema:
                if isinstance(tool.args_schema.__fields_set__, set):
                    tool.args_schema.__fields_set__.remove("self")
                tool.args_schema.__fields__.pop("self", None)

        self._method_tools = tools

    @classmethod
    def _get_assistant_cls_registry(cls: type["AIAssistant"]) -> dict[str, type["AIAssistant"]]:
        registry: dict[str, type["AIAssistant"]] = {}
        for subclass in cls.__subclasses__():
            registry[subclass.id] = subclass
            registry.update(subclass._get_assistant_cls_registry())
        return registry

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
        context_key = self.get_context_key()
        if self.has_rag and f"{context_key}" not in instructions:
            raise AIAssistantMisconfiguredError(
                f"{self.__class__.__name__} has_rag=True"
                f"but does not have a {{{context_key}}} placeholder in instructions."
            )

        return ChatPromptTemplate.from_messages(
            [
                ("system", instructions),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

    def get_message_history(self, thread_id: int | None):
        # DjangoChatMessageHistory must be here because Django may not be loaded yet elsewhere:
        from django_ai_assistant.langchain.chat_message_histories import DjangoChatMessageHistory

        if thread_id is None:
            return InMemoryChatMessageHistory()
        return DjangoChatMessageHistory(thread_id)

    def get_llm(self):
        model = self.get_model()
        temperature = self.get_temperature()
        model_kwargs = self.get_model_kwargs()
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            model_kwargs=model_kwargs,
        )

    def get_tools(self) -> Sequence[BaseTool]:
        return self._method_tools

    def get_document_separator(self) -> str:
        return DEFAULT_DOCUMENT_SEPARATOR

    def get_document_prompt(self) -> PromptTemplate:
        return DEFAULT_DOCUMENT_PROMPT

    def get_context_key(self) -> str:
        return "context"

    def get_retriever(self) -> BaseRetriever:
        raise NotImplementedError(
            f"Override the get_retriever with your implementation at {self.__class__.__name__}"
        )

    def get_contextualize_prompt(self) -> ChatPromptTemplate:
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        return ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("history"),
                ("human", "{input}"),
            ]
        )

    def get_history_aware_retriever(self) -> Runnable[dict, RetrieverOutput]:
        llm = self.get_llm()
        retriever = self.get_retriever()
        prompt = self.get_contextualize_prompt()

        # Based on create_history_aware_retriever:
        return RunnableBranch(
            (
                lambda x: not x.get("history", False),  # pyright: ignore[reportAttributeAccessIssue]
                # If no chat history, then we just pass input to retriever
                (lambda x: x["input"]) | retriever,
            ),
            # If chat history, then we pass inputs to LLM chain, then to retriever
            prompt | llm | StrOutputParser() | retriever,
        )

    def as_chain(self, thread_id: int | None) -> Runnable[dict, dict]:
        # Based on:
        # - https://python.langchain.com/v0.2/docs/how_to/qa_chat_history_how_to/
        # - https://python.langchain.com/v0.2/docs/how_to/migrate_agent/
        # TODO: use langgraph instead?
        llm = self.get_llm()
        tools = self.get_tools()
        prompt = self.get_prompt_template()
        tools = cast(Sequence[BaseTool], tools)
        if tools:
            llm_with_tools = llm.bind_tools(tools)
        else:
            llm_with_tools = llm
        chain = (
            # based on create_tool_calling_agent:
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_tool_messages(x["intermediate_steps"])
            ).with_config(run_name="format_to_tool_messages")
        )

        if self.has_rag:
            # based on create_retrieval_chain:
            retriever = self.get_history_aware_retriever()
            chain = chain | RunnablePassthrough.assign(
                docs=retriever.with_config(run_name="retrieve_documents"),
            )

            # based on create_stuff_documents_chain:
            document_separator = self.get_document_separator()
            document_prompt = self.get_document_prompt()
            context_key = self.get_context_key()
            chain = chain | RunnablePassthrough.assign(
                **{
                    context_key: lambda x: document_separator.join(
                        format_document(doc, document_prompt) for doc in x["docs"]
                    )
                }
            ).with_config(run_name="format_input_docs")

        chain = chain | prompt | llm_with_tools | ToolsAgentOutputParser()

        agent_executor = AgentExecutor(
            agent=chain,  # pyright: ignore[reportArgumentType]
            tools=tools,
        )
        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,  # pyright: ignore[reportArgumentType]
            get_session_history=self.get_message_history,
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
        ).with_config(
            {"configurable": {"thread_id": thread_id}},
            run_name="agent_with_chat_history",
        )

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


def get_assistant_cls_registry() -> dict[str, type[AIAssistant]]:
    return AIAssistant._get_assistant_cls_registry()
