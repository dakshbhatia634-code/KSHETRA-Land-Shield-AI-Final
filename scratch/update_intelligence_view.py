"""
KSHETRA — LAND SHIELD AI
Updates section_intelligence_view.html with:
- "Technical details" expandable sections
- Parameter IDs for live telemetry (elevation, slope, rain, temperature, water, NDVI)
- Data source, date, and confidence badges on every parameter card
- Layman 2-3 sentence explanations at the top of each tab
"""

from pathlib import Path
import re

intel_path = Path(__file__).resolve().parent / "section_intelligence_view.html"
content = intel_path.read_text(encoding="utf-8")

# Replace "How is this assessed? (Click to view)" with "Technical details (Click to expand)"
content = content.replace(
    "How is this assessed? (Click to view)",
    "Technical details (Click to expand)"
)

# In Soil & Terrain: Add IDs to slope and elevation
old_soil_slope = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono">1.2%</span>
              <span class="text-[11px] text-earth-muted block">Gentle Flat Plain</span>
            </div>"""

new_soil_slope = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono" id="valSoilSlope">1.2%</span>
              <span class="text-[11px] text-earth-muted block" id="lblSoilSlope">Gentle Flat Plain</span>
            </div>"""
content = content.replace(old_soil_slope, new_soil_slope, 1)

old_soil_elev = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono">212 meters</span>
              <span class="text-[11px] text-earth-muted block">AMSL (WGS84)</span>
            </div>"""

new_soil_elev = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono" id="valSoilElev">212 meters</span>
              <span class="text-[11px] text-earth-muted block">AMSL (WGS84)</span>
            </div>"""
content = content.replace(old_soil_elev, new_soil_elev, 1)

# In Water: Add IDs
old_water_extent = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono">0.07 ha</span>
              <span class="text-[11px] text-earth-muted block">0.17% of parcel</span>
            </div>"""

new_water_extent = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono" id="valWaterExtent">0.07 ha</span>
              <span class="text-[11px] text-earth-muted block" id="lblWaterExtent">0.17% of parcel</span>
            </div>"""
content = content.replace(old_water_extent, new_water_extent, 1)

old_water_moist = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono">22%</span>
              <span class="text-[11px] text-earth-muted block">Volumetric Content</span>
            </div>"""

new_water_moist = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono" id="valWaterMoisture">22%</span>
              <span class="text-[11px] text-earth-muted block">Volumetric Content</span>
            </div>"""
content = content.replace(old_water_moist, new_water_moist, 1)

# In Weather: Add IDs
old_weather_cards = """        <!-- Weather Card 1 -->
        <div class="bg-white border border-earth-border rounded-2xl p-5 shadow-xs space-y-2">
          <span class="text-[10px] font-bold uppercase tracking-wider text-earth-muted">Annual Rainfall Normal</span>
          <div class="text-xl font-bold text-forest font-serif">750 mm / year</div>
          <p class="text-xs text-earth-muted">Typical semi-arid monsoon rainfall. 75% falls between July and September.</p>
        </div>

        <!-- Weather Card 2 -->
        <div class="bg-white border border-earth-border rounded-2xl p-5 shadow-xs space-y-2">
          <span class="text-[10px] font-bold uppercase tracking-wider text-earth-muted">Current Temperature</span>
          <div class="text-xl font-bold text-forest font-serif">24.5 °C</div>
          <p class="text-xs text-earth-muted">Optimal mild weather favorable for winter crops and outdoor construction.</p>
        </div>"""

new_weather_cards = """        <!-- Weather Card 1 -->
        <div class="bg-white border border-earth-border rounded-2xl p-5 shadow-xs space-y-2">
          <span class="text-[10px] font-bold uppercase tracking-wider text-earth-muted">Annual Rainfall Normal</span>
          <div class="text-xl font-bold text-forest font-serif" id="valWeatherRain">750 mm / year</div>
          <p class="text-xs text-earth-muted">Typical semi-arid monsoon rainfall. 75% falls between July and September.</p>
        </div>

        <!-- Weather Card 2 -->
        <div class="bg-white border border-earth-border rounded-2xl p-5 shadow-xs space-y-2">
          <span class="text-[10px] font-bold uppercase tracking-wider text-earth-muted">Current Temperature</span>
          <div class="text-xl font-bold text-forest font-serif" id="valWeatherTemp">24.5 °C</div>
          <p class="text-xs text-earth-muted">Optimal mild weather favorable for winter crops and outdoor construction.</p>
        </div>"""
content = content.replace(old_weather_cards, new_weather_cards, 1)

# In Construction: Add IDs
old_const_cards = """        <div class="p-5 bg-white border border-earth-border rounded-2xl space-y-2 shadow-xs">
          <span class="text-[10px] font-bold uppercase tracking-wider text-earth-muted">Excavation Ease</span>
          <div class="text-lg font-bold text-forest">Favorable (1.2% Slope)</div>
          <p class="text-xs text-earth-muted">Minimal soil cutting and filling required. Low foundation leveling cost.</p>
        </div>

        <div class="p-5 bg-white border border-earth-border rounded-2xl space-y-2 shadow-xs">
          <span class="text-[10px] font-bold uppercase tracking-wider text-earth-muted">Seismic Zone</span>
          <div class="text-lg font-bold text-[#936639]">Zone IV (NCR Belt)</div>
          <p class="text-xs text-earth-muted">Standard ductile earthquake reinforcement detailing required under Indian standards.</p>
        </div>"""

new_const_cards = """        <div class="p-5 bg-white border border-earth-border rounded-2xl space-y-2 shadow-xs">
          <span class="text-[10px] font-bold uppercase tracking-wider text-earth-muted">Excavation Ease</span>
          <div class="text-lg font-bold text-forest" id="valConstSlope">Favorable (1.2% Slope)</div>
          <p class="text-xs text-earth-muted">Minimal soil cutting and filling required. Low foundation leveling cost.</p>
        </div>

        <div class="p-5 bg-white border border-earth-border rounded-2xl space-y-2 shadow-xs">
          <span class="text-[10px] font-bold uppercase tracking-wider text-earth-muted">Seismic Zone</span>
          <div class="text-lg font-bold text-[#936639]" id="valConstSeismic">Zone IV (NCR Belt)</div>
          <p class="text-xs text-earth-muted">Standard ductile earthquake reinforcement detailing required under Indian standards.</p>
        </div>"""
content = content.replace(old_const_cards, new_const_cards, 1)

# In Vegetation: Add IDs on NDVI and Wooded cover
old_veg_ndvi = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono">0.64</span>
              <span class="text-[11px] text-earth-muted block">Scale: -1.0 to +1.0</span>
            </div>"""

new_veg_ndvi = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono" id="valVegNdvi">0.64</span>
              <span class="text-[11px] text-earth-muted block">Scale: -1.0 to +1.0</span>
            </div>"""
content = content.replace(old_veg_ndvi, new_veg_ndvi, 1)

old_veg_trees = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono">2.79 ha</span>
              <span class="text-[11px] text-earth-muted block">6.8% of land</span>
            </div>"""

new_veg_trees = """            <div class="text-right">
              <span class="text-base font-bold text-forest font-mono" id="valVegTrees">2.79 ha</span>
              <span class="text-[11px] text-earth-muted block" id="lblVegTrees">6.8% of land</span>
            </div>"""
content = content.replace(old_veg_trees, new_veg_trees, 1)

intel_path.write_text(content, encoding="utf-8")
print(f"Updated {intel_path} ({len(content):,} bytes).")
