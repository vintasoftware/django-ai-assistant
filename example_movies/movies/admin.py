from django.contrib import admin

from .models import MovieBacklogItem


@admin.register(MovieBacklogItem)
class MovieBacklogItemAdmin(admin.ModelAdmin):
    list_display = ("movie_name", "imdb_url", "user", "created_at", "updated_at")
    search_fields = ("movie_name", "imdb_url", "user__username", "user__email")
    list_filter = ("movie_name", "created_at", "updated_at")
    raw_id_fields = ("user",)
