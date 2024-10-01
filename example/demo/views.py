from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic.base import TemplateView

from pydantic import ValidationError
from tour_guide.ai_assistants import TourGuideAIAssistant
from weather.ai_assistants import WeatherAIAssistant

from django_ai_assistant.api.schemas import (
    ThreadIn,
    ThreadMessageIn,
)
from django_ai_assistant.helpers.use_cases import (
    create_message,
    create_thread,
    get_thread_messages,
    get_threads,
)
from django_ai_assistant.models import Thread


def react_index(request, **kwargs):
    return render(request, "demo/react_index.html")


class BaseAIAssistantView(TemplateView):
    def get_assistant_id(self, **kwargs):
        """Returns the WeatherAIAssistant. Replace this with your own logic."""
        return WeatherAIAssistant.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        threads = list(get_threads(user=self.request.user))
        context.update(
            {
                "assistant_id": self.get_assistant_id(**kwargs),
                "threads": threads,
            }
        )
        return context


class AIAssistantChatHomeView(BaseAIAssistantView):
    template_name = "demo/chat_home.html"

    # POST to create thread:
    def post(self, request, *args, **kwargs):
        try:
            thread_data = ThreadIn(**request.POST)
        except ValidationError:
            messages.error(request, "Invalid thread data")
            return redirect("chat_home")

        thread = create_thread(
            name=thread_data.name,
            user=request.user,
            request=request,
        )
        return redirect("chat_thread", thread_id=thread.id)


class AIAssistantChatThreadView(BaseAIAssistantView):
    template_name = "demo/chat_thread.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread_id = self.kwargs["thread_id"]
        thread = get_object_or_404(Thread, id=thread_id)

        thread_messages = get_thread_messages(
            thread=thread,
            user=self.request.user,
            request=self.request,
        )
        context.update(
            {
                "thread_id": self.kwargs["thread_id"],
                "thread_messages": thread_messages,
            }
        )
        return context

    # POST to create message:
    def post(self, request, *args, **kwargs):
        assistant_id = self.get_assistant_id()
        thread_id = self.kwargs["thread_id"]
        thread = get_object_or_404(Thread, id=thread_id)

        try:
            message = ThreadMessageIn(
                assistant_id=assistant_id,
                content=request.POST.get("content") or None,
            )
        except ValidationError:
            messages.error(request, "Invalid message data")
            return redirect("chat_thread", thread_id=thread_id)

        create_message(
            assistant_id=assistant_id,
            thread=thread,
            user=request.user,
            content=message.content,
            request=request,
        )
        return redirect("chat_thread", thread_id=thread_id)


class TourGuideAssistantView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in to use this feature."}, status=401)

        coordinates = request.GET.get("coordinate")

        if not coordinates:
            return JsonResponse({})

        a = TourGuideAIAssistant()
        data = a.run(f"My coordinates are: ({coordinates})")
        return JsonResponse(data.model_dump())
