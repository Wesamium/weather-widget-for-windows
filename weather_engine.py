import requests

class WeatherEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"

    def get_coords_by_name(self, city_name):
        """Converts city string into latitude and longitude."""
        params = {'q': city_name, 'limit': 1, 'appid': self.api_key}
        try:
            response = requests.get(self.geo_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data:
                display_label = f"{data[0]['name']}, {data[0].get('country', '')}"
                return data[0]['lat'], data[0]['lon'], display_label
            return None
        except Exception as e:
            print(f"Geocoding lookup failed: {e}")
            return None

    def get_weather(self, lat, lon):
        """Fetches weather data including the official layout icon ID."""
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'en'
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                "temp": round(data["main"]["temp"]),
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"].title(),
                "icon_id": data["weather"][0]["icon"] # <-- EXTRACTS ICON CODE (e.g., "01d")
            }
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None