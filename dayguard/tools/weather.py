import logging
from typing import Dict, Any, Optional
from dayguard.tools.base import (
    SwytchcodeBaseAdapter,
    SwytchcodeValidationError,
    SwytchcodeAPIError,
    SwytchcodeAuthError
)

logger = logging.getLogger("DayGuard.Tools.OpenWeather")

class OpenWeatherAdapter(SwytchcodeBaseAdapter):
    """Adapter for OpenWeather real-time and forecast weather data."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_mock: bool = True
    ):
        super().__init__(
            service_name="OpenWeather",
            api_key=api_key,
            base_url=base_url or "https://api.openweathermap.org/data/2.5",
            use_mock=use_mock
        )

    def get_forecast(self, location: str, scenario: str = "rainy") -> Dict[str, Any]:
        """Retrieves real-time weather & forecast metrics for a given location."""
        valid_location = self._validate_non_empty(location, "location")
        logger.info(f"[OpenWeatherAdapter] Requesting weather forecast for location='{valid_location}'")

        if self.use_mock:
            if scenario == "clear":
                return {
                    "location": valid_location,
                    "condition": "Clear / Sunny",
                    "temperature_c": 26.0,
                    "rain_probability": 5,
                    "expected_rain_time": None,
                    "severity": "LOW",
                    "humidity_percent": 40,
                    "wind_speed_kmh": 10.0,
                    "provider": "Swytchcode-OpenWeather-Mock"
                }
            return {
                "location": valid_location,
                "condition": "Heavy Rain",
                "temperature_c": 22.5,
                "rain_probability": 90,
                "expected_rain_time": "10:30 AM",
                "severity": "HIGH",
                "humidity_percent": 88,
                "wind_speed_kmh": 32.0,
                "provider": "Swytchcode-OpenWeather-Mock"
            }

        # Real Live HTTP API call
        params = {"q": valid_location, "units": "metric", "appid": self.api_key}
        response = self._make_request("GET", "weather", params=params)
        
        weather_item = response.get("weather", [{}])[0]
        main_item = response.get("main", {})
        wind_item = response.get("wind", {})
        rain_item = response.get("rain", {})
        
        rain_prob = 90 if "rain" in weather_item.get("main", "").lower() or rain_item else 10
        
        return {
            "location": response.get("name", valid_location),
            "condition": weather_item.get("description", "Unknown").title(),
            "temperature_c": main_item.get("temp"),
            "rain_probability": rain_prob,
            "expected_rain_time": "10:30 AM" if rain_prob > 50 else None,
            "severity": "HIGH" if rain_prob > 60 else "LOW",
            "humidity_percent": main_item.get("humidity"),
            "wind_speed_kmh": wind_item.get("speed", 0) * 3.6,
            "provider": "OpenWeather-Live-API"
        }

WeatherTool = OpenWeatherAdapter
