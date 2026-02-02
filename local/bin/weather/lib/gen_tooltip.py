import datetime
from pydantic.dataclasses import dataclass
import pandas as pd
from zoneinfo import ZoneInfo


@dataclass
class WeatherEntry:
    label: str
    icon: str
    temp_high: float
    temp_low: float | None = None
    precip_prob: int = 0
    precipitation: float = 0.0

    def temperature_str(
        self, high, low: float | None = None, celsius: bool = False
    ) -> str:
        def conv(f: float, celsius) -> int:
            return round((f - 32) * 5 / 9) if celsius else round(f)

        temp_str = f"{conv(high, celsius)}"
        if low:
            temp_str = f"{conv(high, celsius)}/{conv(low, celsius)}"
        return f"{temp_str}"

    def precip_str(self, celsius: bool) -> str:
        if self.precipitation < 0.01:
            return ""
        unit = "cm" if celsius else "in"
        return (
            f"{self.precipitation:.1f}{unit}"
            if self.precipitation >= 0.1
            else f"{self.precipitation:.2f}{unit}".lstrip("0")
        )

    def format(self, celsius: bool = False) -> str:
        p_prob = f"{self.precip_prob}%" if self.precip_prob > 0 else ""
        p_sum = self.precip_str(celsius)
        precip_icon = "󰖌" if self.precip_prob > 0 or self.precipitation > 0 else ""
        is_hourly = ":" in self.label
        if is_hourly:
            t_hour = self.temperature_str(self.temp_high, celsius)
            return (
                f"{self.label}"
                f"<span size='18pt'>{self.icon.rjust(2)}</span>"
                f"{t_hour.rjust(5)}<span size='16pt'></span>{'C' if celsius else 'F'}"
                f"{precip_icon.rjust(3)}"
                f"{p_prob.rjust(4)} {p_sum.rjust(5)}"
            )
        else:
            t_day = self.temperature_str(self.temp_high, self.temp_low, celsius)
            return (
                f"{self.label}"
                f"<span size='18pt'>{self.icon.rjust(2)}</span>"
                f"{t_day.rjust(8)}<span size='16pt'></span>{'C' if celsius else 'F'}"
                f"{precip_icon.rjust(3)}"
                f"{p_prob.rjust(4)} {p_sum.rjust(5)}"
            )


def format_date():
    today_date = pd.to_datetime("today")
    day = today_date.day

    def add_day_suffix(day):
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        if 10 <= day % 100 <= 20:
            suffix = "th"
        return f"{day}{suffix}"

    day_with_suffix = add_day_suffix(day)
    formatted_date = today_date.strftime(f"%a, %b. {day_with_suffix}, %Y")

    return formatted_date


def is_daytime(sunrise: datetime.datetime, sunset: datetime.datetime, timezone) -> bool:
    current_time = datetime.datetime.now(ZoneInfo(timezone))
    if sunrise.tzinfo is not None:
        current_time = current_time.astimezone(sunrise.tzinfo)
    if sunrise <= current_time <= sunset:
        return True
    return False


def build_tooltip(
    daily_df: pd.DataFrame,
    hourly_df: pd.DataFrame,
    timezone: str,
    hourly_step: int = 2,
    celsius: bool = False,
) -> str:
    # Create Daily Entries
    hourly_entries = [
        WeatherEntry(
            label=row["date"].strftime("%H:%M"),
            icon=row["icon"],
            temp_high=row["temperature_2m"],
            precip_prob=int(row["precipitation_probability"]),
            precipitation=row["precipitation"],
        )
        for idx, (_, row) in enumerate(hourly_df.head(24).iterrows())
        if idx % hourly_step == 0
    ]

    # Add sunrise and sunset information to hourly_entries
    hourly_text = ""
    for e, (_, row) in zip(hourly_entries, hourly_df.head(24).iterrows()):
        time_str = e.format(celsius)
        sunrise_time = row.get("sunrise", None)
        sunset_time = row.get("sunset", None)

        if sunrise_time and sunset_time:
            # Check if current time is between sunrise and sunset
            if is_daytime(sunrise_time, sunset_time, timezone):
                # Format sunrise/sunset to a readable string (e.g., "06:15 AM")
                sunrise_str = sunrise_time.strftime("%I:%M %p")
                sunset_str = sunset_time.strftime("%I:%M %p")
                # Append sunrise and sunset info to the hourly entry
                hourly_text += (
                    f"{time_str} | Sunrise: {sunrise_str} | Sunset: {sunset_str}\n"
                )
            else:
                # If not daytime, show a different message or omit sunrise/sunset info
                hourly_text += f"{time_str} | Daytime has passed\n"
        else:
            hourly_text += f"{time_str} | Sunrise/Sunset data unavailable\n"

    # Create Daily Entries
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

    icon_size = 17
    daily_text = "\n".join(e.format(celsius) for e in daily_entries)
    today_date = format_date()

    return (
        f"<span size='{icon_size}pt'></span>      <span size='13pt'>{today_date}</span>\n"
        "───────────────────────────────────\n"
        f"{hourly_text}"
        f"\n\n<span size='{icon_size}pt'>󰨳</span>\n"
        "───────────────────────────────────\n"
        f"{daily_text}\n"
    )
