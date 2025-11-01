# leafs.py
from datetime import datetime
from zoneinfo import ZoneInfo
from time_to import get_time_to_years_str

# Toronto clinched the Cup on May 2, 1967 (Game 6 vs. Montreal).
LEAFS_LAST_CUP = datetime(1967, 5, 2, tzinfo=ZoneInfo("America/Toronto"))

def get_leafs_drought_str() -> str:
    seconds = (datetime.now(ZoneInfo("America/Toronto")) - LEAFS_LAST_CUP).total_seconds()
    return (
        f'It has been {get_time_to_years_str(seconds)} '
        f'since the Toronto Maple Leafs last won the Stanley Cup!'
    )
