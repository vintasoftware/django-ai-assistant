from typing import Sequence

from django.utils import timezone

from firecrawl import FirecrawlApp
from langchain_community.tools import WikipediaQueryRun
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import BaseTool

from django_ai_assistant.helpers.assistants import AIAssistant, register_assistant
from django_ai_assistant.tools import tool

from .models import MovieBacklogItem


# Note this assistant is not registered, but we'll use it as a tool on the other.
# This one shouldn't be used direclty, as it do web searches and scraping.
class IMDBURLFinderTool(AIAssistant):
    id = "imdb_url_finder"  # noqa: A003
    description = "A tool that finds the IMDB URL of a given movie."
    instructions = (
        "You're a tool to find the IMDB URL of a given movie. "
        "Use the Tavily Search API to find the IMDB URL. "
        "Make search queries like: \n"
        "- IMDB page of The Matrix\n"
        "- IMDB page of The Godfather\n"
        "- IMDB page of The Shawshank Redemption\n"
        "Then check results and provide only the IMDB URL to the user."
    )
    name = "IMDB URL Finder"
    model = "gpt-4o"

    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()
        return f"{self.instructions} Today is: {current_date_str}."

    def get_tools(self) -> Sequence[BaseTool]:
        return [
            TavilySearchResults(),
            *super().get_tools(),
        ]


@register_assistant
class MovieRecommendationAIAssistant(AIAssistant):
    id = "movie_recommendation_assistant"  # noqa: A003
    description = "A movie recommendation assistant."
    instructions = (
        "You're a helpful movie recommendation assistant. "
        "Help users find movies to watch and manage their movie backlogs. "
        "By using the provided tools, you can:\n"
        "- Research for upcoming movies\n"
        "- Research for similar movies\n"
        "- Research more information about movies\n"
        "- List what movies are on user's backlog\n"
        "- Check if a movie is already in user's backlog\n"
        "- Add a movie to user's backlog\n"
        "- Remove a movie to user's backlog\n"
        "- Get the IMDB URL of a movie\n"
        "You must carefully follow the step-by-step below to provide the best experience to the user.\n"
        "When the user asks for a movie recommendation, "
        "or asks about a movie, do the following in order:\n"
        "1. Get the movie IMDB URL using the imdb_url_finder. \n"
        "2. Check if the movie is already in user's backlog. Use the IMDB URL for that. \n"
        "3. Only after you find out if the movie is in user's backlog, offer the user to add it, in case it's not. \n"
    )
    name = "Movie Recommendation Assistant"
    model = "gpt-4o"

    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()
        return f"{self.instructions} Today is: {current_date_str}."

    def get_tools(self) -> Sequence[BaseTool]:
        return [
            TavilySearchResults(),
            WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),  # type: ignore[call-arg]
            IMDBURLFinderTool().as_tool(),
            *super().get_tools(),
        ]

    @tool
    def firecrawl_scrape_url(self, url: str) -> str:
        """Visit the provided website URL and return the content as markdown."""

        firecrawl_app = FirecrawlApp()
        response = firecrawl_app.scrape_url(
            url=url,
            params={
                "pageOptions": {
                    "onlyMainContent": True,
                    "waitFor": 1000,
                },
            },
        )
        return response["markdown"]

    @tool
    def list_movies_backlog(self) -> str:
        """List what movies are on user's backlog."""

        movies = MovieBacklogItem.objects.filter(user=self._user)
        return (
            "\n".join([f"- [{movie.movie_name}]({movie.imdb_url})" for movie in movies]) or "Empty"
        )

    @tool
    def is_movie_in_backlog(self, imdb_url: str) -> str:
        """Check if a movie is in user's backlog. To get the IMDB URL, use the imdb_url_finder."""

        is_in_backlog = MovieBacklogItem.objects.filter(
            imdb_url=imdb_url.strip(),
            user=self._user,
        ).exists()
        if is_in_backlog:
            return "Yes."
        return "No."

    @tool
    def add_movie_to_backlog(self, movie_name: str, imdb_url: str) -> str:
        """Add a movie to user's backlog. To get the IMDB URL, use the imdb_url_finder."""

        MovieBacklogItem.objects.update_or_create(
            movie_name=movie_name.strip(),
            imdb_url=imdb_url.strip(),
            user=self._user,
        )
        return f"Added {movie_name} to {self._user} backlog."

    @tool
    def remove_movie_from_backlog(self, movie_name: str) -> str:
        """Remove a movie from user's backlog."""

        MovieBacklogItem.objects.filter(
            movie_name=movie_name.strip(),
            user=self._user,
        ).delete()
        return f"Removed {movie_name} to {self._user} backlog."
