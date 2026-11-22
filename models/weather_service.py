
import requests


def get_weather(location):

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    # Handle locations like Pembi/Nirmal/Telangana
    parts = [
        part.strip()
        for part in location.replace(",", "/").split("/")
        if part.strip()
    ]

    place = None

    # Search village first, then district
    for name in parts:

        geo_params = {
            "name": name,
            "count": 10,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=15
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        results = geo_data.get("results", [])

        # Prefer a location in Telangana, India
        for result in results:
            if (
                result.get("country_code") == "IN"
                and "telangana" in result.get("admin1", "").lower()
            ):
                place = result
                break

        if place:
            break

    if not place:
        raise ValueError("Farm location not found. Try entering Nirmal, Telangana.")

    latitude = place["latitude"]
    longitude = place["longitude"]

    # Get weather information
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain",
        "daily": "precipitation_sum,precipitation_probability_max",
        "forecast_days": 1,
        "timezone": "auto"
    }

    weather_response = requests.get(
        weather_url,
        params=weather_params,
        timeout=15
    )

    weather_response.raise_for_status()

    weather_data = weather_response.json()

    current = weather_data["current"]
    daily = weather_data["daily"]

    return {
        "location": place["name"] + ", " + place.get("admin1", "Telangana"),
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "current_precipitation": current["precipitation"],
        "current_rain": current["rain"],
        "today_rainfall_forecast": daily["precipitation_sum"][0],
        "rain_probability": daily["precipitation_probability_max"][0]
    }
