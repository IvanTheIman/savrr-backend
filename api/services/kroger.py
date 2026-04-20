import os
from dotenv import load_dotenv
import requests
import base64
import time
from django.core.management.base import BaseCommand
from api.models import Store, Product, PriceHistory

load_dotenv()


token = None
token_expiration = 0


def get_token_kroger(scope):
    """
    function that takes client id and secret from env file and attempts to make a call to the 
    Kroger product api.
    """
    CLIENT_ID = os.getenv("KROGER_CLIENT_ID")
    CLIENT_SECRET = os.getenv("KROGER_CLIENT_SECRET")
    global token, token_expiration

    if token and time.time() < token_expiration:
        return token

    if not CLIENT_ID or not CLIENT_SECRET:
        print(" KROGER_CLIENT_ID or KROGER_CLIENT_SECRET not set in environment")
        return None

    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    enc_auth = base64.b64encode(auth.encode()).decode()

    response = requests.post(
        "https://api-ce.kroger.com/v1/connect/oauth2/token",
        headers={
            "Authorization": f"Basic {enc_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials", "scope": scope},
    )

    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        token_expiration = time.time() + token_data["expires_in"] - 30
        print("✓ Kroger token obtained")
        return token

    print(f" Token failed {response.status_code}: {response.text}")
    return None



def product_search(term, location_id):
    """
    function that runs once call to Kroger API is successful. takes json response and attempts to format
    into store into store model, each product into product model and each price into price history model,
    while also saving to database
    """
    t = get_token_kroger("product.compact")
    if not t:
        return None

    response = requests.get(
        "https://api-ce.kroger.com/v1/products",
        headers={"Authorization": f"Bearer {t}", "Accept": "application/json"},
        params={
            "filter.term": term,
            "filter.locationId": location_id,
            "filter.limit": 5,
        },
    )

    if response.status_code != 200:
        print(f" Product search failed: {response.status_code}")
        return None

    products = response.json().get("data", [])

    store, _ = Store.objects.get_or_create(
        store_id=location_id,
        defaults={
            "name": "Kroger",
            "location": "701 W Marshall Ave, Longview, TX 75601",
        },
    )

    cheapest_product = None
    cheapest_price = None
    cheapest_unit = None

    for product in products:
        items = product.get("items", [])
        if items:
            price = items[0].get("price", {}).get("regular")
            size = items[0].get("size")
            if price is not None and (cheapest_price is None or price < cheapest_price):
                cheapest_price = price
                cheapest_product = product
                cheapest_unit = size

    if not cheapest_product or cheapest_price is None:
        return []

    product_id = cheapest_product.get("productId")

    db_product, _ = Product.objects.get_or_create(
        product_id=product_id,
        defaults={               
            "name": term,
            "unit": cheapest_unit or "",
        },
    )

    try:
        PriceHistory.objects.create(
            product=db_product,
            store=store,
            price=cheapest_price,
        )
        print(f"✓ Saved: {term} @ ${cheapest_price} ({cheapest_unit})")
    except Exception as e:
        print(f" DB Error: {e}")

    return [{"product_id": product_id, "name": term, "price": cheapest_price, "unit": cheapest_unit}]