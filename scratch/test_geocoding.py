import urllib.request
import urllib.parse
import json

def geocode(q):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(q)}&count=5&country_code=IN"
    req = urllib.request.Request(url, headers={'User-Agent': 'KSHETRA/2.0'})
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read().decode('utf-8'))
        results = data.get("results", [])
        print(f"Query: {q} -> count: {len(results)}")
        for res in results[:2]:
            print(f"  {res.get('name')}, {res.get('admin1')}, Lat: {res.get('latitude')}, Lon: {res.get('longitude')}, Elev: {res.get('elevation')}")

if __name__ == "__main__":
    for place in ["Delhi", "Pune", "Bhubaneswar", "Shimla", "Nashik", "Wayanad"]:
        geocode(place)
