from django.urls import path

from django_ai_assistant.api.views import api


urlpatterns = [
    path("", api.urls),
]
