from django.urls import path

from . import api, views


urlpatterns = [
    path("", api.api.urls),
    path("assistants/", views.AssistantListView.as_view(), name="assistants-list"),
    path("threads/", views.ThreadListCreateView.as_view(), name="threads-list-create"),
    path(
        "threads/<str:openai_thread_id>/messages/",
        views.ThreadMessageListCreateView.as_view(),
        name="messages-list-create",
    ),
]
