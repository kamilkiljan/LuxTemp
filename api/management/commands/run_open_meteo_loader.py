from django.core.management.base import BaseCommand

from loaders.open_meteo_loader import OpenMeteoLoader


class Command(BaseCommand):
    help = "Run the OpenMeteoLoader pipeline."

    def add_arguments(self, parser):
        parser.add_argument("--lat", type=float)
        parser.add_argument("--lon", type=float)
        parser.add_argument("--start_date", type=str)
        parser.add_argument("--end_date", type=str)
        parser.add_argument("--interpolate_missing", action="store_true")

    def handle(self, *args, **options):
        loader = OpenMeteoLoader(
            lat=options["lat"],
            lon=options["lon"],
            start_date=options["start_date"],
            end_date=options["end_date"],
            interpolate_missing=bool(options["interpolate_missing"]),
        )
        loader.run()
