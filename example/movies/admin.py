from django.contrib import admin
from django.utils.safestring import mark_safe

from movies.models import MovieBacklogItem


@admin.register(MovieBacklogItem)
class MovieBacklogItemAdmin(admin.ModelAdmin):
    list_display = (
        "movie_name",
        "imdb_url_link",
        "imdb_rating",
        "position",
        "user",
        "created_at",
        "updated_at",
    )
    search_fields = ("movie_name", "imdb_url", "user__username", "user__email")
    list_filter = ("user", "created_at", "updated_at")
    list_select_related = ("user",)
    raw_id_fields = ("user",)

    @admin.display(ordering="imdb_url", description="IMDb URL")
    def imdb_url_link(self, obj):
        return mark_safe(f'<a href="{obj.imdb_url}">{obj.imdb_url}</a>')  # noqa: S308
