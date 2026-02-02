import json
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
from pydantic.dataclasses import dataclass

LATITUDE = 34.1751
LONGITUDE = -82.024


def fetch_weather(lat, lon):
    def create_retry_session():
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        return retry_session

    session = create_retry_session()
    openmeteo = openmeteo_requests.Client(session)
    params = {
        "latitude": lat,
        "longitude": lon,
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
    response = openmeteo.weather_api(
        "https://api.open-meteo.com/v1/forecast", params=params
    )[0]
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
    return daily_dataframe, hourly_dataframe


class WeatherIconMapper:
    def __init__(self):
        self.weather_icons = {
            "clear_sky": {
                "day_icon": "󰖙",
                "night_icon": "",
                "wmo_codes": [0],
            },
            "mainly_clear": {
                "day_icon": "󰖕",
                "night_icon": "",
                "wmo_codes": [1, 2, 3],
            },
            "fog": {
                "day_icon": "󰖑",
                "night_icon": "",
                "wmo_codes": [45, 48],
            },
            "drizzle_light": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [51],
            },
            "drizzle_moderate": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [53],
            },
            "drizzle_dense": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [55],
            },
            "freezing_drizzle_light": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [56],
            },
            "freezing_drizzle_dense": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [57],
            },
            "rain_slight": {
                "day_icon": "󰖗",
                "night_icon": "",
                "wmo_codes": [61],
            },
            "rain_moderate": {
                "day_icon": "󰖗",
                "night_icon": "",
                "wmo_codes": [63],
            },
            "rain_heavy": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [65],
            },
            "freezing_rain_light": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [66],
            },
            "freezing_rain_heavy": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [67],
            },
            "snowfall_slight": {
                "day_icon": "󰖘",
                "night_icon": "",
                "wmo_codes": [71],
            },
            "snowfall_moderate": {
                "day_icon": "󰖘",
                "night_icon": "",
                "wmo_codes": [73],
            },
            "snowfall_heavy": {
                "day_icon": "󰖘",
                "night_icon": "",
                "wmo_codes": [75],
            },
            "snow_grains": {
                "day_icon": "󰖘",
                "night_icon": "",
                "wmo_codes": [77],
            },
            "rain_showers_slight": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [80],
            },
            "rain_showers_moderate": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [81],
            },
            "rain_showers_violent": {
                "day_icon": "󰖖",
                "night_icon": "",
                "wmo_codes": [82],
            },
            "snow_showers_slight": {
                "day_icon": "󰖘",
                "night_icon": "",
                "wmo_codes": [85],
            },
            "snow_showers_heavy": {
                "day_icon": "󰖘",
                "night_icon": "",
                "wmo_codes": [86],
            },
            "thunderstorm_slight": {
                "day_icon": "󰖓",
                "night_icon": "",
                "wmo_codes": [95],
            },
            "thunderstorm_moderate": {
                "day_icon": "󰖓",
                "night_icon": "",
                "wmo_codes": [95],
            },
            "thunderstorm_hail_slight": {
                "day_icon": "󰖓",
                "night_icon": "",
                "wmo_codes": [96],
            },
            "thunderstorm_hail_heavy": {
                "day_icon": "󰖓",
                "night_icon": "",
                "wmo_codes": [99],
            },
        }

    def get_weather_description(self, wmo_code):
        for condition, data in self.weather_icons.items():
            if wmo_code in data["wmo_codes"]:
                return condition
        return None

    def get_icon(self, code, is_night=False):
        for weather, icon_data in self.weather_icons.items():
            if code in icon_data["wmo_codes"]:
                return icon_data["night_icon"] if is_night else icon_data["day_icon"]
        return self.weather_icons["clear_sky"]["day_icon"]


@dataclass
class WeatherLine:
    time_or_day: str
    icon: str
    temperature_2m_max: float
    temperature_min: float | None
    precip_probability: float
    precipitation: float

    def fahrenheit_to_celsius(self, fahrenheit: float) -> float:
        return (fahrenheit - 32) * 5 / 9

    def format_temperature(self, temperature: float, celsius: bool) -> str:
        if celsius:
            return f"{self.fahrenheit_to_celsius(temperature):.0f}"
        return f"{temperature:.0f}"

    def format_precipitation(self, celsius: bool) -> str:
        precip = ""
        if self.precipitation:
            if self.precipitation >= 0.1:
                precip = f"{self.precipitation:.1f}"
            else:
                precip_format = f"{self.precipitation:.2f}".lstrip("0")
                if celsius:
                    precip = f"{precip_format}<span size='10pt'> </span>(cm)"
                else:
                    precip = f"{precip_format} in"
        return precip

    def __str__(self, celsius: bool = False):
        precip_icon = "󰖌".rjust(3) if self.precip_probability else ""
        prob = f"{self.precip_probability:.0f}%" if self.precip_probability else ""
        temp_max = self.format_temperature(self.temperature_2m_max, celsius)
        temp_min = (
            self.format_temperature(self.temperature_min, celsius)
            if self.temperature_min is not None
            else ""
        )
        precip = self.format_precipitation(celsius)

        if ":" in self.time_or_day:
            return (
                f"{self.time_or_day}"
                f"<span size='20pt'>{self.icon.rjust(4)}</span>"
                f"{temp_max.rjust(6)}"
                f"<span size='16pt'></span>"
                f"<span size='14pt'>{precip_icon}</span>"
                f"{prob.rjust(4)}   "
                f"{precip.rjust(3)}"
            )
        else:
            return (
                f"{self.time_or_day}"
                f"<span size='20pt'>{self.icon.rjust(4)}</span>"
                f"{temp_max.rjust(6)}"
                f"<span size='16pt'></span>/"
                f"{temp_min.rjust(3)}"
                f"<span size='16pt'></span>"
                f" <span size='14pt'>{precip_icon}</span>"
                f"{prob.rjust(4)}"
                f"  {precip.ljust(3)}"
            )


def is_night(daily_df, hourly_df):
    mapping = daily_df.set_index(daily_df["date"].dt.date)[["sunrise", "sunset"]]
    hourly_df = hourly_df.assign(
        sunrise=pd.to_datetime(
            hourly_df["date"].dt.date.map(mapping["sunrise"]), unit="s", utc=True
        ),
        sunset=pd.to_datetime(
            hourly_df["date"].dt.date.map(mapping["sunset"]), unit="s", utc=True
        ),
        date=pd.to_datetime(hourly_df["date"], utc=True),
    )
    hourly_df["Day"] = hourly_df["date"].between(
        hourly_df["sunrise"], hourly_df["sunset"]
    )
    return hourly_df


def generate_weather_lines(df, is_hourly=True, hour_step=2):
    weather_lines = []
    for i, r in df.iterrows():
        if is_hourly and i % hour_step != 0:
            continue
        weather_lines.append(
            WeatherLine(
                r["date"].strftime("%H:%M" if is_hourly else "%m-%d"),
                r["icon"],
                r["temperature_2m"] if is_hourly else r["temperature_2m_max"],
                None if is_hourly else r["temperature_2m_min"],
                int(r["precipitation_probability"])
                if is_hourly
                else int(r["precipitation_probability_max"]),
                r["precipitation"] if is_hourly else r["precipitation_sum"],
            )
        )
    return weather_lines


def generate_tooltip(daily_df, hourly_df, hour_step=2):
    icon_size = 17
    sun_size = 19
    hourly_lines = generate_weather_lines(
        hourly_df, is_hourly=True, hour_step=hour_step
    )
    daily_lines = generate_weather_lines(daily_df, is_hourly=False)
    hourly_str = "\n ".join(str(line) for line in hourly_lines)
    daily_str = "\n ".join(str(line) for line in daily_lines)
    tooltip = (
        f" <span size='{icon_size}pt'></span><span size='{icon_size}pt'>󰔏</span>\n"
        "_____________________________________________\n "
        + hourly_str
        + f"<span size='{sun_size}pt'>󱣖</span><span size='20pt'></span>"
        f"<span size='{sun_size}pt'>󱩱</span><span size='{sun_size}pt'>󰙿</span>  "
        f"<span size='{icon_size}pt'>󰏰</span>\<span size='{icon_size}pt'>󰑭</span>\n"
        "_____________________________________________\n " + daily_str
    )
    return tooltip


def apply_icons_to_dataframes(hourly_df, daily_df, icon_mapper):
    def get_hourly_info(row):
        code = row["weather_code"]
        icon = icon_mapper.get_icon(code, is_night=not row["Day"])
        weather_class = icon_mapper.get_weather_description(code)
        return pd.Series([icon, weather_class])

    def get_daily_info(row):
        code = row["weather_code"]
        icon = icon_mapper.get_icon(code, is_night=False)
        weather_class = icon_mapper.get_weather_description(code)
        return pd.Series([icon, weather_class])

    hourly_df[["icon", "weather_class"]] = hourly_df.apply(get_hourly_info, axis=1)
    daily_df[["icon", "weather_class"]] = daily_df.apply(get_daily_info, axis=1)
    return hourly_df, daily_df


def main(latitude: float = LATITUDE, longitude: float = LONGITUDE):
    daily_df, hourly_df = fetch_weather(LATITUDE, LONGITUDE)
    icon_mapper = WeatherIconMapper()
    hourly_df = is_night(daily_df, hourly_df)
    hourly_df, daily_df = apply_icons_to_dataframes(hourly_df, daily_df, icon_mapper)
    tz = "America/New_York"
    for index, row in hourly_df.iterrows():
        sunrise = row["sunrise"].tz_convert(tz)
        sunset = row["sunset"].tz_convert(tz)
        hourly_df.loc[index, "sunrise_local"] = sunrise
        hourly_df.loc[index, "sunset_local"] = sunset
        date_local = row["date"]
        hourly_df.loc[index, "date_local"] = date_local
    toolbar = generate_tooltip(daily_df, hourly_df)
    waybar_json = {
        "text": hourly_df.at[0, "icon"],
        "class": hourly_df.at[0, "weather_class"],
        "tooltip": toolbar,
    }
    print(json.dumps(waybar_json, ensure_ascii=False))


if __name__ == "__main__":
    main()
#     print(daily_df[["date", "sunrise_local", "sunset_local"]])
