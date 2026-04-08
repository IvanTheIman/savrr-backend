import json
import time
from api.services.kroger import product_search
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "run Kroger searches from JSON file"

    def handle(self, *args, **kwargs):
        with open("api/data/items.json", "r") as file:
            data = json.load(file)

        locations = ["01400943"]

        terms = data["items"]
        for location in locations:
            for item in terms:
                for term in item.keys():
                    results = product_search(term, location)
                    time.sleep(0.5)
                    if results is None:
                        continue
                    self.stdout.write(f"Entered: str{results}")