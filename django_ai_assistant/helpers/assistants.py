import abc
import inspect
import re
from typing import Annotated, Any, ClassVar, Dict, Sequence, Type, TypedDict, cast

from langchain.chains.combine_documents.base import (
    DEFAULT_DOCUMENT_PROMPT,
    DEFAULT_DOCUMENT_SEPARATOR,
)
from langchain.tools import StructuredTool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
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
    Runnable,
    RunnableBranch,
)
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from django_ai_assistant.decorators import with_cast_id
from django_ai_assistant.exceptions import (
    AIAssistantMisconfiguredError,
)
from django_ai_assistant.helpers.django_messages import save_django_messages
from django_ai_assistant.langchain.tools import tool as tool_decorator


class AIAssistant(abc.ABC):  # noqa: F821
    """Base class for AI Assistants. Subclasses must define at least the following attributes:

    * id: str
    * name: str
    * instructions: str
    * model: str

    Subclasses can override the public methods to customize the behavior of the assistant.\n
    Tools can be added to the assistant by decorating methods with `@method_tool`.\n
    Check the docs Tutorial for more info on how to build an AI Assistant.
    """

    id: ClassVar[str]  # noqa: A003
    """Class variable with the id of the assistant. Used to select the assistant to use.\n
    Must be unique across the whole Django project and match the pattern '^[a-zA-Z0-9_-]+$'."""
    name: ClassVar[str]
    """Class variable with the name of the assistant.
    Should be a friendly name to optionally display to users."""
    instructions: str
    """Instructions for the AI assistant knowing what to do. This is the LLM system prompt."""
    model: str
    """LLM model name to use for the assistant.\n
    Should be a valid model name from OpenAI, because the default `get_llm` method uses OpenAI.\n
    `get_llm` can be overridden to use a different LLM implementation.
    """
    temperature: float = 1.0
    """Temperature to use for the assistant LLM model.\nDefaults to `1.0`."""
    tool_max_concurrency: int = 1
    """Maximum number of tools to run concurrently / in parallel.\nDefaults to `1` (no concurrency)."""
    has_rag: bool = False
    """Whether the assistant uses RAG (Retrieval-Augmented Generation) or not.\n
    Defaults to `False`.
    When True, the assistant will use a retriever to get documents to provide as context to the LLM.
    Additionally, the assistant class should implement the `get_retriever` method to return
    the retriever to use."""
    structured_output: Dict[str, Any] | Type[BaseModel] | Type | None = None
    """Structured output to use for the assistant.\n
    Defaults to `None`.
    When not `None`, the assistant will return a structured output in the provided format.
    See https://python.langchain.com/v0.3/docs/how_to/structured_output/ for the available formats.
    """
    _user: Any | None
    """The current user the assistant is helping. A model instance.\n
    Set by the constructor.
    When API views are used, this is set to the current request user.\n
    Can be used in any `@method_tool` to customize behavior."""
    _request: Any | None
    """The current Django request the assistant was initialized with. A request instance.\n
    Set by the constructor.\n
    Can be used in any `@method_tool` to customize behavior."""
    _view: Any | None
    """The current Django view the assistant was initialized with. A view instance.\n
    Set by the constructor.\n
    Can be used in any `@method_tool` to customize behavior."""
    _init_kwargs: dict[str, Any]
    """Extra keyword arguments passed to the constructor.\n
    Set by the constructor.\n
    Can be used in any `@method_tool` to customize behavior."""
    _method_tools: Sequence[BaseTool]
    """List of `@method_tool` tools the assistant can use. Automatically set by the constructor."""

    _registry: ClassVar[dict[str, type["AIAssistant"]]] = {}
    """Registry of all AIAssistant subclasses by their id.\n
    Automatically populated by when a subclass is declared.\n
    Use `get_cls_registry` and `get_cls` to access the registry."""

    def __init__(self, *, user=None, request=None, view=None, **kwargs: Any):
        """Initialize the AIAssistant instance.\n
        Optionally set the current user, request, and view for the assistant.\n
        Those can be used in any `@method_tool` to customize behavior.\n

        Args:
            user (Any | None): The current user the assistant is helping. A model instance.
                Defaults to `None`. Stored in `self._user`.
            request (Any | None): The current Django request the assistant was initialized with.
                A request instance. Defaults to `None`. Stored in `self._request`.
            view (Any | None): The current Django view the assistant was initialized with.
                A view instance. Defaults to `None`. Stored in `self._view`.
            **kwargs: Extra keyword arguments passed to the constructor. Stored in `self._init_kwargs`.
        """

        self._user = user
        self._request = request
        self._view = view
        self._init_kwargs = kwargs

        self._set_method_tools()

    def __init_subclass__(cls, **kwargs: Any):
        """Called when a class is subclassed from AIAssistant.

        This method is automatically invoked when a new subclass of AIAssistant
        is created. It allows AIAssistant to perform additional setup or configuration
        for the subclass, such as registering the subclass in a registry.

        Args:
            cls (type): The newly created subclass.
            **kwargs: Additional keyword arguments passed during subclass creation.
        """
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "id"):
            raise AIAssistantMisconfiguredError(f"Assistant id is not defined at {cls.__name__}")
        if cls.id is None:
            raise AIAssistantMisconfiguredError(f"Assistant id is None at {cls.__name__}")
        if not re.match(r"^[a-zA-Z0-9_-]+$", cls.id):
            # id should match the pattern '^[a-zA-Z0-9_-]+$ to support as_tool in OpenAI
            raise AIAssistantMisconfiguredError(
                f"Assistant id '{cls.id}' does not match the pattern '^[a-zA-Z0-9_-]+$'"
                f"at {cls.__name__}"
            )

        cls._registry[cls.id] = cls

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
    def get_cls_registry(cls) -> dict[str, type["AIAssistant"]]:
        """Get the registry of AIAssistant classes.

        Returns:
            dict[str, type[AIAssistant]]: A dictionary mapping assistant ids to their classes.
        """
        return cls._registry

    @classmethod
    def get_cls(cls, assistant_id: str) -> type["AIAssistant"]:
        """Get the AIAssistant class for the given assistant ID.

        Args:
            assistant_id (str): The ID of the assistant to get.
        Returns:
            type[AIAssistant]: The AIAssistant subclass for the given ID.
        """
        return cls.get_cls_registry()[assistant_id]

    @classmethod
    def clear_cls_registry(cls: type["AIAssistant"]) -> None:
        """Clear the registry of AIAssistant classes."""

        cls._registry.clear()

    def get_instructions(self) -> str:
        """Get the instructions for the assistant. By default, this is the `instructions` attribute.\n
        Override the `instructions` attribute or this method to use different instructions.

        Returns:
            str: The instructions for the assistant, i.e., the LLM system prompt.
        """
        return self.instructions

    def get_model(self) -> str:
        """Get the LLM model name for the assistant. By default, this is the `model` attribute.\n
        Used by the `get_llm` method to create the LLM instance.\n
        Override the `model` attribute or this method to use a different LLM model.

        Returns:
            str: The LLM model name for the assistant.
        """
        return self.model

    def get_temperature(self) -> float:
        """Get the temperature to use for the assistant LLM model.
        By default, this is the `temperature` attribute, which is `1.0` by default.\n
        Used by the `get_llm` method to create the LLM instance.\n
        Override the `temperature` attribute or this method to use a different temperature.

        Returns:
            float: The temperature to use for the assistant LLM model.
        """
        return self.temperature

    def get_model_kwargs(self) -> dict[str, Any]:
        """Get additional keyword arguments to pass to the LLM model constructor.\n
        Used by the `get_llm` method to create the LLM instance.\n
        Override this method to pass additional keyword arguments to the LLM model constructor.

        Returns:
            dict[str, Any]: Additional keyword arguments to pass to the LLM model constructor.
        """
        return {}

    def get_llm(self) -> BaseChatModel:
        """Get the LangChain LLM instance for the assistant.
        By default, this uses the OpenAI implementation.\n
        `get_model`, `get_temperature`, and `get_model_kwargs` are used to create the LLM instance.\n
        Override this method to use a different LLM implementation.

        Returns:
            BaseChatModel: The LLM instance for the assistant.
        """
        model = self.get_model()
        temperature = self.get_temperature()
        model_kwargs = self.get_model_kwargs()
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            model_kwargs=model_kwargs,
        )

    def get_structured_output_llm(self) -> Runnable:
        """Get the LLM model to use for the structured output.

        Returns:
            BaseChatModel: The LLM model to use for the structured output.
        """
        if not self.structured_output:
            raise ValueError("structured_output is not defined")

        llm = self.get_llm()

        method = "json_mode"
        if isinstance(llm, ChatOpenAI):
            # When using ChatOpenAI, it's better to use json_schema method
            # because it enables strict mode.
            # https://platform.openai.com/docs/guides/structured-outputs
            method = "json_schema"

        return llm.with_structured_output(self.structured_output, method=method)

    def get_tools(self) -> Sequence[BaseTool]:
        """Get the list of method tools the assistant can use.
        By default, this is the `_method_tools` attribute, which are all `@method_tool`s.\n
        Override and call super to add additional tools,
        such as [any langchain_community tools](https://python.langchain.com/v0.3/docs/integrations/tools/).

        Returns:
            Sequence[BaseTool]: The list of tools the assistant can use.
        """
        return self._method_tools

    def get_document_separator(self) -> str:
        """Get the RAG document separator to use in the prompt. Only used when `has_rag=True`.\n
        Defaults to `"\\n\\n"`, which is the LangChain default.\n
        Override this method to use a different separator.

        Returns:
            str: a separator for documents in the prompt.
        """
        return DEFAULT_DOCUMENT_SEPARATOR

    def get_document_prompt(self) -> PromptTemplate:
        """Get the PromptTemplate template to use when rendering RAG documents in the prompt.
        Only used when `has_rag=True`.\n
        Defaults to `PromptTemplate.from_template("{page_content}")`, which is the LangChain default.\n
        Override this method to use a different template.

        Returns:
            PromptTemplate: a prompt template for RAG documents.
        """
        return DEFAULT_DOCUMENT_PROMPT

    def get_retriever(self) -> BaseRetriever:
        """Get the RAG retriever to use for fetching documents.\n
        Must be implemented by subclasses when `has_rag=True`.\n

        Returns:
            BaseRetriever: the RAG retriever to use for fetching documents.
        """
        raise NotImplementedError(
            f"Override the get_retriever with your implementation at {self.__class__.__name__}"
        )

    def get_contextualize_prompt(self) -> ChatPromptTemplate:
        """Get the contextualize prompt template for the assistant.\n
        This is used when `has_rag=True` and there are previous messages in the thread.
        Since the latest user question might reference the chat history,
        the LLM needs to generate a new standalone question,
        and use that question to query the retriever for relevant documents.\n
        By default, this is a prompt that asks the LLM to
        reformulate the latest user question without the chat history.\n
        Override this method to use a different contextualize prompt.\n
        See `get_history_aware_retriever` for how this prompt is used.\n

        Returns:
            ChatPromptTemplate: The contextualize prompt template for the assistant.
        """
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
                # TODO: make history key configurable?
                MessagesPlaceholder("history"),
                # TODO: make input key configurable?
                ("human", "{input}"),
            ]
        )

    def get_history_aware_retriever(self) -> Runnable[dict, RetrieverOutput]:
        """Get the history-aware retriever LangChain chain for the assistant.\n
        This is used when `has_rag=True` to fetch documents based on the chat history.\n
        By default, this is a chain that checks if there is chat history,
        and if so, it uses the chat history to generate a new standalone question
        to query the retriever for relevant documents.\n
        When there is no chat history, it just passes the input to the retriever.\n
        Override this method to use a different history-aware retriever chain.

        Read more about the history-aware retriever in the
        [LangChain docs](https://python.langchain.com/v0.2/docs/how_to/qa_chat_history_how_to/).

        Returns:
            Runnable[dict, RetrieverOutput]: a history-aware retriever LangChain chain.
        """
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

    @with_cast_id
    def as_graph(self, thread_id: Any | None = None) -> Runnable[dict, dict]:
        """Create the LangGraph graph for the assistant.\n
        This graph is an agent that supports chat history, tool calling, and RAG (if `has_rag=True`).\n
        `as_graph` uses many other methods to create the graph for the assistant.
        Prefer to override the other methods to customize the graph for the assistant.
        Only override this method if you need to customize the graph at a lower level.

        Args:
            thread_id (Any | None): The thread ID for the chat message history.
                If `None`, an in-memory chat message history is used.

        Returns:
            the compiled graph
        """
        from django_ai_assistant.models import Thread

        llm = self.get_llm()
        tools = self.get_tools()
        llm_with_tools = llm.bind_tools(tools) if tools else llm
        if thread_id:
            thread = Thread.objects.get(id=thread_id)
        else:
            thread = None

        def custom_add_messages(left: list[BaseMessage], right: list[BaseMessage]):
            result = add_messages(left, right)  # type: ignore
            if thread:
                # Save all messages, except the initial system message:
                thread_messages = [m for m in result if not isinstance(m, SystemMessage)]
                save_django_messages(cast(list[BaseMessage], thread_messages), thread=thread)
            return result

        class AgentState(TypedDict):
            messages: Annotated[list[AnyMessage], custom_add_messages]
            input: str | None  # noqa: A003
            output: Any

        def setup(state: AgentState):
            system_prompt = self.get_instructions()
            return {"messages": [SystemMessage(content=system_prompt)]}

        def history(state: AgentState):
            messages = thread.get_messages(include_extra_messages=True) if thread else []
            if state["input"]:
                messages.append(HumanMessage(content=state["input"]))

            return {"messages": messages}

        def retriever(state: AgentState):
            if not self.has_rag:
                return

            retriever = self.get_history_aware_retriever()
            # Remove the initial instructions to prevent having two SystemMessages
            # This is necessary for compatibility with Anthropic
            messages_to_summarize = state["messages"][1:-1]
            input_message = state["messages"][-1]
            docs = retriever.invoke({"input": input_message, "history": messages_to_summarize})

            document_separator = self.get_document_separator()
            document_prompt = self.get_document_prompt()

            formatted_docs = document_separator.join(
                format_document(doc, document_prompt) for doc in docs
            )

            system_message = state["messages"][0]
            system_message.content += (
                f"\n\n---START OF CONTEXT---\n{formatted_docs}---END OF CONTEXT---\n\n"
            )

        def agent(state: AgentState):
            response = llm_with_tools.invoke(state["messages"])

            return {"messages": [response]}

        def tool_selector(state: AgentState):
            last_message = state["messages"][-1]

            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                return "call_tool"

            return "continue"

        def record_response(state: AgentState):
            # Structured output must happen in the end, to avoid disabling tool calling.
            # Tool calling + structured output is not supported by OpenAI:
            if self.structured_output:
                messages = state["messages"]

                # Change the original system prompt:
                if isinstance(messages[0], SystemMessage):
                    messages[0].content += "\nUse the chat history to produce a JSON output."

                # Add a final message asking for JSON generation / structured output:
                json_request_message = HumanMessage(
                    content="Use the chat history to produce a JSON output."
                )
                messages.append(json_request_message)

                llm_with_structured_output = self.get_structured_output_llm()
                response = llm_with_structured_output.invoke(messages)
            else:
                response = state["messages"][-1].content

            return {"output": response}

        workflow = StateGraph(AgentState)

        workflow.add_node("setup", setup)
        workflow.add_node("history", history)
        workflow.add_node("retriever", retriever)
        workflow.add_node("agent", agent)
        workflow.add_node("tools", ToolNode(tools))
        workflow.add_node("respond", record_response)

        workflow.set_entry_point("setup")
        workflow.add_edge("setup", "history")
        workflow.add_edge("history", "retriever")
        workflow.add_edge("retriever", "agent")
        workflow.add_conditional_edges(
            "agent",
            tool_selector,
            {
                "call_tool": "tools",
                "continue": "respond",
            },
        )
        workflow.add_edge("tools", "agent")
        workflow.add_edge("respond", END)

        return workflow.compile()

    @with_cast_id
    def invoke(self, *args: Any, thread_id: Any | None, **kwargs: Any) -> dict:
        """Invoke the assistant LangChain graph with the given arguments and keyword arguments.\n
        This is the lower-level method to run the assistant.\n
        The graph is created by the `as_graph` method.\n

        Args:
            *args: Positional arguments to pass to the graph.
                To add a new message, use a dict like `{"input": "user message"}`.
                If thread already has a `HumanMessage` in the end, you can invoke without args.
            thread_id (Any | None): The thread ID for the chat message history.
                If `None`, an in-memory chat message history is used.
            **kwargs: Keyword arguments to pass to the graph.

        Returns:
            dict: The output of the assistant graph,
                structured like `{"output": "assistant response", "history": ...}`.
        """
        graph = self.as_graph(thread_id)
        config = kwargs.pop("config", {})
        config["max_concurrency"] = config.pop("max_concurrency", self.tool_max_concurrency)
        return graph.invoke(*args, config=config, **kwargs)

    @with_cast_id
    def run(self, message: str, thread_id: Any | None = None, **kwargs: Any) -> Any:
        """Run the assistant with the given message and thread ID.\n
        This is the higher-level method to run the assistant.\n

        Args:
            message (str): The user message to pass to the assistant.
            thread_id (Any | None): The thread ID for the chat message history.
                If `None`, an in-memory chat message history is used.
            **kwargs: Additional keyword arguments to pass to the graph.

        Returns:
            Any: The assistant response to the user message.
        """
        return self.invoke(
            {
                "input": message,
            },
            thread_id=thread_id,
            **kwargs,
        )["output"]

    def _run_as_tool(self, message: str, **kwargs: Any) -> Any:
        return self.run(message, thread_id=None, **kwargs)

    def as_tool(self, description: str) -> BaseTool:
        """Create a tool from the assistant.\n
        This is useful to compose assistants.\n

        Args:
            description (str): The description for the tool.

        Returns:
            BaseTool: A tool that runs the assistant. The tool name is this assistant's id.
        """
        return StructuredTool.from_function(
            func=self._run_as_tool,
            name=self.id,
            description=description,
        )
