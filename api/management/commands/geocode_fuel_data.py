import time
from django.core.management.base import BaseCommand
from api.models import FuelStop
from api.utils import geocode_address


class Command(BaseCommand):
    help = "Geocode fuel stops and save their locations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delay",
            type=int,
            default=1,
            help="Initial delay in seconds between API calls to avoid rate limiting",
        )
        parser.add_argument(
            "--max_retries",
            type=int,
            default=3,
            help="Maximum number of retries for geocoding requests",
        )

    def handle(self, *args, **kwargs):
        delay = kwargs["delay"]
        max_retries = kwargs["max_retries"]
        fuel_stops = FuelStop.objects.filter(
            latitude__isnull=True, longitude__isnull=True
        )
        for stop in fuel_stops:
            # Try different combinations of address components
            address_combinations = [
                f"{stop.name}",
                f"{stop.city}, {stop.state}",
            ]

            geocoded = False
            for address in address_combinations:
                retries = 0
                while retries < max_retries:
                    try:
                        lat, lon = geocode_address(address)
                        stop.latitude = lat
                        stop.longitude = lon
                        stop.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Geocoded {stop.name} with address '{address}'"
                            )
                        )
                        geocoded = True
                        break
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f"Retrying ..."))
                        break  # Skip to the next address combination if no results are found
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed to geocode {stop.name} with address '{address}': {e}"
                            )
                        )
                        retries += 1
                        time.sleep(delay * (2**retries))  # Exponential backoff
                        if retries == max_retries:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Max retries reached for {stop.name} with address '{address}'"
                                )
                            )
                if geocoded:
                    break  # Stop trying other combinations if geocoding was successful
