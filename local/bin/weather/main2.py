import json
import pandas as pd
from lib.iconmapper import WeatherIconMapper
from lib.weatherdataframe import fetch_weather, daily_weatherframe, hourly_weatherframe
from lib.gen_tooltip import generate_tooltip

LATITUDE = 34.1751
LONGITUDE = -82.024


def icons_right(hourly_df, daily_df, icon_mapper):
    def get_icon_and_class(row, is_night=False):
        code = row["weather_code"]
        icon = icon_mapper.get_icon(code, is_night)
        weather_class = icon_mapper.get_weather_description(code)
        return pd.Series([icon, weather_class])

    hourly_df[["icon", "weather_class"]] = hourly_df.apply(
        lambda row: get_icon_and_class(row, is_night=False), axis=1
    )
    daily_df[["icon", "weather_class"]] = daily_df.apply(
        lambda row: get_icon_and_class(row, is_night=False), axis=1
    )
    return hourly_df, daily_df


def convert_tz(data, daily_df):
    daily = data.Daily()
    sunrise_utc = pd.to_datetime(
        daily.Variables(2).ValuesInt64AsNumpy(), unit="s", utc=True
    )
    sunset_utc = pd.to_datetime(
        daily.Variables(3).ValuesInt64AsNumpy(), unit="s", utc=True
    )
    sunrise_local = sunrise_utc + pd.Timedelta(seconds=-18000)
    sunset_local = sunset_utc + pd.Timedelta(seconds=-18000)
    daily_df["sunrise_local"] = sunrise_local
    daily_df["sunset_local"] = sunset_local
    # print(daily_df[["date", "sunrise_local", "sunset_local"]])


def main(latitude: float = LATITUDE, longitude: float = LONGITUDE):
    #     daily = data.Daily()
    #     sunrise_utc = pd.to_datetime(
    #         daily.Variables(2).ValuesInt64AsNumpy(), unit="s", utc=True
    #     )
    #     sunset_utc = pd.to_datetime(
    #         daily.Variables(3).ValuesInt64AsNumpy(), unit="s", utc=True
    #     )
    #     sunrise_local = sunrise_utc + pd.Timedelta(seconds=-18000)
    #     sunset_local = sunset_utc + pd.Timedelta(seconds=-18000)
    #     daily_df["sunrise_local"] = sunrise_local
    #     daily_df["sunset_local"] = sunset_local
    data = fetch_weather(latitude, longitude)
    daily_df = daily_weatherframe(data)
    hourly_df = hourly_weatherframe(data)
    icon_mapper = WeatherIconMapper()
    convert_tz(data, daily_df)
    icons_right(hourly_df, daily_df, icon_mapper)
    toolbar = generate_tooltip(daily_df, hourly_df)
    waybar_json = {
        "text": hourly_df.at[0, "icon"],
        "class": hourly_df.at[0, "weather_class"],
        "tooltip": toolbar,
    }
    print(json.dumps(waybar_json, ensure_ascii=False))


if __name__ == "__main__":
    main()

# if __name__ == "__main__":

#     print(daily_df[["date", "sunrise_local", "sunset_local"]])
