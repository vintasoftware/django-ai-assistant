from django.contrib import admin

from issue_tracker.models import Issue


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignee",
        "created_at",
        "updated_at",
    )
    search_fields = ("id", "title", "description", "assignee__username", "assignee__email")
    list_filter = ("assignee", "created_at", "updated_at")
    raw_id_fields = ("assignee",)
