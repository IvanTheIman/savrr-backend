import json
import time
from django.utils.timezone import now
from django.core.management.base import BaseCommand
from api.models import Store, Product, PriceHistory
from api.services.price_randomizer import randomizer


class Command(BaseCommand):
    help = "Generate fake data for app"

    def handle(self, *args, **kwargs):
        with open("api/data/items.json", "r") as file1, open("api/data/stores.json") as file2:
            raw_items = json.load(file1)
            raw_stores = json.load(file2)

        stores = raw_stores["stores"]
        products = raw_items["items"][0]
        for store_name, locations in stores.items():
            for location in locations:
                store, _ = Store.objects.get_or_create(
                    name = store_name,
                    location = location
                )
                for product_name, base_price in products.items():
                    price = randomizer(base_price, store_name)

                    product, _ = Product.objects.get_or_create(
                        name = product_name,
                        defaults = {'product_id': product_name}
                    )
                    pricehistory = PriceHistory.objects.create(
                        product = product,
                        store = store,
                        price = price,
                        date = now()
                    )
                    self.stdout.write(f"Attempting to add {pricehistory}")
                    


       