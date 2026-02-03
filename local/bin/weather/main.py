#!/usr/bin/env python3
import json
from lib.weatherdataframe import open_meteo
from lib.iconmapper import map_icons
from lib.timecalc import add_daytime_flag
from lib.tooltip import build_tooltip

LATITUDE = 34.1751
LONGITUDE = -82.024
HOURLY_STEP = 2
TIMEZONE = "America/New_York"
METRIC = False


def main():
    daily_df, hourly_df = open_meteo(LATITUDE, LONGITUDE)
    hourly_df = add_daytime_flag(
        hourly_df, daily_df, TIMEZONE, HOURLY_STEP, metric=METRIC
    )
    hourly_df = map_icons(hourly_df, is_hourly=True)
    daily_df = map_icons(daily_df, is_hourly=False)
    tooltip = build_tooltip(
        daily_df, hourly_df, my_zone=TIMEZONE, hourly_step=HOURLY_STEP
    )
    current = hourly_df.iloc[0]
    output = {
        "text": current.icon,
        "tooltip": tooltip,
        "class": current.description,
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
