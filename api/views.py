from django.http import JsonResponse
from .utils import get_route, calculate_fuel_stops, geocode_address


def route_optimizer(request):
    start_address = request.GET.get("start")
    finish_address = request.GET.get("finish")

    if not start_address or not finish_address:
        return JsonResponse(
            {"error": "Start and finish addresses are required."}, status=400
        )

    try:
        # Geocode start and finish addresses
        start_coords = geocode_address(start_address)
        finish_coords = geocode_address(finish_address)

        print(f"Start coordinates: {start_coords}")
        print(f"Finish coordinates: {finish_coords}")

        # Get the route and total distance
        route_geometry, total_distance = get_route(start_coords, finish_coords)
        coordinates = route_geometry["coordinates"]

        # Convert coordinates to [latitude, longitude] pairs
        formatted_coordinates = [[coord[1], coord[0]] for coord in coordinates]

        print(f"Route coordinates: {len(formatted_coordinates)}")

        # Find fuel stops along the route
        fuel_stops, total_cost = calculate_fuel_stops(
            formatted_coordinates, total_distance
        )

        print(f"Total cost: {total_cost}")

        response = {
            "route": formatted_coordinates,
            "fuel_stops": fuel_stops,
            "total_cost": total_cost,
            "total_distance": total_distance,
        }
        return JsonResponse(response)
    except Exception as e:
        print(f"Error in route_optimizer: {e}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)
