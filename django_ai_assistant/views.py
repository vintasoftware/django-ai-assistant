import json

from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse as HttpResponse
from django.utils import timezone
from django.views import View

from openai import AsyncOpenAI

from .ai.assistant import run_assistant
from .conf import settings
from .models import Assistant, Thread


def _parse_json(request: HttpRequest) -> dict:
    try:
        if request.body:
            return json.loads(request.body)
        else:
            return {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)


class BaseAssistantView(View):
    def _get_default_kwargs(self):
        return {
            "request": self.request,
            "user": self.request.user,
            "view_kwargs": self.kwargs,
        }

    def get_ai_client(self) -> AsyncOpenAI:
        return settings.call_fn(
            "CLIENT_INIT_FN",
            **self._get_default_kwargs(),
        )

    def can_create_thread(self) -> bool:
        return settings.call_fn(
            "CAN_CREATE_THREAD_FN",
            **self._get_default_kwargs(),
        )

    def can_create_message(self, thread) -> bool:
        return settings.call_fn(
            "CAN_CREATE_MESSAGE_FN",
            **self._get_default_kwargs(),
            thread=thread,
        )

    def can_use_assistant(self, assistant) -> bool:
        return settings.call_fn(
            "CAN_USE_ASSISTANT",
            **self._get_default_kwargs(),
            assistant=assistant,
        )

    # Validate if user is authenticated:
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=403)
        return super().dispatch(request, *args, **kwargs)


class AssistantListView(BaseAssistantView):
    def list_assistants(self) -> list[dict]:
        client = self.get_ai_client()
        openai_assistant_dict = {}

        for assistant in client.beta.assistants.list(order="desc"):
            openai_assistant_dict[assistant.id] = assistant.to_dict()

        django_assistants = Assistant.objects.filter(openai_id__in=openai_assistant_dict.keys())
        for django_assistant in django_assistants:
            if not self.can_use_assistant(django_assistant):
                del openai_assistant_dict[django_assistant.openai_id]

        return list(openai_assistant_dict.values())

    def get(self, request: HttpRequest, *args, **kwargs):
        assistants = self.list_assistants()
        return JsonResponse({"object": "list", "data": assistants})


class ThreadListCreateView(BaseAssistantView):
    def get_default_thread_name(self, data: dict) -> str:
        return timezone.now().strftime("%Y-%m-%d %H:%M")

    def create_thread(self, name: str):
        client = self.get_ai_client()
        thread = client.beta.threads.create(metadata={"name": name})
        Thread.objects.create(name=name, created_by=self.request.user, openai_id=thread.id)
        return thread

    def list_threads(self) -> list[dict]:
        threads = []
        for thread in Thread.objects.filter(created_by=self.request.user):
            threads.append(
                {
                    "openai_id": thread.openai_id,
                    "name": thread.name,
                    "created_at": thread.created_at.isoformat(),
                    "updated_at": thread.updated_at.isoformat(),
                }
            )
        return threads

    def get(self, request: HttpRequest, *args, **kwargs):
        threads = self.list_threads()
        return JsonResponse({"object": "list", "data": threads})

    def post(self, request: HttpRequest, *args, **kwargs):
        if not self.can_create_thread():
            return JsonResponse({"error": "User is not allowed to create threads"}, status=403)
        data = _parse_json(request)

        thread = self.create_thread(name=data.get("name", self.get_default_thread_name(data)))
        return JsonResponse(thread.to_dict())


class ThreadMessageListCreateView(BaseAssistantView):
    django_thread: Thread

    def list_thread_messages(self):
        client = self.get_ai_client()
        yield from client.beta.threads.messages.list(thread_id=self.kwargs["thread_id"])

    def create_thread_message(self, content: str):
        client = self.get_ai_client()
        return client.beta.threads.messages.create(
            thread_id=self.kwargs["thread_id"], role="user", content=content
        )

    def create_run(self, assistant_id: str):
        # TODO: Decide how to deal with fn changes (migrations) and how to sync with OpenAI.
        client = self.get_ai_client()
        thread_id = self.kwargs["thread_id"]
        # TODO: handle exceptions properly
        event_handler = run_assistant(
            client, openai_thread_id=thread_id, openai_assistant_id=assistant_id
        )
        return event_handler.current_run.id

    # Set django_thread attribute:
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names and hasattr(
            self, request.method.lower()
        ):
            try:
                self.django_thread = Thread.objects.get(openai_id=kwargs["thread_id"])
            except Thread.DoesNotExist:
                return JsonResponse({"error": "Thread not found"}, status=404)
        return super().dispatch(request, *args, **kwargs)

    # List messages in a thread:
    def get(self, request: HttpRequest, *args, **kwargs):
        messages = []
        for message in self.list_thread_messages():
            messages.append(message.to_dict())

        return JsonResponse({"object": "list", "data": messages})

    # Create a message in a thread:
    def post(self, request: HttpRequest, *args, **kwargs):
        if not self.can_create_message(thread=self.django_thread):
            return JsonResponse({"error": "User is not allowed to create messages"}, status=403)
        data = _parse_json(request)
        if not data.get("content"):
            return JsonResponse({"error": "Message content is required"}, status=400)
        if not data.get("assistant_id"):
            return JsonResponse({"error": "OpenAI Assistant ID content is required"}, status=400)

        message = self.create_thread_message(content=data["content"])
        run_id = self.create_run(assistant_id=data["assistant_id"])

        return JsonResponse(
            {
                "message": message.to_dict(),
                "run_id": run_id,
            }
        )
