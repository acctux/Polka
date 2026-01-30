#!/home/nick/.local/bin/weather/.venv/bin/python

import json
import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests

# Weather code → icon & description
WMO_ICONS = {
    0: "",
    1: "",
    2: "",
    3: "",
    4: "",
    5: "",
    6: "",
    7: "",
    8: "",
    10: "",
    11: "",
    12: "",
    13: "",
    14: "",
    15: "",
    16: "",
    17: "",
    18: "",
    19: "",
    20: "",
    21: "",
    22: "",
    23: "",
    24: "",
    25: "",
    26: "",
    27: "",
    28: "",
    29: "",
    30: "",
    31: "",
    32: "",
    33: "",
    34: "",
    35: "",
    36: "",
    37: "",
    38: "",
    39: "",
    40: "",
    41: "",
    42: "",
    43: "",
    44: "",
    45: "",
    46: "",
    47: "",
    48: "",
    49: "",
}


def get_icon(code: float) -> str:
    return WMO_ICONS.get(int(code), "")


def get_class_grouped(code: float) -> str:
    code = int(code)
    if code in (0, 1):
        return "clear"
    if code in (2, 3):
        return "cloudy"
    if 40 <= code <= 49:
        return "fog"
    if (51 <= code <= 55) or (61 <= code <= 65) or (80 <= code <= 82):
        return "rain"
    if (71 <= code <= 75) or (85 <= code <= 86):
        return "snow"
    if code >= 95:
        return "thunder"
    if code in (23, 24, 25, 26, 27):
        return "mixed"
    return "unknown"


session = retry(
    requests_cache.CachedSession(".cache", expire_after=3600),
    retries=5,
    backoff_factor=0.2,
)
client = openmeteo_requests.Client(session=session)  # type: ignore
params = {
    "latitude": 34.1751,
    "longitude": -82.024,
    "daily": [
        "weather_code",
        "sunrise",
        "sunset",
        "precipitation_sum",
        "precipitation_probability_max",
        "apparent_temperature_max",
        "apparent_temperature_min",
    ],
    "hourly": ["weather_code"],
    "current": ["weather_code"],
    "timezone": "America/New_York",
    "timeformat": "unixtime",
}

response = client.weather_api("https://api.open-meteo.com/v1/forecast", params=params)[
    0
]

# Daily data
daily = response.Daily()
daily_dates = pd.to_datetime(
    daily.Time().ValuesAsNumpy() + response.UtcOffsetSeconds(), unit="s", utc=True
)
daily_data = pd.DataFrame(
    {
        "date": daily_dates,
        "weather_code": daily.Variables(0).ValuesAsNumpy(),
        "apparent_temp_max": daily.Variables(5).ValuesAsNumpy(),
        "apparent_temp_min": daily.Variables(6).ValuesAsNumpy(),
        "precip_prob": daily.Variables(4).ValuesAsNumpy(),
        "precip_sum": daily.Variables(3).ValuesAsNumpy(),
    }
)
daily_data["icon"] = daily_data["weather_code"].apply(get_icon)
hourly = response.Hourly()
hourly_dates = pd.to_datetime(
    hourly.Time().ValuesAsNumpy() + response.UtcOffsetSeconds(), unit="s", utc=True
)
hourly_data = pd.DataFrame(
    {
        "date": hourly_dates,
        "weather_code": hourly.Variables(0).ValuesAsNumpy(),
    }
)
hourly_data["icon"] = hourly_data["weather_code"].apply(get_icon)
tooltip_lines = [
    f"Day {i + 1}: {row.icon} {row.apparent_temp_max:.0f}/{row.apparent_temp_min:.0f}°F, "
    f"{int(row.precip_prob)}%, {row.precip_sum:.2f} in"
    for i, row in daily_data.iterrows()
]
waybar_output = {
    "text": hourly_data.at[0, "icon"],
    "class": get_class_grouped(hourly_data.at[0, "weather_code"]),
    "tooltip": "\n".join(tooltip_lines),
}
print(json.dumps(waybar_output, ensure_ascii=False))
