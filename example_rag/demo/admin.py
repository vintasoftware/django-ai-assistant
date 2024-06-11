from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import DjangoDocPage


@admin.register(DjangoDocPage)
class DjangoDocPageAdmin(admin.ModelAdmin):
    list_display = ("path", "django_docs_url")
    search_fields = ("path",)

    def django_docs_url(self, obj):
        return mark_safe(f'<a href="{obj.django_docs_url}">{obj.django_docs_url}</a>')  # noqa: S308

    django_docs_url.short_description = "Django Docs URL"
