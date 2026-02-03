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
        code = int(row["weather_code"])
        desc, day_i, night_i = WEATHER_ICONS.get(code, FALLBACK)
        icon = night_i if is_hourly and not row.get("is_day", True) else day_i
        return icon, desc

    df[["icon", "description"]] = df.apply(get_icon_desc, axis=1, result_type="expand")
    return df


def is_daytime(
    hourly_df: pd.DataFrame, daily_df: pd.DataFrame, tz: str
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
    hourly_df["is_day"] = hourly_df["date"].between(
        hourly_df["sunrise"], hourly_df["sunset"], inclusive="left"
    )
    hourly_df["status_change"] = None
    for i in range(1, len(hourly_df)):
        if hourly_df["is_day"].iloc[i] != hourly_df["is_day"].iloc[i - 1]:
            hourly_df.at[i, "status_change"] = "󰖛"  # sunrise/sunset symbol

    return hourly_df


@dataclass
class WeatherEntry:
    label: str
    icon: str
    temp: float  # high (daily) or current (hourly)
    temp_low: float | None = None
    precip_prob: int = 0
    precipitation: float = 0.0
    sun: str | None = None

    def temp_str(self, celsius: bool = False) -> str:
        def conv(f: float) -> int:
            return round((f - 32) * 5 / 9) if celsius else round(f)

        hi = conv(self.temp)
        if self.temp_low is not None:
            lo = conv(self.temp_low)
            return f"{hi}/{lo}"
        return f"{hi}"

    def precip_str(self, celsius: bool = False) -> str:
        if self.precipitation < 0.01:
            return ""
        unit = "cm" if celsius else "in"
        if self.precipitation >= 0.1:
            return f"{self.precipitation:.1f}{unit}"
        return f"{self.precipitation:.2f}{unit}".lstrip("0")

    def format(self, celsius: bool = False) -> str:
        t_str = self.temp_str(celsius)
        unit = "C" if celsius else "F"
        p_prob = f"{self.precip_prob}%" if self.precip_prob > 0 else ""
        p_sum = self.precip_str(celsius)
        rain_icon = "󰖌" if self.precip_prob > 0 or self.precipitation > 0 else ""
        sun_icon = self.sun or ""

        is_hourly = ":" in self.label
        weather_icon = f"{self.icon}".rjust(3)
        if is_hourly:
            return (
                f"{self.label:<5}"
                f"<span size='18pt'>{weather_icon}</span>"
                f"{t_str.rjust(10)}{unit}"
                f"{rain_icon.rjust(3)}{p_prob.rjust(5)} {p_sum.rjust(6)}"
                f"{sun_icon:<3}"
            )
        else:
            return (
                f"{self.label:<5}"
                f"<span size='18pt'>{self.icon.rjust(3)}</span>"
                f"{t_str.rjust(8)}{unit}"
                f"{rain_icon.rjust(3)}{p_prob.rjust(5)} {p_sum.rjust(6)}"
            )


def build_tooltip(daily_df, hourly_df, hourly_step=2, celsius=False):
    daily_entries = [
        WeatherEntry(
            label=row["date"].strftime("%m-%d"),
            icon=row["icon"],
            temp=row["temperature_2m_max"],
            temp_low=row["temperature_2m_min"],
            precip_prob=int(row.get("precipitation_probability_max", 0)),
            precipitation=row.get("precipitation_sum", 0.0),
        )
        for _, row in daily_df.iterrows()
    ]

    hourly_entries = [
        WeatherEntry(
            label=row["date"].strftime("%H:%M"),
            icon=row["icon"],
            temp=row["temperature_2m"],
            precip_prob=int(row.get("precipitation_probability", 0)),
            precipitation=row.get("precipitation", 0.0),
            sun=row.get("status_change"),
        )
        for i, (_, row) in enumerate(hourly_df.head(24).iterrows())
        if i % hourly_step == 0
    ]

    icon_size = 17
    return (
        f"<span size='{icon_size}pt'></span> <span size='14pt'>{today_formatted()}</span>\n"
        "───────────────────────────────────\n"
        f"{' '.join(e.format(celsius) for e in hourly_entries)}\n"
        f"\n<span size='{icon_size}pt'>󰨳</span>\n"
        "───────────────────────────────────\n"
        f"{' '.join(e.format(celsius) for e in daily_entries)}\n"
    )


def today_formatted() -> str:
    t = pd.Timestamp.now()
    day_suffix = {1: "st", 2: "nd", 3: "rd"}.get(t.day % 10, "th")
    if 10 <= t.day % 100 <= 20:
        day_suffix = "th"
    return t.strftime(f"%a, %b {t.day}{day_suffix}, %Y")


def main():
    daily_df, hourly_df = open_meteo(LATITUDE, LONGITUDE)
    hourly_df = is_daytime(hourly_df, daily_df, TIMEZONE)
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
