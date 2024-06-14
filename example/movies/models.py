from django.conf import settings
from django.db import models, transaction


class MovieBacklogItem(models.Model):
    movie_name = models.CharField(max_length=255)
    imdb_url = models.URLField()
    imdb_rating = models.FloatField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="movie_backlog",
    )
    position = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Movie Backlog Item"
        verbose_name_plural = "Movie Backlog Items"
        ordering = ("user", "position")
        unique_together = (("user", "imdb_url"),)

    def __str__(self):
        return f"{self.movie_name} - {self.user}"

    def __repr__(self) -> str:
        return f"<MovieBacklogItem {self.movie_name} of {self.user}>"

    @classmethod
    def reorder_backlog(cls, user, imdb_url_list=None):
        with transaction.atomic():
            if imdb_url_list is None:
                item_list = list(
                    MovieBacklogItem.objects.filter(user=user).order_by("user", "position")
                )
            else:
                item_qs = MovieBacklogItem.objects.filter(user=user, imdb_url__in=imdb_url_list)
                item_order_dict = {imdb_url: idx for idx, imdb_url in enumerate(imdb_url_list)}
                item_list = sorted(item_qs, key=lambda item: item_order_dict[item.imdb_url])

            for position, item in enumerate(item_list, start=1):
                item.position = position
            MovieBacklogItem.objects.bulk_update(item_list, fields=["position"])
