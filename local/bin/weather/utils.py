def add_daytime_flag(
    hourly_df: pd.DataFrame, daily_df: pd.DataFrame, tz: str, step: int
) -> pd.DataFrame:
    def is_daytime_at_step(row, next_row, step):
        row_end = row["sunset"]
        if row["sunrise"] <= row["date"] < row_end:
            return True
        return False

    def is_sunrise(row, next_row, step):
        next_row_time = row["date"] + pd.Timedelta(hours=step)
        if row["date"] <= row["sunrise"] < next_row_time:
            return row["sunrise"]
        elif row["date"] <= row["sunset"] < next_row_time:
            return row["sunset"]
        return ""

    def is_sunset(row, next_row, step):
        next_row_time = row["date"] + pd.Timedelta(hours=step)
        if row["date"] <= row["sunrise"] < next_row_time:
            return row["sunrise"]
        elif row["date"] <= row["sunset"] < next_row_time:
            return row["sunset"]
        return ""

    daily_df = daily_df.copy()
    daily_df["sunrise"] = pd.to_datetime(
        daily_df["sunrise"], unit="s", utc=True
    ).dt.tz_convert(ZoneInfo(tz))
    daily_df["sunset"] = pd.to_datetime(
        daily_df["sunset"], unit="s", utc=True
    ).dt.tz_convert(ZoneInfo(tz))
    hourly_df = hourly_df.copy()
    hourly_df["local_date"] = hourly_df["date"].dt.tz_convert(tz).dt.date
    sun_times = daily_df.set_index(daily_df["date"].dt.date)[["sunrise", "sunset"]]
    hourly_df = hourly_df.merge(
        sun_times, left_on="local_date", right_index=True, how="left"
    )
    hourly_df["is_day"] = hourly_df.apply(
        lambda row: is_daytime_at_step(
            row,
            hourly_df.iloc[row.name + 1] if row.name + 1 < len(hourly_df) else row,
            step,
        ),
        axis=1,
    )
    hourly_df["sunrise"] = hourly_df.apply(
        lambda row: is_sunrise(
            row,
            hourly_df.iloc[row.name + 1] if row.name + 1 < len(hourly_df) else row,
            step,
        ),
        axis=1,
    )
    hourly_df["sunset"] = hourly_df.apply(
        lambda row: is_sunset(
            row,
            hourly_df.iloc[row.name + 1] if row.name + 1 < len(hourly_df) else row,
            step,
        ),
        axis=1,
    )
    return hourly_df
