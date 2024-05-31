from django.urls import include, path

from . import views


urlpatterns = [
    path("ai-assistant/", include("django_ai_assistant.urls")),
    path("", views.react_index, name="react_index"),
    path("htmx/", views.htmx_index, name="htmx_index"),
    path("htmx/thread/<int:thread_id>/", views.htmx_index, name="htmx_thread_detail"),
]
