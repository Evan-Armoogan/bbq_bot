# leafs.py
from datetime import datetime, timezone
from time_to import get_time_to_str

# Toronto clinched the Cup on May 2, 1967 (Game 6 vs. Montreal). :contentReference[oaicite:0]{index=0}
LEAFS_LAST_CUP = datetime(1967, 5, 2, tzinfo=timezone.utc)

def get_leafs_drought_str() -> str:
    seconds = (datetime.now(timezone.utc) - LEAFS_LAST_CUP).total_seconds()
    return (
        f"It has been {get_time_to_str(seconds)} "
        f"since the Toronto Maple Leafs last won the Stanley Cup. Stop coping and accept that this dogshit team will never win anything again. Brad Marchand my goat!"
    )
