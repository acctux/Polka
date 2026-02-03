#!/usr/bin/env python3
import json
from lib.weatherdataframe import open_meteo
from lib.iconmapper import map_icons
from lib.timecalc import add_daytime_flag
from lib.tooltip import build_tooltip
from zoneinfo import ZoneInfo
from dataclasses import dataclass
import pandas as pd


LATITUDE = 34.1751
LONGITUDE = -82.024
HOURLY_STEP = 2
TIMEZONE = "America/New_York"
METRIC = False
WEATHER_ICONS = {
    0: ("clear", "", ""),
    1: ("Clouds dissolving", "", "󰼱"),
    2: ("Sky unchanged", "󰖕", "󰼱"),
    3: ("Clouds forming", "󰖐", "󰖐"),
    4: ("Smoke", "", ""),
    5: ("Haze", "", ""),
    6: ("Dust", "", ""),
    10: ("Mist", "", ""),
    11: ("Patches", "", ""),
    13: ("Lightning, no thunder", "󰼲", ""),
    14: ("Precipitation in sight", "", ""),
    20: ("Drizzel", "", ""),
    21: ("Rain not freezing", "", ""),
    22: ("Snow", "󰼶", ""),
    23: ("Rain,or snow, or ice pellets", "󰙿", "󰙿"),
    25: ("Showers of rain", "󰖗", "󰖗"),
    26: ("Shower(s) of snow, or of rain and snow", "󰙿", "󰙿"),
    28: ("fog", "󰖑", "󰖑"),
    29: ("Thunderstorm", "", ""),
    30: ("Dust/sandstorms", "", ""),
    33: ("Severe dust/sandstorms", "", ""),
    36: ("Slight or moderate blowing snow", "", ""),
    37: ("Heavy drifting snow", "", ""),
    38: ("Slight or moderate blowing snow(above eye level)", "", ""),
    39: ("Heavy drifting snow(above eye level)", "", ""),
    40: ("fog", "", ""),
    50: ("Drizzle, not freezing, intermittent)", "", ""),
    51: ("Drizzle, not freezing, continuous", "", ""),
    52: ("Drizzle, not freezing, intermittent)", "", ""),
    53: ("Drizzle, not freezing, continuous", "", ""),
    54: ("Drizzle, not freezing, intermittent (heavy)", "", ""),
    55: ("Drizzle, not freezing, continuous", "", ""),
    56: ("Drizzle, freezing, slight", "", ""),
    57: ("Drizzle, freezing, moderate or heavy (dense)", "", ""),
    58: ("Drizzle and rain, slight", "", ""),
    59: ("Drizzle and rain, moderate or heavy", "", ""),
    60: ("Rain, not freezing, intermittent (slight)", "󰖗", ""),
    61: ("Rain, not freezing, continuous", "󰖗", ""),
    62: ("Rain, not freezing, intermittent (moderate)", "󰖗", ""),
    63: ("Rain, not freezing, continuous", "󰖗", ""),
    64: ("Rain, not freezing, intermittent (heavy)", "󰖗", ""),
    65: ("Rain, not freezing, continuous", "󰖗", ""),
    66: ("Rain, freezing, slight", "󰖗", ""),
    67: ("Rain, freezing, moderate or heavy (dense)", "󰖗", ""),
    68: ("Rain or drizzle and snow, slight", "󰖗", ""),
    69: ("Rain or drizzle and snow, moderate or heavy", "󰖗", ""),
    70: ("Intermittent fall of snowflakes (slight)", "󰖗", ""),
    71: ("Continuous fall of snowflakes", "󰖗", ""),
    72: ("Intermittent fall of snowflakes (moderate)", "󰖗", ""),
    73: ("Continuous fall of snowflakes", "󰖗", ""),
    74: ("Intermittent fall of snowflakes (heavy)", "󰖗", ""),
    75: ("Continuous fall of snowflakes", "󰖗", ""),
    76: ("Diamond dust (with or without fog)", "󰖗", ""),
    77: ("Snow grains (with or without fog)", "󰖗", ""),
    78: ("Isolated snow crystals (with/without fog)", "󰖗", ""),
    79: ("Ice pellets", "󰖗", ""),
    80: ("rain_showers", "󰖖", ""),
    81: ("rain_showers", "󰖖", ""),
    82: ("rain_showers", "󰖖", ""),
    85: ("snow_showers", "󰖘", ""),
    86: ("snow_showers", "󰖘", ""),
    87: ("rain_showers", "󰖖", ""),
    95: ("thunderstorm", "󰖓", ""),
    96: ("thunderstorm_hail", "", ""),
    99: ("thunderstorm_hail", "󰖒", ""),
}
FALLBACK_ICON = ("unknown", "", "")


def map_icons(
    df: pd.DataFrame,
    is_hourly: bool = False,
    weather_icons=WEATHER_ICONS,
    fallback_icon=FALLBACK_ICON,
) -> pd.DataFrame:
    def pick_icon_and_description(row):
        weather_code = int(row["weather_code"])
        _, day_icon, night_icon = weather_icons.get(weather_code, fallback_icon)
        description = weather_icons.get(weather_code, fallback_icon)[0]
        if is_hourly and not row.get("is_day", True):
            return day_icon, description
        return night_icon, description

    df[["icon", "description"]] = df.apply(
        pick_icon_and_description, axis=1, result_type="expand"
    )
    return df


@dataclass
class WeatherEntry:
    label: str
    icon: str
    temp: float
    units: str
    units_in_cm: str
    sunset_str: str | None = None
    sunrise_str: str | None = None
    temp_low: float | None = None
    precip_prob: int = 0
    precipitation: float = 0.0

    def format(self) -> str:
        today = pd.Timestamp.now().strftime("%m-%d")  # Format today as 'MM-DD'
        label = self.label
        if self.label == today:
            label = "Today"
        precip_prob = f"{self.precip_prob}%" if self.precip_prob > 0 else ""
        precip_sum = (
            str(round(self.precipitation, 2)) if self.precipitation >= 0.01 else ""
        )
        if self.precipitation < 0.1:
            precip_sum = precip_sum.lstrip("0")
        precip_output = ""
        if precip_sum:
            precip_output = f"{precip_sum}{self.units_in_cm}"
        rain_icon = "󰖌" if self.precip_prob > 0 else ""
        temp_low = ""
        if self.temp_low:
            temp_low = round(self.temp_low)
            if self.temp_low > 0.01:
                temp_low = round(self.temp_low)
        sun_icon = ""
        sun_time = ""
        if self.sunrise_str:
            sun_icon = "󰖜".rjust(2)
            sun_time = f"{self.sunrise_str}".rjust(4)
        elif self.sunset_str:
            sun_icon = "󰖛".rjust(2)
            sun_time = f"{self.sunset_str}".rjust(4)
        else:
            sun_icon = ""
        daily_temp = f"{round(self.temp)}/{temp_low}"
        is_hourly = ":" in self.label
        if is_hourly:
            rain_icon = rain_icon.rjust(3)
            return (
                f"{self.label:<5}"
                f"<span size='18pt'>{self.icon.rjust(2)}</span>"
                f"{str(round(self.temp)).rjust(6)}<span size='17pt'></span>{self.units}"
                f"{rain_icon}{precip_prob.rjust(4)}{precip_output.rjust(6)}"
                f"<span size='16pt'>{sun_icon} </span>{sun_time}"
            )
        else:
            rain_icon = rain_icon.rjust(4)
            return (
                f"{label:<5}"
                f"<span size='19pt'>{self.icon.rjust(2)}</span>"
                f"{daily_temp.rjust(9)}<span size='17pt'></span>{self.units}"
                f"{rain_icon}{precip_prob.rjust(4)}{precip_output.rjust(7)}"
            )


def today_formatted() -> str:
    t = pd.Timestamp.now()
    day_suffix = {1: "st", 2: "nd", 3: "rd"}.get(t.day % 10, "th")
    if 10 <= t.day % 100 <= 20:
        day_suffix = "th"
    return t.strftime(f"%a, %b {t.day}{day_suffix}, %Y")


def add_daytime_flag(
    hourly_df: pd.DataFrame, daily_df: pd.DataFrame, tz: str, step: int, metric
) -> pd.DataFrame:
    def is_daytime(row):
        return row["sunrise"] <= row["date"] < row["sunset"]

    def to_dt_tz(df_row, tz):
        return pd.to_datetime(df_row["sunrise"], unit="s", utc=True).dt.tz_convert(
            ZoneInfo(tz)
        )

    daily_df["sunrise"] = pd.to_datetime(
        daily_df["sunrise"], unit="s", utc=True
    ).dt.tz_convert(ZoneInfo(tz))
    daily_df["sunset"] = pd.to_datetime(
        daily_df["sunset"], unit="s", utc=True
    ).dt.tz_convert(ZoneInfo(tz))
    hourly_df["local_date"] = hourly_df["date"].dt.tz_convert(tz).dt.date
    sun_times = daily_df.set_index(daily_df["date"].dt.date)[["sunrise", "sunset"]]
    hourly_df = hourly_df.merge(
        sun_times, left_on="local_date", right_index=True, how="left"
    )
    hourly_df["is_day"] = hourly_df.apply(is_daytime, axis=1)
    hourly_df["sunrise_str"] = hourly_df.apply(
        lambda row: str(row["sunrise"].strftime("%H:%M"))
        if row["date"] <= row["sunrise"] < row["date"] + pd.Timedelta(hours=1)
        else "",
        axis=1,
    )
    hourly_df["sunset_str"] = hourly_df.apply(
        lambda row: str(row["sunset"].strftime("%H:%M"))
        if row["date"] <= row["sunset"] < row["date"] + pd.Timedelta(hours=1)
        else "",
        axis=1,
    )
    units = "in"
    if metric:
        units = "cm"
        hourly_df["temperature_2m"] = (hourly_df["temperature_2m"] - 32) * 5 / 9
        daily_df["temperature_2m_max"] = (daily_df["temperature_2m_max"] - 32) * 5 / 9
        daily_df["temperature_2m_min"] = (daily_df["temperature_2m_min"] - 32) * 5 / 9
    hourly_df["units"] = units
    daily_df["units"] = units
    return hourly_df


def build_tooltip(daily_df, hourly_df, my_zone: str, hourly_step=2, celsius=False):
    def proc_entries(entries):
        return "\n".join([entry.format() for entry in entries])

    unit_str = "C" if celsius else "F"
    t = pd.Timestamp.now(ZoneInfo(my_zone))
    current_time = t.replace(minute=0, second=0, microsecond=0)
    time_24h_later = current_time + pd.Timedelta(hours=48)
    current_time_str = t.strftime("%H:%M")
    hourly_df["date"] = hourly_df["date"].dt.tz_convert(ZoneInfo(my_zone))
    hourly_entries = [
        WeatherEntry(
            label=row["date"].strftime("%H:%M"),
            icon=row["icon"],
            temp=row["temperature_2m"],
            sunrise_str=row["sunrise_str"],
            sunset_str=row["sunset_str"],
            units=unit_str,
            units_in_cm=row["units"],
            precip_prob=int(row.get("precipitation_probability", 0)),
            precipitation=row.get("precipitation", 0.0),
        )
        for i, (_, row) in enumerate(hourly_df.head(48).iterrows())
        if current_time <= row["date"] < time_24h_later
        and (row["date"].hour - current_time.hour) % hourly_step == 0
    ]

    daily_entries = [
        WeatherEntry(
            label=row["date"].strftime("%m-%d"),
            icon=row["icon"],
            units_in_cm=row["units"],
            temp=row["temperature_2m_max"],
            temp_low=row["temperature_2m_min"],
            units=unit_str,
            precip_prob=int(row.get("precipitation_probability_max", 0)),
            precipitation=row.get("precipitation_sum", 0.0),
        )
        for _, row in daily_df.iterrows()
    ]

    icon_size = 18
    return (
        f"<span size='{icon_size}pt'>󰨳</span><span size='14pt'>     {today_formatted()}</span>\n"
        "─────────────────────────────────────────\n"
        + f"{proc_entries(daily_entries)}\n"
        + f"\n<span size='{icon_size}pt'></span>\t<span size='14pt'>    {current_time_str}</span>\n"
        "─────────────────────────────────────────\n"
        + f"{proc_entries(hourly_entries)}"
    )


def main():
    daily_df, hourly_df = open_meteo(LATITUDE, LONGITUDE)
    hourly_df = add_daytime_flag(
        hourly_df, daily_df, TIMEZONE, HOURLY_STEP, metric=METRIC
    )
    hourly_df = map_icons(hourly_df, is_hourly=True)
    daily_df = map_icons(daily_df, is_hourly=False)
    print(f"{hourly_df['sunset_str'].head(48)}")
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

