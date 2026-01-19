import requests
from config import WEATHER_API_KEY


def get_weather(city='Omaha', units='imperial'):
    """Get current weather and forecast"""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': units 
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        return {
            'temp': f"{data['main']['temp']:.0f}°F",
            'feels_like': f"{data['main']['feels_like']:.0f}°F",
            'high': f"{data['main']['temp_max']:.0f}°F",
            'low': f"{data['main']['temp_min']:.0f}°F",
            'conditions': data['weather'][0]['description'],
            'city': city
        }

    except Exception as e:
        print(f"Weather error: {e}")
        return None
