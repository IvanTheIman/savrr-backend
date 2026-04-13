import os
from django.core.files import File
from api.models import Product
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "attach images to products based on filename"

    def handle(self, *args, **kwargs):
        folder = "media"

        for file in os.listdir(folder):
            product_id = file.split(".")[0]

            # skip anything that isn't a numeric id
            if not product_id.isdigit():
                self.stdout.write(f"Skipping {file}")
                continue

            try:
                product = Product.objects.get(id=product_id)
                with open(os.path.join(folder, file), "rb") as f:
                    product.image.save(file, File(f), save=True)
                self.stdout.write(f"✓ {file} → {product.name}")

            except Product.DoesNotExist:
                self.stdout.write(f"No product found for id {product_id}")