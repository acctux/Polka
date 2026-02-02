import pandas as pd


# tz = "America/New_York"
# print(f"Sunrise (EST):\n{hourly_df['sunrise'].dt.tz_convert(tz)}")
# print(f"Sunset (EST):\n{hourly_df['sunset'].dt.tz_convert(tz)}")
# print(f"Current Date (EST):\n{hourly_df['date'].dt.tz_convert(tz)}")
def format_date():
    today_date = pd.to_datetime("today")
    formatted_date = today_date.strftime("%a, %b. %d, %Y")

    def add_day_suffix(day):
        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return f"{day}{suffix}"

    day_with_suffix = add_day_suffix(today_date.day)
    formatted_date = formatted_date.replace(f"{today_date.day:02}", day_with_suffix)
    return formatted_date


date = format_date()
print(f"{date}")
