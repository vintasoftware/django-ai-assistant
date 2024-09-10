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
        "You will receive the user coordinates and should use available tools to find nearby attractions. "
        "Only call the find_nearby_attractions tool once. "
        "Your response should only contain valid JSON data. DON'T include '```json' in your response. "
        "The JSON should be formatted according to the following structure: \n"
        f"\n\n{_tour_guide_example_json()}\n\n\n"
        "In the 'attraction_name' field provide the name of the attraction in english. "
        "In the 'attraction_description' field generate an overview about the attraction with the most important information, "
        "curiosities and interesting facts. "
        "Only include a value for the 'attraction_url' field if you find a real value in the provided data otherwise keep it empty. "
    )
    model = "gpt-4o-2024-08-06"

    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()

        return f"Today is: {current_date_str}. {self.instructions}"

    @method_tool
    def find_nearby_attractions(self, latitude: float, longitude: float) -> str:
        """
        Find nearby attractions based on user's current location.
        Returns a JSON with the list of all types of points of interest,
        which may or may not include attractions.
        Calls to this tool are idempotent.
        """
        return json.dumps(
            fetch_points_of_interest(
                latitude=latitude,
                longitude=longitude,
                tags=["tourism", "leisure", "place", "building"],
                radius=500,
            )
        )
