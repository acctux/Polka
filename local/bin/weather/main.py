#!/usr/bin/env python3
import json
from lib.weatherdataframe import open_meteo
from lib.gen_tooltip import build_tooltip
from lib.iconmapper import add_day_night_flag, map_icons

LATITUDE = (34.1751,)
LONGITUDE = (-82.024,)
HOURLY_STEP = 3
TIMEZONE = "America/New_York"


def main():
    daily_df, hourly_df = open_meteo(LATITUDE, LONGITUDE)
    hourly_df = add_day_night_flag(hourly_df, daily_df, TIMEZONE)
    hourly_df = map_icons(hourly_df, is_hourly=True)
    daily_df = map_icons(daily_df, is_hourly=False)
    tooltip = build_tooltip(daily_df, hourly_df, TIMEZONE, HOURLY_STEP)
    current_row = hourly_df.iloc[0]
    output = {
        "text": current_row.icon,
        "tooltip": tooltip,
        "class": current_row.description,
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
