import sys
sys.path.insert(0, '.')

from backend.routes.geo import search_india_locations, get_environmental_telemetry, get_data_source_registry

print("Calling search_india_locations...")
res = search_india_locations('Delhi')
print(f"Search results: {len(res)}")
for r in res[:2]:
    print(" -", r.name, r.latitude, r.longitude, r.data_state)

print("\nCalling get_environmental_telemetry...")
env = get_environmental_telemetry(28.6139, 77.2090)
print(f"Env temp: {env.temperature_c}°C, state: {env.weather_data_state}")

print("\nCalling get_data_source_registry...")
reg = get_data_source_registry()
print(f"Sources in registry: {len(reg['sources'])}")
for s in reg['sources'][:3]:
    print(" *", s['name'], "->", s['data_state'])

print("\nAll Geo route functions executed successfully!")
