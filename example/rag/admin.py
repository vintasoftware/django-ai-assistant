from django.contrib import admin
from django.utils.safestring import mark_safe

from rag.models import DjangoDocPage


@admin.register(DjangoDocPage)
class DjangoDocPageAdmin(admin.ModelAdmin):
    list_display = ("path", "django_docs_url")
    search_fields = ("path",)

    @admin.display(ordering="path", description="Django Docs URL")
    def django_docs_url(self, obj):
        return mark_safe(f'<a href="{obj.django_docs_url}">{obj.django_docs_url}</a>')  # noqa: S308
