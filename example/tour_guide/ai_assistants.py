import json

from django.utils import timezone

from django_ai_assistant import AIAssistant, method_tool
from tour_guide.integrations import fetch_points_of_interest


def _tour_guide_example_json():
    return json.dumps(
        {
            "nearby_attractions": [
                {
                    "attraction_name": f"<attraction-{i}-name-here>",
                    "attraction_description": f"<attraction-{i}-description-here>",
                    "attraction_url": f"<attraction-{i}-imdb-page-url-here>",
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


class TourGuideAIAssistant(AIAssistant):
    id = "tour_guide_assistant"  # noqa: A003
    name = "Tour Guide Assistant"
    instructions = (
        "You are a tour guide assistant that offers information about nearby attractions. "
        "The application will capture the user coordinates, and should provide a list of nearby attractions. "
        "Use the available tools to suggest nearby attractions to the user. "
        "You don't need to include all the found items, only include attractions that are relevant for a tourist. "
        "Select the top 10 best attractions for a tourist, if there are less then 10 relevant items only return these. "
        "Order items by the most relevant to the least relevant. "
        "If there are no relevant attractions nearby, just keep the list empty. "
        "Your response will be integrated with a frontend web application therefore it's critical that "
        "it only contains a valid JSON. DON'T include '```json' in your response. "
        "The JSON should be formatted according to the following structure: \n"
        f"\n\n{_tour_guide_example_json()}\n\n\n"
        "In the 'attraction_name' field provide the name of the attraction in english. "
        "In the 'attraction_description' field generate an overview about the attraction with the most important information, "
        "curiosities and interesting facts. "
        "Only include a value for the 'attraction_url' field if you find a real value in the provided data otherwise keep it empty. "
    )
    model = "gpt-4o"

    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()

        return f"Today is: {current_date_str}. {self.instructions}"

    @method_tool
    def get_nearby_attractions_from_api(self, latitude: float, longitude: float) -> dict:
        """Find nearby attractions based on user's current location."""
        return fetch_points_of_interest(
            latitude=latitude,
            longitude=longitude,
            tags=["tourism", "leisure", "place", "building"],
            radius=500,
        )