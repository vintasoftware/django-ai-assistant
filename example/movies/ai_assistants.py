import threading
import time
from typing import Sequence

from django.conf import settings
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

import requests
from langchain_community.tools import BraveSearch
from langchain_core.tools import BaseTool

from django_ai_assistant import AIAssistant, method_tool
from movies.models import MovieBacklogItem


brave_search_lock = threading.Lock()


class RateLimitedBraveSearch(BraveSearch):
    def _run(self, query: str, **kwargs) -> str:
        """Use the tool."""

        # brave_search_lock is necessary to ensure 1 request/second,
        # due to free plan limitations of Brave Search API:
        try:
            brave_search_lock.acquire(timeout=10)
            start_time = time.time()
            result = self.search_wrapper.run(query)
            elapsed_time = time.time() - start_time
            if 1 - elapsed_time > 0:
                time.sleep(1 - elapsed_time + 0.2)  # sleep plus some jitter
            return result
        finally:
            brave_search_lock.release()


# Note this assistant is not registered, but we'll use it as a tool on the other.
# This one shouldn't be used directly, as it does web searches and scraping.
class IMDbScraper(AIAssistant):
    id = "imdb_scraper"  # noqa: A003
    instructions = (
        "You're a function to find the IMDb URL of a given movie, "
        "and scrape this URL to get the movie rating and other information.\n"
        "Use the search function to find the IMDb URL. "
        "Make search queries like:\n"
        "- IMDb page of <queried movie here>\n"
        "Then check results, scrape the IMDb URL, process the page, and produce an output like this: \n"
        "- IMDb URL: ...\n"
        "- IMDb Rating: ...\n"
        "- IMDb Page: <Markdown content of the IMDb page>"
    )
    name = "IMDb Scraper"
    model = "gpt-4o-mini"
    tool_max_concurrency = 4

    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()
        return f"{self.instructions}.\n Today is: {current_date_str}."

    @method_tool
    def scrape_imdb_url(self, url: str) -> str:
        """Scrape the IMDb URL and return the content as Markdown."""
        return requests.get(
            "https://r.jina.ai/" + url,
            headers={
                "Authorization": "Bearer " + settings.JINA_API_KEY,
            },
            timeout=20,
        ).text[:30000]

    def get_tools(self) -> Sequence[BaseTool]:
        return [
            RateLimitedBraveSearch.from_api_key(
                api_key=settings.BRAVE_SEARCH_API_KEY, search_kwargs={"count": 5}
            ),
            *super().get_tools(),
        ]


class MovieRecommendationAIAssistant(AIAssistant):
    id = "movie_recommendation_assistant"  # noqa: A003
    instructions = (
        "You're a helpful movie recommendation assistant. "
        "Use the provided functions to answer queries and run operations.\n"
        "Use the search function to find movie recommendations based on user's query.\n"
        "Then, use the IMDb Scraper to get the IMDb URL and rating of the movies you're recommending. "
        "Both the IMDb URL and rating are necessary to add a movie to the user's backlog. "
        "Note the backlog is stored in a DB. "
        "When managing the backlog, you must call the functions, to keep your answers in sync with the DB. "
        "The backlog has an order, and you should respect it. Call `reorder_backlog` when necessary.\n"
        "When showing the backlog, show the movies in the order they are stored in the DB, "
        "and include the IMDb URL and rating.\n"
        "Ask the user if they want to add your recommended movies to their backlog.\n"
        "User may talk to you in any language. Respond with the same language, "
        "but refer to movies and call functions with their English name.\n"
        "Do not include images in your response."
    )
    name = "Movie Recommendation Assistant"
    model = "gpt-4o-mini"
    tool_max_concurrency = 4

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
            RateLimitedBraveSearch.from_api_key(
                api_key=settings.BRAVE_SEARCH_API_KEY, search_kwargs={"count": 5}
            ),
            IMDbScraper().as_tool(
                description="IMDb Scraper to get the IMDb data a given movie. "
                "Given a movie name (in English), "
                "finds the movie URL, rating, and scrapes the IMDb page (as Markdown)."
            ),
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
        """
        Add a movie to user's backlog. Must pass the movie_name, imdb_url, and imdb_rating.
        Set imdb_rating to 0.0 if not available.
        """

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
