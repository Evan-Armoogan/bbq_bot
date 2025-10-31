from datetime import datetime
from time_to import get_time_to_str


def get_nearest_birthday(birthdays: dict[str, datetime]) -> tuple[str, datetime] | None:
    """
    Returns the name and date of the nearest upcoming birthday from today.

    If multiple birthdays are on the same nearest date, returns one of them.

    Returns:
        A tuple containing the name (str) and date (datetime) of the nearest birthday.
    """
    if len(birthdays) == 0:
        return None

    today = datetime.now()
    current_year = today.year

    nearest_name = None
    nearest_birthday = None
    min_days_until_birthday = float('inf')

    for name, birthday in birthdays.items():
        # Adjust birthday to the current year
        birthday_this_year = birthday.replace(year=current_year)

        # If birthday has already occurred this year, consider next year's birthday
        if birthday_this_year < today:
            birthday_this_year = birthday_this_year.replace(year=current_year + 1)

        days_until_birthday = (birthday_this_year - today).days

        if days_until_birthday < min_days_until_birthday:
            min_days_until_birthday = days_until_birthday
            nearest_name = name
            nearest_birthday = birthday_this_year

    return nearest_name, nearest_birthday


def get_nearest_birthday_str(birthdays: dict[str, datetime]) -> str | None:
    if (result := get_nearest_birthday(birthdays)) is None:
        return None
    name, date = result
    return f"{name}'s birthday is in {get_time_to_str((date - datetime.now()).total_seconds())} on {date.strftime('%B %d, %Y')}."
