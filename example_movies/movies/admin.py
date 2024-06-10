from django.contrib import admin

from .models import MovieBacklogItem


@admin.register(MovieBacklogItem)
class MovieBacklogItemAdmin(admin.ModelAdmin):
    list_display = (
        "movie_name",
        "imdb_url",
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
