import os
import django
import cloudinary.uploader
from api.models import Product

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grocery_backend.settings')
django.setup()

"""
function that attempts to load images from local storage into cloudinary image cloud service, while also
attempting to save image to product in database
"""
for product in Product.objects.all():
    if not product.image:
        continue
    
    local_path = f"media/{product.image}"
    
    if not os.path.exists(local_path):
        print(f"File not found: {local_path}")
        continue
    
    try:
        result = cloudinary.uploader.upload(
            local_path,
            public_id=f"product/{product.id}",
            overwrite=True
        )
        product.image = result['public_id']
        product.save()
        print(f" Uploaded: {product.name} → {result['public_id']}")
    except Exception as e:
        print(f" Failed {product.name}: {e}")