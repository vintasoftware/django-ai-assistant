from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.base import TemplateView

from pydantic import ValidationError

from django_ai_assistant.helpers.assistants import (
    create_message,
    create_thread,
    get_thread_messages,
    get_threads,
)
from django_ai_assistant.models import Thread
from django_ai_assistant.schemas import (
    ThreadMessagesSchemaIn,
    ThreadSchemaIn,
)

from .ai_assistants import MovieRecommendationAIAssistant


def react_index(request):
    return render(request, "demo/react_index.html")


class BaseAIAssistantView(TemplateView):
    def get_assistant_id(self, **kwargs):
        """Returns the MovieRecommendationAIAssistant. Replace this with your own logic."""
        return MovieRecommendationAIAssistant.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        threads = list(get_threads(user=self.request.user, request=self.request, view=None))
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
            thread_data = ThreadSchemaIn(**request.POST)
        except ValidationError:
            messages.error(request, "Invalid thread data")
            return redirect("chat_home")

        thread = create_thread(name=thread_data.name, user=request.user, request=request, view=None)
        return redirect("chat_thread", thread_id=thread.id)


class AIAssistantChatThreadView(BaseAIAssistantView):
    template_name = "demo/chat_thread.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        thread_messages = get_thread_messages(
            thread_id=self.kwargs["thread_id"],
            user=self.request.user,
            request=self.request,
            view=None,
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
            message = ThreadMessagesSchemaIn(
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
            view=None,
        )
        return redirect("chat_thread", thread_id=thread_id)
