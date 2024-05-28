import json

from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from openai import OpenAI

from django_ai_assistant.exceptions import AIUserNotAllowedError

from .conf import settings
from .helpers.assistants import (
    assistants_generator,
    create_thread,
    create_thread_message_as_user,
    run_assistant_as_user,
    thread_messages_generator,
    threads_generator,
)
from .models import Assistant, Thread


def _parse_json(request: HttpRequest) -> dict:
    try:
        if request.body:
            return json.loads(request.body)
        else:
            return {}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON data"}


class BaseAssistantView(View):
    def _get_default_kwargs(self):
        return {
            "request": self.request,
            "user": self.request.user,
            "view": self,
        }

    def get_ai_client(self) -> OpenAI:
        return settings.call_fn(
            "CLIENT_INIT_FN",
            **self._get_default_kwargs(),
        )

    # Validate if user is authenticated:
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=403)
        return super().dispatch(request, *args, **kwargs)


class AssistantListView(BaseAssistantView):
    def get(self, request: HttpRequest, *args, **kwargs):
        assistants_data = [
            {
                "openai_id": a.openai_id,
                "name": a.name,
                "created_at": a.created_at.isoformat(),
                "updated_at": a.updated_at.isoformat(),
            }
            for a in assistants_generator(user=self.request.user, request=self.request, view=self)
        ]
        return JsonResponse({"object": "list", "data": assistants_data})


class ThreadListCreateView(BaseAssistantView):
    def get_default_thread_name(self, data: dict) -> str:
        return timezone.now().strftime("%Y-%m-%d %H:%M")

    def get_threads_data(self):
        return [
            {
                "openai_id": t.openai_id,
                "name": t.name,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat(),
            }
            for t in threads_generator(user=self.request.user, request=self.request, view=self)
        ]

    def get(self, request: HttpRequest, *args, **kwargs):
        threads_data = self.get_threads_data()
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            return render(request, "threads/list.html", {"threads": threads_data})
        return JsonResponse({"object": "list", "data": threads_data})

    def post(self, request: HttpRequest, *args, **kwargs):
        data = _parse_json(request)
        if "error" in data:
            return JsonResponse(data, status=400)

        name = data.get("name", self.get_default_thread_name(data))
        try:
            _, openai_thread = create_thread(
                name=name, user=self.request.user, request=self.request, view=self
            )
        except AIUserNotAllowedError as e:
            return JsonResponse({"error": str(e)}, status=403)
        accept = request.headers.get("Accept", "")

        if "text/html" in accept:
            threads_data = self.get_threads_data()
            return render(request, "threads/list.html", {"threads": threads_data})
        return JsonResponse(openai_thread.to_dict())


class ThreadMessageListCreateView(BaseAssistantView):
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Thread.DoesNotExist:
            return JsonResponse({"error": "Thread not found"}, status=404)
        except Assistant.DoesNotExist:
            return JsonResponse({"error": "Assistant not found"}, status=404)

    def get_messages_data(self):
        messages_data = []
        for message in thread_messages_generator(
            openai_thread_id=self.kwargs["openai_thread_id"],
            user=self.request.user,
            request=self.request,
            view=self,
        ):
            messages_data.append(message.to_dict())
        return messages_data

    # List messages in a thread:
    def get(self, request: HttpRequest, *args, **kwargs):
        messages_data = self.get_messages_data()

        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            return render(request, "messages/list.html", {"messages": messages_data})

        return JsonResponse({"object": "list", "data": messages_data})

    # Create a message in a thread:
    def post(self, request: HttpRequest, *args, **kwargs):
        data = _parse_json(request)
        if "error" in data:
            return JsonResponse(data, status=400)
        if not data.get("content"):
            return JsonResponse({"error": "Message content is required"}, status=400)
        if not data.get("assistant_id"):
            return JsonResponse({"error": "OpenAI Assistant ID is required"}, status=400)

        assistant = Assistant.objects.get(openai_id=data["assistant_id"])
        thread = Thread.objects.get(openai_id=self.kwargs["openai_thread_id"])
        message = create_thread_message_as_user(
            openai_thread_id=self.kwargs["openai_thread_id"],
            content=data["content"],
            user=self.request.user,
            request=self.request,
            view=self,
        )
        run_assistant_as_user(
            assistant=assistant,
            thread=thread,
            user=self.request.user,
            request=self.request,
            view=self,
        )

        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            messages_data = self.get_messages_data()
            return render(
                request,
                "messages/list.html",
                {"messages": messages_data},
            )

        return JsonResponse({"message": message.to_dict()})
