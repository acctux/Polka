from pydantic.dataclasses import dataclass
import pandas as pd


@dataclass
class WeatherEntry:
    label: str
    icon: str
    temp_high: float
    temp_low: float | None = None
    precip_prob: int = 0
    precipitation: float = 0.0

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
            )
        else:
            return (
                f"{self.label}"
                f"<span size='18pt'>{self.icon.rjust(3)}</span>"
                f"{t.rjust(7)}"
                f"{precip_icon.rjust(2)}"
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


def build_tooltip(
    daily_df: pd.DataFrame,
    hourly_df: pd.DataFrame,
    hourly_step: int = 2,
    celsius: bool = False,
) -> str:
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
    icon_size = 17
    hourly_text = "\n".join(e.format(celsius) for e in hourly_entries)
    daily_text = "\n".join(e.format(celsius) for e in daily_entries)
    today_date = format_date()
    return (
        f"<span size='{icon_size}pt'></span>    <span size='14pt'>{today_date}</span>\n"
        "───────────────────────────────────\n"
        f"{hourly_text}"
        f"\n\n<span size='{icon_size}pt'>󰨳</span>\n"
        "───────────────────────────────────\n"
        f"{daily_text}\n"
    )
