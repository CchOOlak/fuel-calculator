# api/management/commands/import_fuel_data.py
import csv
from django.core.management.base import BaseCommand
from api.models import FuelStop


class Command(BaseCommand):
    help = "Import fuel price data from a CSV file into the FuelStop model."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="The path to the CSV file containing fuel price data.",
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        try:
            with open(csv_file, "r") as file:
                reader = csv.DictReader(file)
                fuel_stops = []

                for row in reader:
                    fuel_stop = FuelStop(
                        truckstop_id=int(row["OPIS Truckstop ID"]),
                        name=row["Truckstop Name"],
                        address=row["Address"],
                        city=row["City"],
                        state=row["State"],
                        rack_id=int(row["Rack ID"]),
                        retail_price=float(row["Retail Price"]),
                    )
                    fuel_stops.append(fuel_stop)

                FuelStop.objects.bulk_create(fuel_stops)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully imported {len(fuel_stops)} fuel stops."
                    )
                )

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
