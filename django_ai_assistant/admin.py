from typing import ClassVar, List, Type

from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe

from django_ai_assistant.models import Message, Thread


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ("pk", "message_type", "content", "created_at")
    readonly_fields = fields
    ordering = ("created_at",)
    show_change_link = True

    def pk(self, obj):
        display_text = "<a href={}>{}</a>".format(
            reverse(
                f"admin:{Message._meta.app_label}_{Message._meta.model_name}_change", args=(obj.pk,)
            ),
            obj.pk,
        )
        return mark_safe(display_text)  # noqa: S308

    def message_type(self, obj):
        return obj.message.get("type") if obj.message else None

    def content(self, obj):
        return obj.message.get("data", {}).get("content") if obj.message else None

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "created_by", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    raw_id_fields = ("created_by",)
    inlines: ClassVar[List[Type[InlineModelAdmin]]] = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "created_at")
    search_fields = ("thread__name", "message")
    list_filter = ("created_at",)
    raw_id_fields = ("thread",)
