from django.urls import include, path

from demo import views


urlpatterns = [
    path("ai-assistant/", include("django_ai_assistant.urls")),
    path("htmx/", views.AIAssistantChatHomeView.as_view(), name="chat_home"),
    path(
        "htmx/thread/<int:thread_id>/",
        views.AIAssistantChatThreadView.as_view(),
        name="chat_thread",
    ),
    path(
        "tour-guide/",
        views.TourGuideAssistantView.as_view(),
        name="tour_guide",
    ),
    # Catch all for react app:
    path("", views.react_index, {"resource": ""}),
    path("<path:resource>", views.react_index),
]
