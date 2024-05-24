from django.conf import settings

import requests
from pydantic import Field


BASE_URL = "https://api.weatherapi.com/v1/"
TIMEOUT = 10


def fetch_current_weather(location: str) -> dict:
    """Fetch the current weather data for a location"""

    response = requests.get(
        f"{BASE_URL}current.json",
        params={
            "key": settings.WEATHER_API_KEY,
            "q": location,
        },
        timeout=TIMEOUT,
    )
    return response.json()


def fetch_forecast_weather(
    location: str, dt_str: str = Field(description="Date in the format 'YYYY-MM-DD'")
):
    """Fetch the forecast weather data for a location"""

    response = requests.get(
        f"{BASE_URL}forecast.json",
        params={
            "key": settings.WEATHER_API_KEY,
            "q": location,
            "days": 14,
            "dt": dt_str,
        },
        timeout=TIMEOUT,
    )
    return response.json()
