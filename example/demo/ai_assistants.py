from django.utils import timezone

from django_ai_assistant.helpers.assistants import AIAssistant, register_assistant

from .weather import fetch_current_weather, fetch_forecast_weather


@register_assistant
class WeatherAIAssistant(AIAssistant):
    id = "weather_assistant"  # noqa: A003
    name = "Weather Assistant"
    fns = (fetch_current_weather, fetch_forecast_weather)
    model = "gpt-4o"

    def build_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()
        return f"You are a weather bot. Use the provided functions to answer questions. Today is: {current_date_str}."
