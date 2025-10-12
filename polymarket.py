import re
import requests
import json
import math
from time import sleep


def extract_candidate_name(question_string: str) -> str | None:
    """
    Extracts the candidate's name from a political prediction question string.

    The regex captures the text located between "Will " and " win the 2028 US Presidential Election?".

    Args:
        question_string: The input string (e.g., "Will JD Vance win the 2028 US Presidential Election?").

    Returns:
        The extracted name string, or None if the pattern doesn't match.
    """
    # Regex Breakdown:
    # ^Will\s+: Matches "Will" at the start of the string, followed by one or more whitespace characters.
    # (.*?): This is the CAPTURING GROUP for the name. It matches any character (.), zero or more times (*),
    #        but NON-GREEDILY (?), meaning it stops as soon as it matches the next part of the pattern.
    # \s+win\s+the\s+2028\s+US\s+Presidential\s+Election\?: Matches the fixed end portion of the string.
    # $: Matches the end of the string.
    
    pattern = r'^Will\s+(.*?)\s+win\s+the\s+2028\s+US\s+Presidential\s+Election\?$'
    
    match = re.search(pattern, question_string)
    
    if match:
        # Group 1 (match.group(1)) is the content inside the first parentheses (.*?)
        return match.group(1)
    else:
        return None


class Outcome:
    def __init__(self, name: str, yes: float, no: float):
        self.name = name
        self.yes = yes
        self.no = no
    
    def __str__(self):
        return f"Outcome(name={self.name}, yes={self.yes}, no={self.no})"

    name: str
    yes: float
    no: float


# --- Configuration ---
# The slug is updated to the 2028 Presidential Election market, based on your curl output.
PRESIDENTIAL_ELECTION_EVENT_SLUG = "presidential-election-winner-2028" 
# The API endpoint structure remains correct for looking up events by slug.
API_BASE_URL = "https://gamma-api.polymarket.com/events"
API_URL = f"{API_BASE_URL}/slug/{PRESIDENTIAL_ELECTION_EVENT_SLUG}" 

def fetch_and_summarize_presidential_odds(slug: str) -> dict:
    """
    Fetches the market data for the 2028 Presidential Election (Categorical Market).

    This version is designed to handle a single market with multiple outcomes (candidates),
    extracting the title (candidate name) and price (probability) for each.

    Args:
        slug: The URL slug of the Polymarket event.

    Returns:
        A dictionary mapping candidate name (str) to its odds (float, 0 to 1).
    """
    headers = {
        "Accept": "application/json"
    }

    print(f"-> Searching for Polymarket event: '{slug}' at direct URL: {API_URL}...")

    # Implement exponential backoff for robust API calling
    for attempt in range(4):
        try:
            response = requests.get(API_URL, headers=headers, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            # The response is the full event object containing the markets list.
            event = response.json()
            odds = {}

            # --- UPDATED LOGIC: Search for Outcomes list in all markets ---
            markets = event.get('markets')

            if not isinstance(markets, list) or not markets:
                print(f"Error: 'markets' field is missing or empty for event '{slug}'.")
                return {}
            
            # Iterate through all markets to find the one that contains the outcomes list.
            outcomes: list[Outcome] = []
            for market in markets:
                current_outcomes = market.get('outcomes')
                current_prices = market.get('outcomePrices')
                # Check if outcomes exists, is a list, and is not empty
                if isinstance(current_outcomes, str) and isinstance(current_prices, str) and current_outcomes and current_prices:
                    current_outcomes = json.loads(current_outcomes)
                    current_prices = json.loads(current_prices)
                    name = extract_candidate_name(market.get('question'))
                    yes = 0.0
                    no = 0.0
                    if current_outcomes[0] == 'Yes':
                        yes = float(current_prices[0])
                        no = float(current_prices[1])
                    elif current_outcomes[0] == 'No':
                        no = float(current_prices[0])
                        yes = float(current_prices[1])
                    outcome_obj = Outcome(name=name if name else "Unknown", yes=yes, no=no)
                    outcomes.append(outcome_obj)
            
            if not outcomes:
                print(f"Error: Could not find a valid 'outcomes' list in any market for event '{slug}'.")
                return {}
            
            # Iterate through each candidate outcome found
            for outcome in outcomes:
                odds[outcome.name] = outcome.yes  # Use the 'yes' price as the probability

            # If we successfully populated odds, return them.
            if odds:
                return odds
                
            print(f"Error: No active candidate prices found for event '{slug}'.")
            return {}

        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err} (Status Code: {err.response.status_code})")
            if err.response.status_code == 429:
                # Implement exponential backoff delay (do not log this to console during real run)
                sleep(2**attempt) 
            elif err.response.status_code == 404:
                print(f"Error: Event slug '{slug}' not found (404). Check the slug for correctness.")
                print("Tip: You can find active slugs by checking the Polymarket URL for a live market, e.g., 'https://polymarket.com/event/SLUG-GOES-HERE'")
                return {}
            else:
                return {}
        except requests.exceptions.RequestException as err:
            print(f"An error occurred during the request: {err}")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred during processing: {e}")
            return {}

    print("Failed to fetch data after multiple retries.")
    return {}


def format_odds(odds: dict) -> list[tuple[str, int]]:
    """Prints the extracted odds in a formatted, readable way."""
    if not odds:
        print("\nCould not retrieve odds.")
        return

    # Sort odds from highest probability to lowest
    sorted_odds = sorted(odds.items(), key=lambda item: item[1], reverse=True)

    result: list[tuple[str, int]] = []
    for outcome, probability in sorted_odds:
        percentage = probability * 100
        if percentage % 0.5 == 0:
            percentage = math.ceil(percentage)
        else:
            percentage = round(percentage)
        result.append((outcome, percentage))
    
    return result


def get_2028_presidential_odds() -> list[tuple[str, int]]:
    """Fetch and format the odds for the 2028 presidential election."""
    odds = fetch_and_summarize_presidential_odds("2028-presidential-election")
    return format_odds(odds)


def main() -> None:
    for outcome, percentage in get_2028_presidential_odds():
        print(f"{outcome}: {percentage}%")


if __name__ == "__main__":
    main()
