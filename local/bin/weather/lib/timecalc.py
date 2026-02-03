from zoneinfo import ZoneInfo
import pandas as pd


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


def add_day_suffix(day: int) -> str:
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    if 10 <= day % 100 <= 20:
        suffix = "th"
    return f"{day}{suffix}"


def format_date() -> str:
    today_date = pd.to_datetime("today")
    day_with_suffix = add_day_suffix(today_date.day)
    return today_date.strftime(f"%a, %b. {day_with_suffix}, %Y")


def adjust_sunrise_sunset_times(daily_df: pd.DataFrame, timezone: str) -> pd.DataFrame:
    daily_df["sunrise"] = pd.to_datetime(
        daily_df["sunrise"], unit="s", utc=True
    ).dt.tz_convert(ZoneInfo(timezone))
    daily_df["sunset"] = pd.to_datetime(
        daily_df["sunset"], unit="s", utc=True
    ).dt.tz_convert(ZoneInfo(timezone))
    return daily_df


def add_day_night_flag(
    hourly_df: pd.DataFrame, daily_df: pd.DataFrame, timezone: str
) -> pd.DataFrame:
    daily_df = adjust_sunrise_sunset_times(daily_df, timezone)
    hourly_df["local_date"] = hourly_df["date"].dt.tz_convert(timezone).dt.date
    sun_times = daily_df.set_index(daily_df["date"].dt.date)[["sunrise", "sunset"]]
    hourly_df = hourly_df.merge(
        sun_times, left_on="local_date", right_index=True, how="left"
    )
    hourly_df = hourly_df.drop(columns=["local_date"])
    hourly_df["sunrise"] = pd.to_datetime(hourly_df["sunrise"])
    hourly_df["sunset"] = pd.to_datetime(hourly_df["sunset"])
    hourly_df["is_day"] = hourly_df["date"].between(
        hourly_df["sunrise"], hourly_df["sunset"], inclusive="left"
    )
    return hourly_df


def is_daytime_to_local_dataframe(
    daily_df: pd.DataFrame, hourly_df: pd.DataFrame, timezone: str
) -> pd.DataFrame:
    daily_df = adjust_sunrise_sunset_times(daily_df, timezone)
    daily_days = pd.to_datetime(daily_df["sunrise"]).dt.date
    hourly_df["sunrise"] = hourly_df["date"].dt.date.map(
        dict(zip(daily_days, daily_df["sunrise"]))
    )
    hourly_df["sunset"] = hourly_df["date"].dt.date.map(
        dict(zip(daily_days, daily_df["sunset"]))
    )
    hourly_df["is_daytime"] = hourly_df["date"].between(
        hourly_df["sunrise"], hourly_df["sunset"], inclusive="left"
    )
    hourly_df["status_change"] = ""
    for idx in range(1, len(hourly_df)):
        if hourly_df["is_daytime"].iloc[idx] != hourly_df["is_daytime"].iloc[idx - 1]:
            hourly_df.at[idx - 1, "status_change"] = hourly_df["sunrise"].iloc[idx]
            hourly_df.at[idx, "status_change"] = "󰖜"
    return hourly_df
