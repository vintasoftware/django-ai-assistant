from django.urls import include, path

from . import views


urlpatterns = [
    path("ai-assistant/", include("django_ai_assistant.urls")),
    path("htmx/", views.AIAssistantChatHomeView.as_view(), name="chat_home"),
    path(
        "htmx/thread/<int:thread_id>/",
        views.AIAssistantChatThreadView.as_view(),
        name="chat_thread",
    ),
    path("", views.react_index, name="react_index"),
]
