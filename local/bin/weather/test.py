#!/usr/bin/env python3
import json
from lib.weatherdataframe import open_meteo
import pandas as pd
from pydantic.dataclasses import dataclass
from zoneinfo import ZoneInfo


LATITUDE = 34.1751
LONGITUDE = -82.024
HOURLY_STEP = 1
TIMEZONE = "America/New_York"
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


def convert_temperature(fahrenheit: float, celsius: bool) -> int:
    if celsius:
        return round((fahrenheit - 32) * 5 / 9)
    return round(fahrenheit)


def format_precipitation(precipitation: float, celsius: bool) -> str:
    if precipitation < 0.01:
        return ""
    unit = "cm" if celsius else "in"
    return (
        f"{precipitation:.1f}{unit}"
        if precipitation >= 0.1
        else f"{precipitation:.2f}{unit}".lstrip("0")
    )


def is_daytime(
    hourly_df: pd.DataFrame, daily_df: pd.DataFrame, timezone: str
) -> pd.DataFrame:
    daily_df["sunrise"] = pd.to_datetime(
        daily_df["sunrise"], unit="s", utc=True
    ).dt.tz_convert(ZoneInfo(timezone))
    daily_df["sunset"] = pd.to_datetime(
        daily_df["sunset"], unit="s", utc=True
    ).dt.tz_convert(ZoneInfo(timezone))
    hourly_df["local_date"] = hourly_df["date"].dt.tz_convert(timezone).dt.date
    sun_times = daily_df.set_index(daily_df["date"].dt.date)[["sunrise", "sunset"]]
    hourly_df = hourly_df.merge(
        sun_times, left_on="local_date", right_index=True, how="left"
    )
    hourly_df["date"] = pd.to_datetime(hourly_df["date"])
    hourly_df["is_day"] = hourly_df["date"].between(
        hourly_df["sunrise"], hourly_df["sunset"], inclusive="left"
    )
    hourly_df["status_change"] = None
    for idx in range(1, len(hourly_df)):
        if hourly_df["is_day"].iloc[idx] != hourly_df["is_day"].iloc[idx - 1]:
            hourly_df.at[idx - 1, "status_change"] = "󰖜"
    return hourly_df


def today_formatted() -> str:
    today = pd.to_datetime("today")

    def add_day_suffix(day: int) -> str:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        if 10 <= day % 100 <= 20:
            suffix = "th"
        return f"{day}{suffix}"

    day_with_suffix = add_day_suffix(today.day)
    formatted_date = today.strftime(f"%a, %b. {day_with_suffix}, %Y")

    return formatted_date


@dataclass
class WeatherEntry:
    label: str
    icon: str
    temp_high: float
    temp_low: float | None = None
    precip_prob: int = 0
    precipitation: float = 0.0
    sun: str | None = None

    def temp_str(self, high, low: float | None = None, celsius: bool = False) -> str:
        def conv(f: float) -> int:
            return round((f - 32) * 5 / 9) if celsius else round(f)

        high = conv(self.temp_high)
        low = conv(self.temp_low) if self.temp_low is not None else None
        if low:
            return f"{high}/{low}<span size='16pt'></span>{'C' if celsius else 'F'}"
        return f"{high}<span size='16pt'></span>{'C' if celsius else 'F'}"

    def precip_str(self, celsius: bool = False) -> str:
        if self.precipitation < 0.01:
            return ""
        unit = "cm" if celsius else "in"
        return (
            f"{self.precipitation:.1f}{unit}"
            if self.precipitation >= 0.1
            else f"{self.precipitation:.2f}{unit}".lstrip("0")
        )

    def format(self, celsius: bool = False) -> str:
        t = self.temp_str(celsius)
        p_prob = f"{self.precip_prob}%" if self.precip_prob > 0 else ""
        p_sum = self.precip_str(celsius)
        precip_icon = "󰖌" if self.precip_prob > 0 or self.precipitation > 0 else ""
        is_hourly = ":" in self.label
        if is_hourly:
            return (
                f"{self.label}"
                f"<span size='18pt'>{self.icon.rjust(3)}</span>"
                f"{t.rjust(7)}"
                f"{precip_icon.rjust(2)}"
                f"{p_prob.rjust(4)} {p_sum.rjust(5)}"
                f"{p_prob.rjust(4)} {p_sum.rjust(5)}"
            )
        else:
            return (
                f"{self.label}"
                f"<span size='18pt'>{self.icon.rjust(3)}</span>"
                f"{t.rjust(7)}"
                f"{precip_icon.rjust(2)}"
                f"{p_prob.rjust(4)} {p_sum.rjust(5)}"
            )


def build_tooltip(
    daily_df: pd.DataFrame,
    hourly_df: pd.DataFrame,
    hourly_step: int = 2,
    celsius: bool = False,
) -> str:
    daily_entries = [
        WeatherEntry(
            label=row["date"].strftime("%m-%d"),
            icon=row["icon"],
            temp_high=row["temperature_2m_max"],
            temp_low=row["temperature_2m_min"],
            precip_prob=int(row["precipitation_probability_max"]),
            precipitation=row["precipitation_sum"],
        )
        for _, row in daily_df.iterrows()
    ]
    hourly_entries = [
        WeatherEntry(
            label=row["date"].strftime("%H:%M"),
            icon=row["icon"],
            temp_high=row["temperature_2m"],
            precip_prob=int(row["precipitation_probability"]),
            precipitation=row["precipitation"],
            sun=row["status_change"],
        )
        for idx, (_, row) in enumerate(hourly_df.head(24).iterrows())
        if idx % int(hourly_step) == 0
    ]
    icon_size = 17
    hourly_text = "\n".join(e.format(celsius) for e in hourly_entries)
    daily_text = "\n".join(e.format(celsius) for e in daily_entries)
    return (
        f"<span size='{icon_size}pt'></span>    <span size='14pt'>{today_formatted()}</span>\n"
        "───────────────────────────────────\n"
        f"{hourly_text}"
        f"\n\n<span size='{icon_size}pt'>󰨳</span>\n"
        "───────────────────────────────────\n"
        f"{daily_text}\n"
    )


def main():
    daily_df, hourly_df = open_meteo(LATITUDE, LONGITUDE)
    hourly_df = is_daytime(hourly_df, daily_df, TIMEZONE)
    hourly_df = map_icons(hourly_df, is_hourly=True)
    daily_df = map_icons(daily_df, is_hourly=False)
    # print(f"{hourly_df['status_change'].head(20)}")
    tooltip = build_tooltip(daily_df, hourly_df, HOURLY_STEP)
    current_row = hourly_df.iloc[0]
    output = {
        "text": current_row.icon,
        "tooltip": tooltip,
        "class": current_row.description,
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
