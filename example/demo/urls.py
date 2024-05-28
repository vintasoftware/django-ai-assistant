from django.urls import include, path

from . import views


urlpatterns = [
    path("ai-assistant/", include("django_ai_assistant.urls")),
    path("", views.index, name="index"),
    path("htmx-chat/", views.htmx_chat, name="htmlx_chat"),
]
