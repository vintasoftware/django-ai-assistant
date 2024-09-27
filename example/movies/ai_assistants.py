from typing import Sequence

from django.conf import settings
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

import requests
from langchain_community.tools import BraveSearch
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from django_ai_assistant import AIAssistant, method_tool
from movies.models import MovieBacklogItem


class IMDbMovie(BaseModel):
    imdb_url: str
    imdb_rating: float
    scrapped_imdb_page_markdown: str


# Note this assistant is not registered, but we'll use it as a tool on the other.
# This one shouldn't be used directly, as it does web searches and scraping.
class IMDbScraper(AIAssistant):
    id = "imdb_scraper"  # noqa: A003
    instructions = (
        "You're a tool to find the IMDb URL of a given movie, "
        "and scrape this URL to get the movie rating and other information.\n"
        "Use the search tool to find the IMDb URL. "
        "Make search queries like: \n"
        "- IMDb page of The Matrix\n"
        "- IMDb page of The Godfather\n"
        "- IMDb page of The Shawshank Redemption\n"
        "Then check results, scape the IMDb URL, process the page, and produce a JSON output."
    )
    name = "IMDb Scraper"
    model = "gpt-4o"
    structured_output = IMDbMovie

    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()
        return f"{self.instructions} Today is: {current_date_str}."

    @method_tool
    def scrape_imdb_url(self, url: str) -> str:
        """Scrape the IMDb URL and return the content as markdown."""
        return requests.get("https://r.jina.ai/" + url, timeout=20).text[:10000]

    def get_tools(self) -> Sequence[BaseTool]:
        return [
            BraveSearch.from_api_key(
                api_key=settings.BRAVE_SEARCH_API_KEY, search_kwargs={"count": 5}
            ),
            *super().get_tools(),
        ]


class MovieRecommendationAIAssistant(AIAssistant):
    id = "movie_recommendation_assistant"  # noqa: A003
    instructions = (
        "You're a helpful movie recommendation assistant. "
        "Help the user find movies to watch and manage their movie backlogs. "
        "Use the provided tools for that.\n"
        "Note the backlog is stored in a DB. "
        "When managing the backlog, you must call the tools, to keep the sync with the DB. "
        "The backlog has an order, and you should respect it. Call `reorder_backlog` when necessary.\n"
        "Include the IMDb URL and rating of the movies when displaying the backlog.\n"
        "Ask the user if they want to add your recommended movies to their backlog, "
        "but only if the movie is not on the user's backlog yet."
    )
    name = "Movie Recommendation Assistant"
    model = "gpt-4o"

    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()
        user_backlog_str = self.get_movies_backlog()

        return "\n".join(
            [
                self.instructions,
                f"Today is: {current_date_str}",
                f"User's backlog: {user_backlog_str}",
            ]
        )

    def get_tools(self) -> Sequence[BaseTool]:
        return [
            BraveSearch.from_api_key(
                api_key=settings.BRAVE_SEARCH_API_KEY, search_kwargs={"count": 5}
            ),
            IMDbScraper().as_tool(description="Tool to get the IMDb data a given movie."),
            *super().get_tools(),
        ]

    @method_tool
    def get_movies_backlog(self) -> str:
        """Get what movies are on user's backlog."""

        return (
            "\n".join(
                [
                    f"{item.position} - [{item.movie_name}]({item.imdb_url}) - ⭐ {item.imdb_rating}"
                    for item in MovieBacklogItem.objects.filter(user=self._user)
                ]
            )
            or "Empty"
        )

    @method_tool
    def add_movie_to_backlog(self, movie_name: str, imdb_url: str, imdb_rating: float) -> str:
        """Add a movie to user's backlog. Must pass the movie_name, imdb_url, and imdb_rating."""

        with transaction.atomic():
            MovieBacklogItem.objects.update_or_create(
                imdb_url=imdb_url.strip(),
                user=self._user,
                defaults={
                    "movie_name": movie_name.strip(),
                    "imdb_rating": imdb_rating,
                    "position": MovieBacklogItem.objects.filter(user=self._user).aggregate(
                        Max("position", default=0)
                    )["position__max"]
                    + 1,
                },
            )
        return f"Added {movie_name} to backlog."

    @method_tool
    def remove_movie_from_backlog(self, movie_name: str) -> str:
        """Remove a movie from user's backlog."""

        with transaction.atomic():
            MovieBacklogItem.objects.filter(
                user=self._user,
                movie_name=movie_name.strip(),
            ).delete()
            MovieBacklogItem.reorder_backlog(self._user)
        return f"Removed {movie_name} from backlog."

    @method_tool
    def reorder_backlog(self, imdb_url_list: Sequence[str]) -> str:
        """Reorder movies in user's backlog."""

        MovieBacklogItem.reorder_backlog(self._user, imdb_url_list)
        return "Reordered movies in backlog. New backlog: \n" + self.get_movies_backlog()
