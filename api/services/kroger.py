
import os

import requests
import base64
import time
import json
from api.models import Store, Product, PriceHistory

CLIENT_ID = os.getenv("KROGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("KROGER_CLIENT_SECRET")

token = None
token_expiration = 0


def get_token_kroger(scope):
    global token, token_expiration
    
    if token and time.time() < token_expiration:
        return token
    
    
    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    enc_auth = base64.b64encode(auth.encode()).decode()

    print(f"Auth string length: {len(auth)}")
    print(f"Encoded auth (first 20 chars): {enc_auth[:10]}...")

    headers = {
        "Authorization" : f"Basic {enc_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": scope
    }

    response = requests.post(
        "https://api-ce.kroger.com/v1/connect/oauth2/token",
        headers = headers,
        data = data
    )

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        token_expiration = time.time() + token_data["expires_in"] - 30
        print("New token obtained!")
        return token
    else:
        print(f"Test to token failed {response.status_code}")
        return None


def location_search(zip):
    token = get_token_kroger("location.compact")

    if not token:
        return None
    
    headers = {
        "Authorizaton": f"Bearer {token}",
        "Accept": "application/json"
    }

    params = {
        "filter.zipcode.near": zip
    }

    response = requests.get(
        "https://api-ce.kroger.com/v1/locatons",
        headers = headers,
        params = params
    )

    if response.status_code == 200:
        return response.json()
    
    print("location search failed:", response.status_code)
    return None


def product_search(term, location_id):
    token = get_token_kroger("product.compact")

    if not token:
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    params = {
        "filter.term": term,
        "filter.locationId": location_id,
        "filter.limit": 5
    }

    response = requests.get(
        "https://api-ce.kroger.com/v1/products",
        headers = headers,
        params = params
    )

    if response.status_code == 200:
        results =  response.json()
        
        products = results.get('data', [])
    
        store, _ = Store.objects.get_or_create(
            store_id = location_id,
            defaults = {
                "name" : "Kroger",
                "location" : "701 W Marshall Ave, Longview, TX 75601"
            }
        )


        cheapest_product = None
        cheapest_price = None
        cheapest_unit = None

        for product in products:
            items = product.get('items', [])
            if items and len(items) > 0:
                item = items[0]
                price_info = item.get('price', {})
                price = price_info.get('regular')
                size = item.get('size')


                if price is not None and(cheapest_price is None or price < cheapest_price):
                    cheapest_price = price
                    cheapest_product = product
                    cheapest_unit = size
                


        cleaned_results = []

        print(f"Cheapest product: {cheapest_product.get('description') if cheapest_product else 'None'}")  # Debug
        print(f"Cheapest price: {cheapest_price}")
        print(f"Cheapest unit: {cheapest_unit}")

        if cheapest_product and cheapest_price:
            product_id = cheapest_product.get('productId')
            name = cheapest_product.get('description')

            print(f"Attempting to save: {name} at ${cheapest_price}")

            db_product, _ = Product.objects.get_or_create(
                product_id = product_id,
                defaults = {"name": term},
                unit = cheapest_unit
            )

            print(f"Product: {db_product.product_id}")  # Debug
            
            try:
                PriceHistory.objects.create(
                    product = db_product,
                    store = store,
                    price = cheapest_price,
                    date = time.time()
                )
                print("Saved price:", name)
            except Exception as e:
                print("DB Error:", e)
                import traceback
                traceback.print_exc()
        
            cleaned_results.append({
                "product_id" : product_id,
                "name": term,
                "price": cheapest_price,
                "unit": cheapest_unit
            })

        return cleaned_results
    else:
        print(f"Product search failed: {response.status_code}")
        return None

  