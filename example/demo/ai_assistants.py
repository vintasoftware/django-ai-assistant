from django_ai_assistant.helpers.assistants import AIAssistant, register_assistant

from .weather import fetch_current_weather, fetch_forecast_weather


@register_assistant
class WeatherAIAssistant(AIAssistant):
    name = "Weather Assistant"
    instructions = "You are a weather bot. Use the provided functions to answer questions."
    fns = (fetch_current_weather, fetch_forecast_weather)
    model = "gpt-4o"
