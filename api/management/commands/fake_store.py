import json
import random
from django.core.management.base import BaseCommand
from api.models import Store, Product, PriceHistory
from api.services.location.google_maps import Coords

class Command(BaseCommand):
     def handle(self, *args, **kwargs):
        with open("api/data/stores.json", "r") as file:
            raw_stores = json.load(file)
           
        stores = raw_stores["stores"]

        for store_name, locations in stores.items():
            for location in locations:
                coordinates = Coords(location)
            
                store, _ = Store.objects.get_or_create(
                    store_id = random.randint(10_000_000, 99_999_999),
                    name = store_name,
                    location = location,
                    latitude = coordinates[0],
                    longitude = coordinates[1]
                )
