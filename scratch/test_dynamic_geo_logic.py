"""
Test suite for upgraded dynamic geo.py logic.
"""
import urllib.request
import urllib.parse
import json
import math
from datetime import datetime, timezone

def test_dynamic_endpoints():
    # 1. Geocode Delhi
    q = "Delhi"
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(q)}&count=5&country_code=IN"
    req = urllib.request.Request(url, headers={'User-Agent': 'KSHETRA/2.0'})
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read().decode('utf-8'))
        results = data.get("results", [])
        print(f"Geocoding '{q}': found {len(results)} results")
        assert len(results) > 0, "No results for Delhi"
        lat, lon = results[0]["latitude"], results[0]["longitude"]
        print(f"  Target: {results[0]['name']}, Lat: {lat}, Lon: {lon}")

    # 2. Weather & Soil Moisture
    w_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        f"current=temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m,soil_temperature_0cm,soil_moisture_0_to_1cm&"
        f"timezone=auto"
    )
    req = urllib.request.Request(w_url, headers={'User-Agent': 'KSHETRA/2.0'})
    with urllib.request.urlopen(req, timeout=5) as r:
        w_data = json.loads(r.read().decode('utf-8'))
        curr = w_data.get("current", {})
        print("  Live Weather:", curr.get("temperature_2m"), "°C, humidity:", curr.get("relative_humidity_2m"), "%, soil_moisture:", curr.get("soil_moisture_0_to_1cm"))
        assert curr.get("temperature_2m") is not None

    # 3. Elevation & Slope
    elev_url = f"https://api.open-meteo.com/v1/elevation?latitude={lat},{lat+0.001},{lat}&longitude={lon},{lon},{lon+0.001}"
    req = urllib.request.Request(elev_url, headers={'User-Agent': 'KSHETRA/2.0'})
    with urllib.request.urlopen(req, timeout=5) as r:
        elev_data = json.loads(r.read().decode('utf-8'))
        elevs = elev_data.get("elevation", [])
        print("  Elevations:", elevs)
        assert len(elevs) == 3

    print("\n>> All dynamic endpoint tests passed successfully!")

if __name__ == "__main__":
    test_dynamic_endpoints()
