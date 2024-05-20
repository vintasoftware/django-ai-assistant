from django.urls import path

from . import views


urlpatterns = [
    path("threads/", views.AssistantThreadListCreateView.as_view(), name="threads-list-create"),
    path(
        "threads/<str:thread_id>/messages/",
        views.AssistantThreadMessageListCreateView.as_view(),
        name="messages-list-create",
    ),
]
