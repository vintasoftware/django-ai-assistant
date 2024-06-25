import json
from typing import Any, Sequence

from django.db.models import Max
from django.utils import timezone

from firecrawl import FirecrawlApp
from langchain_community.tools import WikipediaQueryRun
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import GoogleSerperAPIWrapper, WikipediaAPIWrapper
from langchain_core.tools import BaseTool

from django_ai_assistant import AIAssistant, method_tool
from movies.models import MovieBacklogItem


# Note this assistant is not registered, but we'll use it as a tool on the other.
# This one shouldn't be used directly, as it does web searches and scraping.
class IMDBURLFinderTool(AIAssistant):
    id = "imdb_url_finder"  # noqa: A003
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


class MovieRecommendationAIAssistant(AIAssistant):
    id = "movie_recommendation_assistant"  # noqa: A003
    instructions = (
        "You're a helpful movie recommendation assistant. "
        "Help the user find movies to watch and manage their movie backlogs. "
        "By using the provided tools, you can:\n"
        "- Get the IMDB URL of a movie\n"
        "- Visit the IMDB page of a movie to get its rating\n"
        "- Research for upcoming movies\n"
        "- Research for similar movies\n"
        "- Research more information about movies\n"
        "- Get what movies are on user's backlog\n"
        "- Add a movie to user's backlog\n"
        "- Remove a movie to user's backlog\n"
        "- Reorder movies in user's backlog\n"
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
            TavilySearchResults(),
            WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),  # pyright: ignore[reportCallIssue]
            IMDBURLFinderTool().as_tool(description="Tool to find the IMDB URL of a given movie."),
            *super().get_tools(),
        ]

    @method_tool
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

    @method_tool
    def get_movies_backlog(self) -> str:
        """Get what movies are on user's backlog."""

        return (
            "\n".join(
                [
                    f"{item.position} - [{item.movie_name}]({item.imdb_url}) - Rating {item.imdb_rating}"
                    for item in MovieBacklogItem.objects.filter(user=self._user)
                ]
            )
            or "Empty"
        )

    @method_tool
    def add_movie_to_backlog(self, movie_name: str, imdb_url: str, imdb_rating: float) -> str:
        """Add a movie to user's backlog. Must pass the movie_name, imdb_url, and imdb_rating."""

        MovieBacklogItem.objects.update_or_create(
            imdb_url=imdb_url.strip(),
            user=self._user,
            defaults={
                "movie_name": movie_name.strip(),
                "imdb_rating": imdb_rating,
                "position": MovieBacklogItem.objects.filter(user=self._user).aggregate(
                    Max("position", default=1)
                )["position__max"],
            },
        )
        return f"Added {movie_name} to backlog."

    @method_tool
    def remove_movie_from_backlog(self, movie_name: str) -> str:
        """Remove a movie from user's backlog."""

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


def _movie_recommendation_example_json():
    return json.dumps(
        {
            "recommended_movies": [
                {
                    "movie_name": f"<movie-{i}-name-here>",
                    "movie_description": f"<movie-{i}-short-description-here>",
                    "movie_poster_image_url": f"<movie-{i}-poster-image-url-here>",
                    "imdb_url": f"<movie-{i}-imdb-page-url-here>",
                }
                for i in range(1, 6)
            ]
        },
        indent=2,
    ).translate(  # Necessary due to ChatPromptTemplate
        str.maketrans(
            {
                "{": "{{",
                "}": "}}",
            }
        )
    )


class MovieRecommendationJSONAIAssistant(AIAssistant):
    id = "movie_recommendation_json_assistant"  # noqa: A003
    instructions = (
        "You're a helpful movie recommendation assistant "
        "that outputs valid JSON in a certain structure. "
        "Help the user find movies similar to a given input movie. "
        "The input will be the IMDB page URL of a movie. "
        "By using the provided tools, you can:\n"
        "- Research for similar movies\n"
        "- Research more information about movies\n"
        "- Visit a website URL and return the content as markdown\n"
        "- Check the Wikipedia page of a movie\n"
        "- Get the IMDB page URL of a movie\n"
        "- Get the poster image URL of a movie\n"
        "Your response will be integrated with a frontend web application,"
        "therefore it's critical to reply with only JSON output in the following structure: \n"
        f"```json\n{_movie_recommendation_example_json()}\n```"
    )
    name = "Movie Recommendation JSON Assistant"
    model = "gpt-4o"

    def get_model_kwargs(self):
        return {"response_format": {"type": "json_object"}}

    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()

        return "\n".join(
            [
                self.instructions,
                f"Today is: {current_date_str}",
            ]
        )

    def get_tools(self) -> Sequence[BaseTool]:
        return [
            TavilySearchResults(),
            WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),  # type: ignore[call-arg]
            IMDBURLFinderTool().as_tool(
                description="Tool to find the IMDB page URL of a given movie."
            ),
            *super().get_tools(),
        ]

    def invoke(self, input_dict, thread_id: Any | None, **kwargs):
        input_dict["input"] = input_dict["input"].strip()
        return super().invoke(
            {"input": f"Movies like the movie from this IMDB page: {json.dumps(input_dict)}"},
            thread_id=thread_id,
        )

    @method_tool
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

    @method_tool
    def find_movie_poster_image_url(self, movie_name: str) -> str:
        """Find the poster image URL of a movie."""
        search = GoogleSerperAPIWrapper(type="images")
        results = search.results(movie_name + " poster")
        try:
            return results["images"][0]["imageUrl"]
        except (IndexError, KeyError):
            return "No image found."
