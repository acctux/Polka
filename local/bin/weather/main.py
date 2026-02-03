#!/usr/bin/env python3
import json
from lib.weatherdataframe import open_meteo
import pandas as pd
from dataclasses import dataclass
from zoneinfo import ZoneInfo

LATITUDE = 34.1751
LONGITUDE = -82.024
HOURLY_STEP = 1
TIMEZONE = "America/New_York"
CELSIUS = False

WEATHER_ICONS = {
    0: ("clear", "", ""),
    1: ("mainly_clear", "", "󰼱"),
    2: ("partly_cloudy", "󰖕", "󰼱"),
    3: ("overcast", "󰖐", "󰖐"),
    45: ("fog", "󰖑", "󰖑"),
    48: ("rime_fog", "", ""),
    51: ("drizzle_light", "", ""),
    53: ("drizzle_moderate", "", ""),
    55: ("drizzle_dense", "", ""),
    61: ("rain_slight", "󰖗", ""),
    63: ("rain_moderate", "󰖗", ""),
    65: ("rain_heavy", "󰖗", ""),
    71: ("snow_slight", "󰼶", ""),
    73: ("snow_moderate", "󰼶", ""),
    75: ("snow_heavy", "󰼶", ""),
    80: ("rain_showers_slight", "󰖖", ""),
    81: ("rain_showers_moderate", "󰖖", ""),
    82: ("rain_showers_violent", "󰖖", ""),
    85: ("snow_showers_slight", "󰖘", ""),
    86: ("snow_showers_heavy", "󰖘", ""),
    95: ("thunderstorm", "󰖓", ""),
    96: ("thunderstorm_hail_slight", "", ""),
    99: ("thunderstorm_hail_heavy", "󰖒", ""),
}
FALLBACK = ("unknown", "", "")


def map_icons(df: pd.DataFrame, is_hourly: bool = False) -> pd.DataFrame:
    def get_icon_desc(row):
        desc, day_i, night_i = WEATHER_ICONS.get(int(row["weather_code"]), FALLBACK)
        icon = night_i if is_hourly and not row.get("is_day", True) else day_i
        return icon, desc

    df[["icon", "description"]] = df.apply(get_icon_desc, axis=1, result_type="expand")
    return df


def today_formatted() -> str:
    t = pd.Timestamp.now()
    day_suffix = {1: "st", 2: "nd", 3: "rd"}.get(t.day % 10, "th")
    if 10 <= t.day % 100 <= 20:
        day_suffix = "th"
    return t.strftime(f"%a, %b {t.day}{day_suffix}, %Y")


def units_handling(hourly_df, daily_df, celsius: bool = False):
    if celsius:
        hourly_df["temperature_2m"] = (hourly_df["temperature_2m"] - 32) * 5 / 9
        daily_df["temperature_2m_max"] = (daily_df["temperature_2m_max"] - 32) * 5 / 9
        daily_df["temperature_2m_min"] = (daily_df["temperature_2m_min"] - 32) * 5 / 9
    hourly_df["temp_str"] = hourly_df.apply(
        lambda row: f"{round(row['temperature_2m'])}/{round(row['temp_low'])}"
        if pd.notnull(row["temp_low"])
        else f"{round(row['temperature_2m'])}",
        axis=1,
    )
    daily_df["temp_str"] = daily_df.apply(
        lambda row: f"{round(row['temperature_2m_max'])}/{round(row['temperature_2m_min'])}"
        if pd.notnull(row["temperature_2m_min"])
        else f"{round(row['temperature_2m_max'])}",
        axis=1,
    )
    threshold = 0.01
    hourly_df["precipitation"] = hourly_df["precipitation"].apply(
        lambda x: x if x >= threshold else 0
    )
    daily_df["precipitation"] = daily_df["precipitation"].apply(
        lambda x: x if x >= threshold else 0
    )
    unit = "cm" if celsius else "in"
    hourly_df["precip_str"] = hourly_df["precipitation"].apply(
        lambda x: f"{x:.1f}{unit}" if x > 0 else ""
    )
    daily_df["precip_str"] = daily_df["precipitation"].apply(
        lambda x: f"{x:.1f}{unit}" if x > 0 else ""
    )
    return hourly_df, daily_df


def add_daytime_flag(
    hourly_df: pd.DataFrame, daily_df: pd.DataFrame, tz: str, step: int
) -> pd.DataFrame:
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

    def is_daytime(row):
        return row["sunrise"] <= row["date"] < row["sunset"]

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
    return hourly_df


@dataclass
class WeatherEntry:
    label: str
    icon: str
    temp: float
    units: str
    sunset_str: str | None = None
    sunrise_str: str | None = None
    temp_low: float | None = None
    precip_prob: int = 0
    precipitation: float = 0.0

    def format(self) -> str:
        t_str = round(self.temp)
        p_prob = f"{self.precip_prob}%" if self.precip_prob > 0 else ""
        p_sum = self.precipitation if self.precipitation > 0.01 else ""
        rain_icon = "󰖌" if self.precip_prob > 0 else ""
        sun_icon = ""
        if self.sunrise_str:
            sun_icon = f"<span size='16pt'>󰖜</span> {self.sunrise_str}"
        elif self.sunset_str:
            sun_icon = f"<span size='16pt'>󰖛</span> {self.sunset_str}"
        else:
            sun_icon = ""
        is_hourly = ":" in self.label
        if is_hourly:
            return (
                f"{self.label:<5}"
                f"<span size='18pt'>{self.icon.rjust(3)}</span>"
                f"{str(t_str).rjust(5)}<span size='17pt'></span>{self.units}"
                f"{rain_icon.rjust(3)}{p_prob.rjust(3)}{str(p_sum).rjust(4)}"
                f"{sun_icon.rjust(3)}"
            )
        else:
            return (
                f"{self.label:<5}"
                f"<span size='18pt'>{self.icon.rjust(3)}</span>"
                f"{str(t_str).rjust(8)}<span size='17pt'></span>{self.units}"
                f"{rain_icon.rjust(3)}{p_prob.rjust(3)} {str(p_sum).rjust(4)}"
            )


def build_tooltip(daily_df, hourly_df, hourly_step=2, celsius=False):
    def proc_entries(entries):
        return "\n".join([entry.format() for entry in entries])

    unit_str = "C" if celsius else "F"
    hourly_entries = [
        WeatherEntry(
            label=row["date"].strftime("%H:%M"),
            icon=row["icon"],
            temp=row["temperature_2m"],
            sunrise_str=row["sunrise_str"],
            sunset_str=row["sunset_str"],
            units=unit_str,
            precip_prob=int(row.get("precipitation_probability", 0)),
            precipitation=row.get("precipitation", 0.0),
        )
        for i, (_, row) in enumerate(hourly_df.head(24).iterrows())
        if i % hourly_step == 0
    ]
    daily_entries = [
        WeatherEntry(
            label=row["date"].strftime("%m-%d"),
            icon=row["icon"],
            temp=row["temperature_2m_max"],
            temp_low=row["temperature_2m_min"],
            units=unit_str,
            precip_prob=int(row.get("precipitation_probability_max", 0)),
            precipitation=row.get("precipitation", 0.0),
        )
        for _, row in daily_df.iterrows()
    ]
    icon_size = 17
    return (
        f"<span size='{icon_size}pt'></span><span size='14pt'> {today_formatted()}</span>\n"
        "─────────────────────────────────────\n"
        + f"{proc_entries(hourly_entries)}"
        + f"\n<span size='{icon_size}pt'>󰨳</span>\n"
        "─────────────────────────────────────\n" + f"{proc_entries(daily_entries)}"
    )


def main():
    daily_df, hourly_df = open_meteo(LATITUDE, LONGITUDE)
    hourly_df = add_daytime_flag(hourly_df, daily_df, TIMEZONE, HOURLY_STEP)
    hourly_df = map_icons(hourly_df, is_hourly=True)
    daily_df = map_icons(daily_df, is_hourly=False)
    tooltip = build_tooltip(daily_df, hourly_df, HOURLY_STEP)
    current = hourly_df.iloc[0]
    output = {
        "text": current.icon,
        "tooltip": tooltip,
        "class": current.description,
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
