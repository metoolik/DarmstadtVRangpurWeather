from flask import Flask, render_template, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
API_KEY = "bee38e967bed3bcf0aeeaa375b630dbd"  # Replace with your actual API key
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# City coordinates
CITIES = {
    "Darmstadt": {"lat": 49.8728, "lon": 8.6512, "country": "Germany"},
    "Rangpur": {"lat": 25.7439, "lon": 89.2752, "country": "Bangladesh"}
}


def get_weather_data(city_name):
    """Fetch weather data for a given city"""
    try:
        # Check if API key is set
        if API_KEY == "YOUR_OPENWEATHER_API_KEY" or not API_KEY:
            print("ERROR: Please set your OpenWeatherMap API key in app.py")
            return None

        city_info = CITIES[city_name]
        params = {
            "lat": city_info["lat"],
            "lon": city_info["lon"],
            "appid": API_KEY,
            "units": "metric"  # Celsius
        }

        print(f"Making API request for {city_name}...")
        response = requests.get(BASE_URL, params=params, timeout=10)
        print(f"API Response Status: {response.status_code}")

        if response.status_code == 401:
            print("ERROR: Invalid API key")
            return None
        elif response.status_code == 429:
            print("ERROR: API rate limit exceeded")
            return None

        response.raise_for_status()

        data = response.json()

        # Extract relevant weather information
        weather_info = {
            "city": city_name,
            "country": city_info["country"],
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "description": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"].get("deg", 0),
            "visibility": data.get("visibility", 0) / 1000,  # Convert to km
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return weather_info

    except requests.RequestException as e:
        print(f"API request failed for {city_name}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response text: {e.response.text}")
        return None
    except KeyError as e:
        print(f"Missing data in API response for {city_name}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {city_name}: {e}")
        return None


def compare_weather(darmstadt_data, rangpur_data):
    """Compare weather data between two cities"""
    if not darmstadt_data or not rangpur_data:
        return None

    comparison = {
        "temperature_diff": round(darmstadt_data["temperature"] - rangpur_data["temperature"], 1),
        "humidity_diff": darmstadt_data["humidity"] - rangpur_data["humidity"],
        "pressure_diff": darmstadt_data["pressure"] - rangpur_data["pressure"],
        "warmer_city": "Darmstadt" if darmstadt_data["temperature"] > rangpur_data["temperature"] else "Rangpur",
        "more_humid_city": "Darmstadt" if darmstadt_data["humidity"] > rangpur_data["humidity"] else "Rangpur"
    }

    return comparison


@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')


@app.route('/api/weather')
def get_weather():
    """API endpoint to get weather data for both cities"""
    darmstadt_weather = get_weather_data("Darmstadt")
    rangpur_weather = get_weather_data("Rangpur")

    if not darmstadt_weather or not rangpur_weather:
        return jsonify({"error": "Failed to fetch weather data"}), 500

    comparison = compare_weather(darmstadt_weather, rangpur_weather)

    return jsonify({
        "darmstadt": darmstadt_weather,
        "rangpur": rangpur_weather,
        "comparison": comparison,
        "success": True
    })


@app.route('/api/weather/<city>')
def get_city_weather(city):
    """API endpoint to get weather data for a specific city"""
    if city not in CITIES:
        return jsonify({"error": "City not found"}), 404

    weather_data = get_weather_data(city)

    if not weather_data:
        return jsonify({"error": "Failed to fetch weather data"}), 500

    return jsonify(weather_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)