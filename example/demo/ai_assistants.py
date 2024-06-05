from typing import Sequence

from django.utils import timezone

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from firecrawl import FirecrawlApp
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import BaseTool

from django_ai_assistant.helpers.assistants import AIAssistant, register_assistant
from django_ai_assistant.tools import tool


BASE_URL = "https://api.weatherapi.com/v1/"
TIMEOUT = 10


# @register_assistant
# class WeatherAIAssistant(AIAssistant):
#     id = "weather_assistant"  # noqa: A003
#     description = "A weather assistant that provides weather information."
#     name = "Weather Assistant"
#     model = "gpt-4o"

#     @tool
#     def fetch_current_weather(self, location: str) -> dict:
#         """Fetch the current weather data for a location"""

#         response = requests.get(
#             f"{BASE_URL}current.json",
#             params={
#                 "key": settings.WEATHER_API_KEY,
#                 "q": location,
#             },
#             timeout=TIMEOUT,
#         )
#         return response.json()

#     class FetchForecastWeatherInput(BaseModel):
#         location: str
#         dt_str: str = Field(description="Date in the format 'YYYY-MM-DD'")

#     @tool(args_schema=FetchForecastWeatherInput)
#     def fetch_forecast_weather(self, location: str, dt_str: str) -> dict:
#         """Fetch the forecast weather data for a location"""

#         response = requests.get(
#             f"{BASE_URL}forecast.json",
#             params={
#                 "key": settings.WEATHER_API_KEY,
#                 "q": location,
#                 "days": 14,
#                 "dt": dt_str,
#             },
#             timeout=TIMEOUT,
#         )
#         return response.json()

#     @tool
#     def who_am_i(self) -> str:
#         """Return the username of the current user"""
#         if self._user:
#             return self._user.username
#         else:
#             return "Anonymous"

#     def get_instructions(self):
#         # Warning: this will use the server's timezone
#         # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
#         # In a real application, you should use the user's timezone
#         current_date_str = timezone.now().date().isoformat()
#         return f"You are a weather bot. Use the provided functions to answer questions. Today is: {current_date_str}."


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
    id = "movie_recommendation_assistant"
    description = "A movie recommendation assistant."
    instructions = (
        "You're a helpful movie recommendation assistant. "
        "Research for upcoming movies and get more information about any movies "
        "by using the provided functions."
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


@register_assistant
class GameRecommendationAIAssistant(AIAssistant):
    id = "game_recommendation_assistant"
    description = "A game recommendation assistant."
    instructions = (
        "You're a helpful game recommendation assistant. "
        "Research for upcoming games and get more information about any games "
        "by using the provided functions."
    )
    name = "Game Recommendation Assistant"
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
