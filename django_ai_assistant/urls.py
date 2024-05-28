from django.urls import path

from . import views


urlpatterns = [
    path("assistants/", views.AssistantListView.as_view(), name="assistants-list"),
    path("threads/", views.ThreadListCreateView.as_view(), name="threads-list-create"),
    path(
        "threads/<str:openai_thread_id>/messages/",
        views.ThreadMessageListCreateView.as_view(),
        name="messages-list-create",
    ),
]
