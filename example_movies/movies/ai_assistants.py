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
class ResearcherAIAssistantTool(AIAssistant):
    id = "researcher_assistant"  # noqa: A003
    description = (
        "A researcher assistant that provides a summary when given a topic to research about."
    )
    instructions = (
        "You're a helpful researcher assistant. "
        "Do a research on the topic you'll get as input. "
        "Provide a summary after done with your research, including important and interesting information. "
        "The topic you'll resarch about can be anything: "
        "people, organizations, places, countries, historical events, "
        "cultural artifacts, facts, concepts, etc."
        "Use the provided functions to perform researches."
    )
    name = "Researcher Assistant"
    model = "gpt-4o"

    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()
        return f"{self.instructions} Today is: {current_date_str}."

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

    def get_tools(self) -> Sequence[BaseTool]:
        return [
            TavilySearchResults(),
            WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),  # type: ignore[call-arg]
            *super().get_tools(),
        ]


@register_assistant
class MovieRecommendationAIAssistant(AIAssistant):
    id = "movie_recommendation_assistant"  # noqa: A003
    description = "A movie recommendation assistant."
    instructions = (
        "You're a helpful movie recommendation assistant. "
        "Help users find movies to watch and manage their movie backlogs. "
        "By using the provided functions, you can:\n"
        "- Research for upcoming movies\n"
        "- Research for similar movies\n"
        "- Research more information about any movies\n"
        "- List what movies are on user's backlog\n"
        "- Add a movie to user's backlog\n"
        "- Remove a movie to user's backlog\n"
        "After recommending a movie, ask the user if they want to add it to their backlog."
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
            ResearcherAIAssistantTool().as_tool(),
            *super().get_tools(),
        ]

    @tool
    def list_movies_backlog(self) -> str:
        """List what movies are on user's backlog."""

        movies = MovieBacklogItem.objects.filter(user=self._user)
        return (
            "\n".join([f"- [{movie.movie_name}]({movie.imdb_url})" for movie in movies]) or "Empty"
        )

    @tool
    def add_movie_to_backlog(self, movie_name: str, imdb_url: str) -> str:
        """Add a movie to user's backlog."""

        MovieBacklogItem.objects.create(
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
