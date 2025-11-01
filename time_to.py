def get_time_to_str(target_datetime: int) -> str:
    days, remainder = divmod(target_datetime, 3600 * 24)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    days = int(days)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    duration_str = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
    return duration_str


def get_time_to_years_str(target_datetime: int) -> str:
    years, remainder = divmod(target_datetime, 3600 * 24 * 365)
    days, remainder = divmod(remainder, 3600 * 24)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    years = int(years)
    days = int(days)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    duration_str = f"{years} years, {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
    return duration_str
