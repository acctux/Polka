import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 34.1954,
    "longitude": -82.1618,
    "daily": [
        "weather_code",
        "precipitation_sum",
        "sunrise",
        "sunset",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_probability_max",
    ],
    "hourly": [
        "temperature_2m",
        "precipitation_probability",
        "precipitation",
        "weather_code",
    ],
    "timezone": "America/New_York",
    "wind_speed_unit": "mph",
    "temperature_unit": "fahrenheit",
    "precipitation_unit": "inch",
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(3).ValuesAsNumpy()

hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(
            hourly.Time() + response.UtcOffsetSeconds(), unit="s", utc=True
        ),
        end=pd.to_datetime(
            hourly.TimeEnd() + response.UtcOffsetSeconds(), unit="s", utc=True
        ),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left",
    )
}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["precipitation_probability"] = hourly_precipitation_probability
hourly_data["precipitation"] = hourly_precipitation
hourly_data["weather_code"] = hourly_weather_code

hourly_dataframe = pd.DataFrame(data=hourly_data)
print("\nHourly data\n", hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(1).ValuesAsNumpy()
daily_sunrise = daily.Variables(2).ValuesInt64AsNumpy()
daily_sunset = daily.Variables(3).ValuesInt64AsNumpy()
daily_temperature_2m_max = daily.Variables(4).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(5).ValuesAsNumpy()
daily_precipitation_probability_max = daily.Variables(6).ValuesAsNumpy()

daily_data = {
    "date": pd.date_range(
        start=pd.to_datetime(
            daily.Time() + response.UtcOffsetSeconds(), unit="s", utc=True
        ),
        end=pd.to_datetime(
            daily.TimeEnd() + response.UtcOffsetSeconds(), unit="s", utc=True
        ),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    )
}

daily_data["weather_code"] = daily_weather_code
daily_data["precipitation_sum"] = daily_precipitation_sum
daily_data["sunrise"] = daily_sunrise
daily_data["sunset"] = daily_sunset
daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["precipitation_probability_max"] = daily_precipitation_probability_max

daily_dataframe = pd.DataFrame(data=daily_data)
print("\nDaily data\n", daily_dataframe)
