from django.conf import settings
from django.db import models
from django.db.models import F, Index


class MovieBacklogItem(models.Model):
    movie_name = models.CharField(max_length=255)
    imdb_url = models.URLField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recommended_movies",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Movie Backlog Item"
        verbose_name_plural = "Movie Backlog Items"
        ordering = ("user", "-created_at")
        indexes = (Index(F("created_at").desc(), name="movie_item_created_at_desc"),)

    def __str__(self):
        return f"{self.movie_name} - {self.user}"

    def __repr__(self) -> str:
        return f"<MovieBacklogItem {self.movie_name} of {self.user}>"
