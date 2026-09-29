import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
URL = "http://api.aviationstack.com/v1/flights"


def _fetch(dep_iata=None, arr_iata=None):
    """Return (flights, error) for one AviationStack query."""
    params = {"access_key": API_KEY, "limit": 5}
    if dep_iata:
        params["dep_iata"] = dep_iata
    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        data = requests.get(URL, params=params, timeout=15).json()
    except Exception as e:
        return [], f"Flight API request failed: {e}"

    if "error" in data:
        return [], data["error"].get("message", "Flight API error")

    return data.get("data") or [], None


def _format(flight):
    airline = (flight.get("airline") or {}).get("name", "Unknown")
    departure = (flight.get("departure") or {}).get("airport", "Unknown")
    arrival = (flight.get("arrival") or {}).get("airport", "Unknown")
    status = flight.get("flight_status", "Unknown")
    return f"""
Airline: {airline}
Departure: {departure}
Arrival: {arrival}
Status: {status}
"""


def search_flights(query, dep_iata=None, arr_iata=None):
    # AviationStack's free plan only returns today's live/scheduled flights,
    # so an exact route is often empty. Widen the search step by step.
    attempts = [
        (dep_iata, arr_iata, None),
        (None, arr_iata, f"No direct {dep_iata} → {arr_iata} flights today. Showing flights arriving at {arr_iata}:"),
        (dep_iata, None, f"No flights found into {arr_iata} today. Showing flights departing {dep_iata}:"),
    ]

    tried = set()
    for dep, arr, note in attempts:
        if (dep, arr) in tried or (note and not (dep or arr)):
            continue
        tried.add((dep, arr))

        flights, error = _fetch(dep, arr)
        if error:
            return f"Live flight data is unavailable right now ({error})."
        if flights:
            header = f"_{note}_\n" if note else ""
            return header + "\n".join(_format(f) for f in flights[:5])

    return "No live flights found for this route today."
