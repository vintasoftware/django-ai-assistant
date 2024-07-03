import json
import requests
from typing import Sequence

from osmapi import OsmApi

from django.utils import timezone

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import BaseTool

from django_ai_assistant import AIAssistant, method_tool


# # Note this assistant is not registered, but we'll use it as a tool on the other.
# # This one shouldn't be used directly, as it does web searches and scraping.
# class OpenStreetMapsAPITool(AIAssistant):
#     id = "open_street_maps_api_tool"  # noqa: A003
#     instructions = (
#         "You're a tool to find the nearby attractions of a given location. "
#         "Use the Open Street Maps API to find nearby attractions around the location, up to a 500m diameter from the point. "
#         "Then check results and provide only the nearby attractions and their details to the user."
#     )
#     name = "Open Street Maps API Tool"
#     model = "gpt-4o"

#     def get_instructions(self):
#         # Warning: this will use the server's timezone
#         # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
#         # In a real application, you should use the user's timezone
#         current_date_str = timezone.now().date().isoformat()
#         return f"{self.instructions} Today is: {current_date_str}."


def _tour_guide_example_json():
    return json.dumps(
        {
            "nearby_attractions": [
                {
                    "attraction_name": f"<attraction-{i}-name-here>",
                    "attraction_description": f"<attraction-{i}-short-description-here>",
                    "attraction_image_url": f"<attraction-{i}-image-url-here>",
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
        "The user is at a location, passed as a combination of latitude and longitude, and wants to know what to learn about nearby attractions. "
        "Use the available tools to suggest nearby attractions to the user. "
        "If there are no interesting attractions nearby, "
        "tell the user there's nothing to see where they're at. "
        "Use three sentences maximum and keep your suggestions concise."
        "Your response will be integrated with a frontend web application,"
        "therefore it's critical to reply with only JSON output in the following structure: \n"
        f"```json\n{_tour_guide_example_json()}\n```"
    )
    model = "gpt-4o"

    def get_instructions(self):
        # Warning: this will use the server's timezone
        # See: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        # In a real application, you should use the user's timezone
        current_date_str = timezone.now().date().isoformat()

        return "\n".join(
            [
                self.instructions,
                f"Today is: {current_date_str}",
                f"The user's current location, considering latitude and longitude is: {self.get_user_location()}",
            ]
        )

    def get_tools(self) -> Sequence[BaseTool]:
        return [
            TavilySearchResults(),
            # OpenStreetMapsAPITool().as_tool(description="Tool to query the Open Street Maps API for location information."),
            *super().get_tools(),
        ]

    @method_tool
    def get_user_location(self) -> dict:
        """Get user's current location."""
        return {"lat": "X", "lon": "Y"} # replace with actual coordinates
    
    @method_tool
    def get_nearby_attractions_from_api(self) -> dict:
        api = OsmApi()
        """Get nearby attractions based on user's current location."""
        return {}
