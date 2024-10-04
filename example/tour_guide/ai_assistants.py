import json

from django.utils import timezone

from pydantic import BaseModel, Field

from django_ai_assistant import AIAssistant, method_tool
from tour_guide.integrations import fetch_points_of_interest


class Attraction(BaseModel):
    name: str = Field(description="The name of the attraction in english")
    description: str = Field(
        description="The description of the attraction, provide information in an entertaining way"
    )


class TourGuide(BaseModel):
    nearby_attractions: list[Attraction] = Field(description="The list of nearby attractions")


class TourGuideAIAssistant(AIAssistant):
    id = "tour_guide_assistant"  # noqa: A003
    name = "Tour Guide Assistant"
    instructions = (
        "You are a tour guide assistant that offers information about nearby attractions. "
        "You will receive the user coordinates and should use available tools to find nearby attractions. "
        "Only include in your response the items that are relevant to a tourist visiting the area. "
        "Only call the find_nearby_attractions tool once. "
    )
    model = "gpt-4o-mini"
    structured_output = TourGuide

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
