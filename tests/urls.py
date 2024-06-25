from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    # Include django_ai_assistant URLs without prefix to properly generate the OpenAPI client
    path("", include("django_ai_assistant.urls")),
]
