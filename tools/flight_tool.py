import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")


def search_flights(query, dep_iata=None, arr_iata=None):
    url = "http://api.aviationstack.com/v1/flights"

    params = {
        "access_key": API_KEY,
        "limit": 5
    }
    # Filter by route when airport codes are known
    if dep_iata:
        params["dep_iata"] = dep_iata
    if arr_iata:
        params["arr_iata"] = arr_iata

    response = requests.get(url, params=params)

    data = response.json()

    flights = []

    if "data" in data:

        for flight in data["data"][:5]:

            airline = flight.get("airline", {}).get("name", "Unknown")

            departure = flight.get(
                "departure", {}
            ).get("airport", "Unknown")

            arrival = flight.get(
                "arrival", {}
            ).get("airport", "Unknown")

            status = flight.get("flight_status", "Unknown")

            flights.append(
                f"""
Airline: {airline}
Departure: {departure}
Arrival: {arrival}
Status: {status}
"""
            )

    if not flights:
        return "No live flights found for this route right now."
    return "\n".join(flights)