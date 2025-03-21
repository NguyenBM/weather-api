from flask import Flask, jsonify, request
import redis_client
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import requests


# Creates an instance of flask web server & a limiter preventing overusage of this api
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# load variables from .env files
load_dotenv()

# Visual crossing api key
API_KEY = os.getenv("API_KEY")

# base url for visual crossing
BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"


# Home route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Weather API!"})

# weather request
@app.route("/weather", methods=["GET"])
def get_weather():

    # check first in cache if data is present already (retrieve)
    city = request.args.get("city")

    # returns error if city argument not present
    if not city:
        return jsonify({"error": "City parameter is required"}), 400
    
    # requests data for the city code IF present in cache
    cached_data = get_cache(city)
    if cached_data:
        return jsonify({"source": "cache", "data": eval(cached_data)})
    
    # if not already cached we fetch from visual crossing api and set it in the cache
    url = f"{BASE_URL}/{city}?key={API_KEY}&unitGroup=metric"
    response = requests.get(url)

    # raise error if problems are encountered
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch weather data"}), 500
    
    # converts weather data to json
    weather_data = response.json()

    # Store response in Redis cache (Time To Live = 12 hour)
    redis_client.setex(city, 43200, str(weather_data))

    # return the weather data
    return jsonify({"source": "API", "data": weather_data})

"""
Following communicates with Reddis API to either set or retrieve data
"""
# uses city code to check if information present in cache already
def get_cache(city):
    return redis_client.get(city)

# Starts app
if __name__ == '__main__':
    app.run(debug=True)