from typing import List

import requests


def fetch_points_of_interest(
    latitude: float, longitude: float, tags: List[str], radius: int = 500
) -> dict:
    """
    Fetch points of interest from OpenStreetMap using Overpass API.

    :param latitude: Latitude of the center point.
    :param longitude: Longitude of the center point.
    :param radius: Radius in meters to search for POIs around the center point.
    :param tags: A list of OpenStreetMap tags to filter the POIs (e.g., ["amenity", "tourism"]).
    :return: A list of POIs with their details.
    """
    # Base URL for the Overpass API
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Construct the Overpass QL (query language) query
    pois_query = "".join(
        [
            (
                f"node[{tag}](around:{radius},{latitude},{longitude});"
                f"way[{tag}](around:{radius},{latitude},{longitude});"
            )
            for tag in tags
        ]
    )

    query = f"""
    [out:json];
    (
        {pois_query}
    );
    out tags;
    """

    response = requests.get(overpass_url, params={"data": query}, timeout=10)

    response.raise_for_status()

    data = response.json()
    return data["elements"]
