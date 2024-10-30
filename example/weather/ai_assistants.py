from datetime import date

from django.conf import settings
from django.utils import timezone
from langchain_ollama import ChatOllama

import requests

from django_ai_assistant import AIAssistant, BaseModel, Field, method_tool

BASE_URL="http://127.0.0.1:11434"
API_URL = "https://api.weatherapi.com/v1/"
TIMEOUT = 10


class WeatherAIAssistant(AIAssistant):
    id = "weather_assistant"
    name = "Weather Assistant"
    instructions = "You are a weather bot."
    model = "llama3.1"

    def get_llm(self):
        model = self.get_model()
        temperature = self.get_temperature()
        model_kwargs = self.get_model_kwargs()
        return ChatOllama(
            model_name=model,
            temperature=temperature,
            model_kwargs=model_kwargs,
            timeout=None,
            max_retries=2,
        )
        
    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()
        return f"I am a weather bot. Use the provided functions to answer questions. Today is: {current_date_str}."

    @method_tool
    def fetch_current_weather(self, location: str) -> dict:
        """Fetch the current weather data for a location"""

        response = requests.get(
            f"{API_URL}current.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
            },
            timeout=TIMEOUT,
        )
        return response.json()

    class FetchForecastWeatherInput(BaseModel):
        location: str = Field(description="Location to fetch the forecast weather for")
        forecast_date: date = Field(description="Date in the format 'YYYY-MM-DD'")

    @method_tool(args_schema=FetchForecastWeatherInput)
    def fetch_forecast_weather(self, location, forecast_date) -> dict:
        """Fetch the forecast weather data for a location"""

        response = requests.get(
            f"{API_URL}forecast.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
                "days": 14,
                "dt": forecast_date.isoformat(),
            },
            timeout=TIMEOUT,
        )
        return response.json()

    @method_tool
    def who_am_i(self) -> str:
        """Return the username of the current user"""
        if self._user:
            return self._user.username
        else:
            return "Anonymous"
