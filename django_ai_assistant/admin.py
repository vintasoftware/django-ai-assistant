from django.contrib import admin

from .models import Message, Thread


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "created_by", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    raw_id_fields = ("created_by",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "created_at", "created_at")
    search_fields = ("thread__name", "message")
    list_filter = ("created_at",)
    list_select_related = ("thread",)
    raw_id_fields = ("thread",)
