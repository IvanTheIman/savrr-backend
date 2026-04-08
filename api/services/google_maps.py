import os
import requests

API_KEY = os.getenv("GOOGLE_API_KEY")

def Coords(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"

    params = {
        "address": address,
        "key": API_KEY
    }

    response = requests.get(url, params = params)
    data = response.json()

    if data["results"]:
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    
    return None, None

def distance(user_coords, store_list_coords, mode = "driving"):
    if not store_list_coords:
        return []
    
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    chunk_size = 25
    all_results = []

    for i in range(0, len(store_list_coords), chunk_size):
        chunk = store_list_coords[i:i + chunk_size]
        destinations = "|".join([f"{lat},{lon}" for lat, lon in chunk])

        params = {
            "origins": f"{user_coords[0]},{user_coords[1]}",
            "destinations": destinations,
            "mode": mode, 
            "units": "imperial",
            "key": API_KEY
        }

        response = requests.get(url, params = params)
        data = response.json()

        results = []
        rows = data.get("rows", [])
        if not rows:
            continue

        elements = rows[0].get("elements", [])
        
        for element in elements:
            if element["status"] == "OK":
                meters = element["distance"]["value"]
                all_results.append({
                    "distance_miles": round(meters * 0.000621371, 2),
                    "distance_text": element["distance"]["text"],
                    "duration_text": element["duration"]["text"],
                })
            else:
                all_results.append(None)

    return all_results