import os
import requests
from geopy.distance import geodesic
from rdp import rdp
from scipy.spatial import KDTree


from .models import FuelStop


ORS_API_KEY = os.getenv("ORS_API_KEY")
ROUTING_API_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
GEOCODING_API_URL = "https://api.openrouteservice.org/geocode/search"
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = os.getenv("USER_AGENT")


def get_route(start_coords, finish_coords):
    params = {
        "api_key": ORS_API_KEY,
        "start": f"{start_coords[1]},{start_coords[0]}",
        "end": f"{finish_coords[1]},{finish_coords[0]}",
    }
    response = requests.get(ROUTING_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            route_geometry = data["features"][0]["geometry"]
            total_distance_meters = data["features"][0]["properties"]["segments"][0][
                "distance"
            ]
            total_distance_miles = (
                total_distance_meters * 0.000621371
            )  # Convert meters to miles

            return route_geometry, total_distance_miles
        else:
            raise ValueError(f"Failed to get route: No route found")
    else:
        raise ValueError(f"Failed to get route: {response.text}")


def geocode_address(address):
    headers = {"User-Agent": USER_AGENT}
    params = {"q": address, "format": "json", "limit": 1}
    response = requests.get(NOMINATIM_API_URL, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            coordinates = data[0]
            return float(coordinates["lat"]), float(coordinates["lon"])
        else:
            raise ValueError(
                f"Failed to geocode address: No results found for {address}"
            )
    else:
        raise ValueError(f"Failed to geocode address: {response.text}")


def simplify_route(route_coordinates, epsilon=0.01):
    return rdp(route_coordinates, epsilon=epsilon)


def calculate_fuel_stops(route_coordinates, total_distance):
    max_range = 500  # miles
    mpg = 10  # miles per gallon
    fuel_stops = []
    total_cost = 0

    # Simplify the route to reduce the number of points
    simplified_route = simplify_route(route_coordinates, epsilon=0.1)

    # Create a list of fuel stop coordinates and prices
    fuel_stop_data = [
        (stop.latitude, stop.longitude, stop.retail_price, stop)
        for stop in FuelStop.objects.all()
    ]
    fuel_stop_coords = [(lat, lon) for lat, lon, price, stop in fuel_stop_data]
    fuel_stop_tree = KDTree(fuel_stop_coords)

    # Calculate fuel prices for each segment of the simplified route
    segment_prices = []
    for i in range(len(simplified_route) - 1):
        current_position = simplified_route[i]
        next_position = simplified_route[i + 1]
        segment_distance = geodesic(current_position, next_position).miles

        # Find the nearest fuel stop using KD-Tree
        _, idx = fuel_stop_tree.query(current_position)
        nearest_stop = fuel_stop_data[idx][3]

        segment_prices.append(
            (segment_distance, nearest_stop.retail_price, nearest_stop)
        )

    # Use dynamic programming to find the optimal fuel stops
    n = len(segment_prices)
    dp = [float("inf")] * (n + 1)
    dp[0] = 0
    path = [-1] * (n + 1)

    for i in range(n):
        distance_covered = 0
        for j in range(i, n):
            distance_covered += segment_prices[j][0]
            if distance_covered > max_range:
                break
            cost = (distance_covered / mpg) * segment_prices[j][1]
            if dp[i] + cost < dp[j + 1]:
                dp[j + 1] = dp[i] + cost
                path[j + 1] = i

    # Reconstruct the path and calculate fuel amounts
    idx = n
    while idx != 0:
        if path[idx] != -1:
            distance_to_next_stop = sum(
                segment_prices[k][0] for k in range(path[idx], idx)
            )
            fuel_amount = distance_to_next_stop / mpg
            fuel_stops.append(
                {
                    "name": segment_prices[path[idx]][2].name,
                    "address": segment_prices[path[idx]][2].address,
                    "city": segment_prices[path[idx]][2].city,
                    "state": segment_prices[path[idx]][2].state,
                    "price": segment_prices[path[idx]][2].retail_price,
                    "latitude": segment_prices[path[idx]][2].latitude,
                    "longitude": segment_prices[path[idx]][2].longitude,
                    "fuel_amount": fuel_amount,
                }
            )
        idx = path[idx]

    fuel_stops.reverse()
    total_cost = dp[n]

    return fuel_stops, total_cost
