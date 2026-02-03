#!/usr/bin/env python3
from zoneinfo import ZoneInfo
from dataclasses import dataclass
import pandas as pd


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
        if self.sunset_str:
            sun_icon = "󰖛".rjust(2)
            sun_time = f"{self.sunset_str}".rjust(4)
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
