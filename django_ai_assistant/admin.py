from django.contrib import admin

from .models import Assistant, Thread


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = ("name", "openai_id", "created_at", "updated_at")
    search_fields = ("name", "openai_id")
    list_filter = ("created_at", "updated_at")


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("name", "openai_id", "created_at", "created_by", "updated_at")
    search_fields = ("name", "openai_id")
    list_filter = ("created_at", "updated_at")
    raw_id_fields = ("created_by",)
