---
search:
    boost: 2
---

# Tutorial

In this tutorial, you will learn how to use Django AI Assistant to supercharge your Django project with LLM capabilities.

## Prerequisites

Make sure you properly configured Django AI Assistant as described in the [Get Started](get-started.md) guide.

## Setting up API keys

The tutorial below uses OpenAI's gpt-4o model, so make sure you have `OPENAI_API_KEY` set as an environment variable for your Django project.
You can also use other models, keep reading to learn more. Just make sure their keys are properly set.

!!! note
    An easy way to set environment variables is to use a `.env` file in your project's root directory and use `python-dotenv` to load them.
    Our [example project](https://github.com/vintasoftware/django-ai-assistant/tree/main/example#readme) uses this approach.

## What AI Assistants can do

AI Assistants are LLMs that can answer to user queries as ChatGPT does, i.e. inputting and outputting strings.
But when integrated with Django, they can also do anything a Django view can, such as accessing the database,
checking permissions, sending emails, downloading and uploading media files, etc.
This is possible by defining "tools" the AI can use. These tools are methods in an AI Assistant class on the Django side.

## Defining an AI Assistant

### Registering

To create an AI Assistant, you need to:

1. Create an `ai_assistants.py` file;
2. Define a class that inherits from `AIAssistant`;
3. Provide an `id`, a `name`, some `instructions` for the LLM (a system prompt), and a `model` name:

```python title="myapp/ai_assistants.py"
from django_ai_assistant import AIAssistant

class WeatherAIAssistant(AIAssistant):
    id = "weather_assistant"
    name = "Weather Assistant"
    instructions = "You are a weather bot."
    model = "gpt-4o"
```

### Defining tools

Useful tools give abilities the LLM doesn't have out-of-the-box,
such as getting the current date and finding the current weather by calling an API.

Use the `@method_tool` decorator to define a tool method in the AI Assistant:

```{.python title="myapp/ai_assistants.py" hl_lines="14-21"}
from django.utils import timezone
from django_ai_assistant import AIAssistant, method_tool
import json

class WeatherAIAssistant(AIAssistant):
    id = "weather_assistant"
    name = "Weather Assistant"
    instructions = "You are a weather bot."
    model = "gpt-4o"

    def get_instructions(self):
        return f"{self.instructions} Today is {timezone.now().isoformat()}."

    @method_tool
    def get_weather(self, location: str) -> str:
        """Fetch the current weather data for a location"""
        return json.dumps({
            "location": location,
            "temperature": "25°C",
            "weather": "sunny"
        })  # imagine some weather API here, this is just a placeholder
```

The `get_weather` method is a tool that the AI Assistant can use to get the current weather for a location, when the user asks for it.
The tool method must be fully type-hinted (all parameters and return value), and it must include a descriptive docstring.
This is necessary for the LLM model to understand the tool's purpose.

A conversation with this Weather Assistant looks like this:

```txt
User: What's the weather in New York City?
AI: The weather in NYC is sunny with a temperature of 25°C.
```

!!! note
    State of the art models such as gpt-4o can process JSON well.
    You can return a `json.dumps(api_output)` from a tool method and the model will be able to process it before responding the user.

### Tool parameters

It's possible to define more complex parameters for tools. As long as they're JSON serializable, the underlying LLM model should be able to call tools with the right arguments.

In the `MovieRecommendationAIAssistant` from the [example project](https://github.com/vintasoftware/django-ai-assistant/tree/main/example#readme), we have a `reorder_backlog` tool method that receives a list of IMDb URLs that represent the user's movie backlog order. Note the `Sequence[str]` parameter:

```{.python title="example/movies/ai_assistants.py" hl_lines="7"}
from django_ai_assistant import AIAssistant, method_tool

class MovieRecommendationAIAssistant(AIAssistant):
    ...

    @method_tool
    def reorder_backlog(self, imdb_url_list: Sequence[str]) -> str:
        """Reorder movies in user's backlog."""
        ...
```

In `WeatherAIAssistant`, another assistant from the example project, we have a `fetch_forecast_weather` method tool with a `args_schema` parameter that defines a JSON schema for the tool arguments:

```{.python title="example/weather/ai_assistants.py" hl_lines="6-8 10"}
from django_ai_assistant import AIAssistant, method_tool, BaseModel, Field

class WeatherAIAssistant(AIAssistant):
    ...

    class FetchForecastWeatherInput(BaseModel):
        location: str = Field(description="Location to fetch the forecast weather for")
        forecast_date: date = Field(description="Date in the format 'YYYY-MM-DD'")

    @method_tool(args_schema=FetchForecastWeatherInput)
    def fetch_forecast_weather(self, location, forecast_date) -> dict:
        """Fetch the forecast weather data for a location"""
        # forecast_date is a `date` object here
        ...
```

!!! note
    It's important to provide a `description` for each field from `args_schema`. This improves the LLM's understanding of the tool's arguments.

### Using Django logic in tools

You have access to the current request user in tools:

```{.python title="myapp/ai_assistants.py" hl_lines=12}
from django_ai_assistant import AIAssistant, method_tool

class PersonalAIAssistant(AIAssistant):
    id = "personal_assistant"
    name = "Personal Assistant"
    instructions = "You are a personal assistant."
    model = "gpt-4o"

    @method_tool
    def get_current_user_username(self) -> str:
        """Get the username of the current user"""
        return self._user.username
```

You can also add any Django logic to tools, such as querying the database:

```{.python title="myapp/ai_assistants.py" hl_lines=13-15}
from django_ai_assistant import AIAssistant, method_tool
import json

class IssueManagementAIAssistant(AIAssistant):
    id = "issue_mgmt_assistant"
    name = "Issue Management Assistant"
    instructions = "You are an issue management bot."
    model = "gpt-4o"

    @method_tool
    def get_current_user_assigned_issues(self) -> str:
        """Get the issues assigned to the current user"""
        return json.dumps({
            "issues": list(Issue.objects.filter(assignee=self._user).values())
        })
```

!!! warning
    Make sure you only return to the LLM what the user can see, considering permissions and privacy.
    Code the tools as if they were Django views.

### Using pre-implemented tools

Django AI Assistant works with [any LangChain-compatible tool](https://python.langchain.com/v0.3/docs/integrations/tools/).
Just override the `get_tools` method in your AI Assistant class to include the tools you want to use.

For example, you can use the `TavilySearch` tool to provide your AI Assistant with the ability to search the web
for information about upcoming movies.

First install dependencies:

```bash
pip install -U langchain-community tavily-python
```

Then, set the `TAVILY_API_KEY` environment variable. You'll need to sign up at [Tavily](https://tavily.com/).

Finally, add the tool to your AI Assistant class by overriding the `get_tools` method:

```{.python title="myapp/ai_assistants.py"  hl_lines="2 19"}
from django_ai_assistant import AIAssistant
from langchain_community.tools.tavily_search import TavilySearchResults

class MovieSearchAIAssistant(AIAssistant):
    id = "movie_search_assistant"  # noqa: A003
    instructions = (
        "You're a helpful movie search assistant. "
        "Help the user find more information about movies. "
        "Use the provided tools to search the web for upcoming movies. "
    )
    name = "Movie Search Assistant"
    model = "gpt-4o"

    def get_instructions(self):
        return f"{self.instructions} Today is {timezone.now().isoformat()}."

    def get_tools(self):
        return [
            TavilySearchResults(),
            *super().get_tools(),
        ]
```

!!! note
    As of now, Django AI Assistant is powered by [LangChain](https://python.langchain.com/v0.3/docs/introduction/)
    and [LangGraph](https://langchain-ai.github.io/langgraph/tutorials/introduction/),
    but knowledge on these tools is NOT necessary to use this library, at least for the main use cases.

## Using an AI Assistant

### Manually calling an AI Assistant

You can manually call an AI Assistant from anywhere in your Django application:

```python
from myapp.ai_assistants import WeatherAIAssistant

assistant = WeatherAIAssistant()
output = assistant.run("What's the weather in New York City?")
assert output == "The weather in NYC is sunny with a temperature of 25°C."
```

The constructor of `AIAssistant` receives `user`, `request`, `view` as optional parameters,
which can be used in the tools with `self._user`, `self._request`, `self._view`.
Also, any extra parameters passed in constructor are stored at `self._init_kwargs`.

### Threads of Messages

The django-ai-assistant app provides two models `Thread` and `Message` to store and retrieve conversations with AI Assistants.
LLMs are stateless by design, meaning they don't hold any context between calls. All they know is the current input.
But by using the `AIAssistant` class, the conversation state is stored in the database as multiple `Message` of a `Thread`,
and automatically retrieved then passed to the LLM when calling the AI Assistant.

To create a `Thread`, you can use a helper from the `django_ai_assistant.use_cases` module. For example:

```{.python hl_lines="4 8"}
from django_ai_assistant.use_cases import create_thread, get_thread_messages
from myapp.ai_assistants import WeatherAIAssistant

thread = create_thread(name="Weather Chat", user=user)
assistant = WeatherAIAssistant()
assistant.run("What's the weather in New York City?", thread_id=thread.id)

messages = get_thread_messages(thread=thread, user=user)  # returns both user and AI messages
```

More CRUD helpers are available at `django_ai_assistant.use_cases` module. Check the [Reference](reference/use-cases-ref.md) for more information.

### Using built-in API views

You can use the built-in API views to interact with AI Assistants via HTTP requests from any frontend,
such as a React application or a mobile app. Add the following to your Django project's `urls.py`:

```python title="myproject/urls.py"
from django.urls import include, path

urlpatterns = [
    path("ai-assistant/", include("django_ai_assistant.urls")),
    ...
]
```

The built-in API supports retrieval of Assistants info, as well as CRUD for Threads and Messages.
It has a OpenAPI schema that you can explore at `http://localhost:8000/ai-assistant/docs`, when running your project locally.

#### Configuring the API

The built-in API is implemented using [Django Ninja](https://django-ninja.dev/reference/api/). By default, it is initialized with the following setting:

```python title="myproject/settings.py"
AI_ASSISTANT_INIT_API_FN = "django_ai_assistant.api.views.init_api"
```

You can override this setting in your Django project's `settings.py` to customize the API, such as using a different authentication method or modifying other configurations.

The method signature for `AI_ASSISTANT_INIT_API_FN` is as follows:

```python
from ninja import NinjaAPI

def init_api():
    return NinjaAPI(...)
```

By providing your own implementation of `init_api`, you can tailor the API setup to better fit your project's requirements.

### Configuring permissions

The API uses the helpers from the `django_ai_assistant.use_cases` module, which have permission checks
to ensure the user can use a certain AI Assistant or do CRUD on Threads and Messages.

By default, any authenticated user can use any AI Assistant, and create a thread.
Users can manage both their own threads and the messages on them. Therefore, the default permissions are:

```python title="myproject/settings.py"
AI_ASSISTANT_CAN_CREATE_THREAD_FN = "django_ai_assistant.permissions.allow_all"
AI_ASSISTANT_CAN_VIEW_THREAD_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_UPDATE_THREAD_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_DELETE_THREAD_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_CREATE_MESSAGE_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_UPDATE_MESSAGE_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_DELETE_MESSAGE_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_RUN_ASSISTANT = "django_ai_assistant.permissions.allow_all"
```

You can override these settings in your Django project's `settings.py` to customize the permissions.

Thread permission signatures look like this:

```python
from django_ai_assistant.models import Thread
from django.http import HttpRequest

def check_custom_thread_permission(
        thread: Thread,
        user: Any,
        request: HttpRequest | None = None) -> bool:
    return ...
```

While Message permission signatures look like this:

```python
from django_ai_assistant.models import Thread, Message
from django.http import HttpRequest

def check_custom_message_permission(
        message: Message,
        thread: Thread,
        user: Any,
        request: HttpRequest | None = None) -> bool:
    return ...
```

## Frontend integration

You can integrate Django AI Assistant with frontend frameworks like React or Vue.js. Please check the [frontend documentation](frontend.md).

If you want to use traditional Django templates, you can try using HTMX to avoid page refreshes. Check the [example project](https://github.com/vintasoftware/django-ai-assistant/tree/main/example#readme), it includes a HTMX application.

## Advanced usage

### Using other AI models

By default the supported models are OpenAI ones,
but you can use [any chat model from LangChain that supports Tool Calling](https://python.langchain.com/docs/integrations/chat/#featured-providers) by overriding `get_llm`:

```python title="myapp/ai_assistants.py"
from django_ai_assistant import AIAssistant
from langchain_anthropic import ChatAnthropic

class WeatherAIAssistant(AIAssistant):
    id = "weather_assistant"
    name = "Weather Assistant"
    instructions = "You are a weather bot."
    model = "claude-3-opus-20240229"

    def get_llm(self):
        model = self.get_model()
        temperature = self.get_temperature()
        model_kwargs = self.get_model_kwargs()
        return ChatAnthropic(
            model_name=model,
            temperature=temperature,
            model_kwargs=model_kwargs,
            timeout=None,
            max_retries=2,
        )
```

### Composing AI Assistants

One AI Assistant can call another AI Assistant as a tool. This is useful for composing complex AI Assistants.
Use the `as_tool` method for that:

```{.python title="myapp/ai_assistants.py"  hl_lines="12 14"}
class SimpleAssistant(AIAssistant):
    ...

class AnotherSimpleAssistant(AIAssistant):
    ...

class ComplexAssistant(AIAssistant):
    ...

    def get_tools(self) -> Sequence[BaseTool]:
        return [
            SimpleAssistant().as_tool(
                description="Tool to <...add a meaningful description here...>"),
            AnotherSimpleAssistant().as_tool(
                description="Tool to <...add a meaningful description here...>"),
            *super().get_tools(),
        ]
```

The `movies/ai_assistants.py` file in the [example project](https://github.com/vintasoftware/django-ai-assistant/tree/main/example#readme)
shows an example of a composed AI Assistant that's able to recommend movies and manage the user's movie backlog.

### Retrieval Augmented Generation (RAG)

You can use RAG in your AI Assistants. RAG means using a retriever to fetch chunks of textual data from a pre-existing DB to give
context to the LLM. This means the LLM will have access to a context your retriever logic provides when generating the response,
thereby improving the quality of the response by avoiding generic or off-topic answers.

For this to work, your must do the following in your AI Assistant:

1. Add `has_rag = True` as a class attribute;
2. Override the `get_retriever` method to return a [LangChain Retriever](https://python.langchain.com/v0.3/docs/how_to/#retrievers).

For example:

```{.python title="myapp/ai_assistants.py"  hl_lines="11 15 17"}
from django_ai_assistant import AIAssistant

class DocsAssistant(AIAssistant):
    id = "docs_assistant"  # noqa: A003
    name = "Docs Assistant"
    instructions = (
        "You are an assistant for answering questions related to the provided context. "
        "Use the following pieces of retrieved context to answer the user's question. "
    )
    model = "gpt-4o"
    has_rag = True

    def get_retriever(self) -> BaseRetriever:
        return ...  # use a LangChain Retriever here
```

The `rag/ai_assistants.py` file in the [example project](https://github.com/vintasoftware/django-ai-assistant/tree/main/example#readme)
shows an example of a RAG-powered AI Assistant that's able to answer questions about Django using the Django Documentation as context.

### Support for other types of Primary Key (PK)

You can have Django AI Assistant models use other types of primary key, such as strings, UUIDs, etc.
This is useful if you're concerned about leaking IDs that exponse thread count, message count, etc. to the frontend.
When using UUIDs, it will prevent users from figuring out if a thread or message exist or not (due to HTTP 404 vs 403).

Here are the files you have to change if you need the ids to be UUID:

```{.python title="myapp/fields.py"}
import uuid
from django.db.backends.base.operations import BaseDatabaseOperations
from django.db.models import AutoField, UUIDField

BaseDatabaseOperations.integer_field_ranges['UUIDField'] = (0, 0)

class UUIDAutoField(UUIDField, AutoField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', uuid.uuid4)
        kwargs.setdefault('editable', False)
        super().__init__(*args, **kwargs)
```

```{.python title="myapp/apps.py"}
from django_ai_assistant.apps import AIAssistantConfig

class AIAssistantConfigOverride(AIAssistantConfig):
    default_auto_field = "django_ai_assistant.api.fields.UUIDAutoField"
```

```{.python title="myproject/settings.py"}
INSTALLED_APPS = [
    # "django_ai_assistant", remove this line and add the one below
    "example.apps.AIAssistantConfigOverride",
]
```

Make sure to run migrations after those changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

For more information, check [Django docs on overriding AppConfig](https://docs.djangoproject.com/en/5.0/ref/applications/#for-application-users).

### Further configuration of AI Assistants

You can further configure the `AIAssistant` subclasses by overriding its public methods. Check the [Reference](reference/assistants-ref.md) for more information.
