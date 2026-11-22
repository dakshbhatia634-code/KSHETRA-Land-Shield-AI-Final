"""
Fixes:
1. Injects #registryModal, #savedPlacesDrawer, #savePlaceModal, #authProfileModal before #techModal
2. Polishes header brand block with whitespace-nowrap
3. Ensures reverseGeocodeMapClick updates hero titles immediately
"""

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Polish header brand block
old_brand_block = '''      <!-- Brand Logo, KSHETRA Title & Commercial Tagline -->
      <div class="flex items-center space-x-3.5">
        <!-- Shield + Nature Sprout SVG Logo -->
        <a href="#heroSection" class="w-12 h-12 rounded-2xl bg-forest flex items-center justify-center shadow-md shadow-forest/20 text-white shrink-0 hover:bg-forest-dark transition">
          <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <!-- Outer Shield Contour -->
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <!-- Interior Leaf Sprout & Terrain Contour Lines -->
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-3 1.5-4 4.5-4 7m4-7c3 1.5 4 4.5 4 7m-4-7v7" stroke-width="1.8" />
          </svg>
        </a>
        <div>
          <div class="flex items-baseline space-x-2.5">
            <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-forest-dark font-serif">KSHETRA</h1>
            <span class="text-[11px] font-extrabold tracking-wider text-earth-dark uppercase">Land Shield AI</span>
            <span class="hidden md:inline-block text-[10px] font-bold tracking-wide px-2 py-0.5 rounded-full bg-sand-light text-forest-dark border border-sand-dark/40">
              Earth Intelligence SaaS
            </span>
          </div>
          <p class="text-xs text-earth-muted font-medium mt-0.5 flex items-center space-x-1.5">
            <span class="italic font-serif text-earth-dark/90">Verifying Titles. Securing Boundaries.</span>
            <span class="hidden lg:inline text-earth-border">•</span>
            <span class="hidden lg:inline">Understand the land. Make informed decisions.</span>
          </p>
        </div>
      </div>'''

new_brand_block = '''      <!-- Brand Logo, KSHETRA Title & Commercial Tagline -->
      <div class="flex items-center space-x-3 shrink-0">
        <!-- Shield + Nature Sprout SVG Logo -->
        <a href="#heroSection" class="w-11 h-11 rounded-2xl bg-forest flex items-center justify-center shadow-md shadow-forest/20 text-white shrink-0 hover:bg-forest-dark transition">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <!-- Outer Shield Contour -->
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <!-- Interior Leaf Sprout & Terrain Contour Lines -->
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-3 1.5-4 4.5-4 7m4-7c3 1.5 4 4.5 4 7m-4-7v7" stroke-width="1.8" />
          </svg>
        </a>
        <div class="leading-tight shrink-0">
          <div class="flex items-center space-x-2 whitespace-nowrap">
            <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-forest-dark font-serif">KSHETRA</h1>
            <span class="text-[10px] font-extrabold tracking-wider text-earth-dark uppercase">Land Shield AI</span>
            <span class="hidden 2xl:inline-block text-[10px] font-bold tracking-wide px-2 py-0.5 rounded-full bg-sand-light text-forest-dark border border-sand-dark/40">
              Earth Intelligence
            </span>
          </div>
          <p class="text-[11px] text-earth-muted font-medium mt-0.5 whitespace-nowrap">
            <span class="italic font-serif text-earth-dark/90">Verifying Titles. Securing Boundaries.</span>
          </p>
        </div>
      </div>'''

if old_brand_block in html:
    html = html.replace(old_brand_block, new_brand_block, 1)

# 2. Insert the 4 Modals right before <!-- TECHNICAL DIAGNOSTICS MODAL -->
modals_html = '''  <!-- ========================================================================= -->
  <!-- 8. KSHETRA DATA PROVENANCE REGISTRY MODAL (#registryModal)                  -->
  <!-- ========================================================================= -->
  <div id="registryModal" class="hidden fixed inset-0 z-50 overflow-y-auto bg-earth-dark/40 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6" onclick="if(event.target === this) closeRegistryModal()">
    <div class="bg-white border border-earth-border rounded-3xl max-w-4xl w-full p-6 sm:p-8 shadow-2xl relative space-y-6 my-auto max-h-[90vh] overflow-y-auto">
      <!-- Modal Header -->
      <div class="flex items-start justify-between border-b border-earth-border pb-4">
        <div>
          <div class="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-sand-light border border-sand-dark/40 text-[10px] font-bold text-forest uppercase tracking-wider mb-1">
            Official Data Provenance
          </div>
          <h3 class="text-xl sm:text-2xl font-bold text-forest-dark font-serif">KSHETRA Data Source Registry</h3>
          <p class="text-xs text-earth-muted mt-0.5">Transparent provenance, resolution, licensing, and operational status for all underlying feeds.</p>
        </div>
        <button onclick="closeRegistryModal()" class="w-8 h-8 rounded-full bg-sand-light hover:bg-sand text-earth-dark flex items-center justify-center transition font-bold text-base">&times;</button>
      </div>

      <!-- Provenance Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-earth-border bg-earth-cardTint text-earth-dark font-bold uppercase tracking-wider text-[10px]">
              <th class="py-2.5 px-3">Provider & Dataset</th>
              <th class="py-2.5 px-3">Domain Category</th>
              <th class="py-2.5 px-3">Spatial Resolution</th>
              <th class="py-2.5 px-3">Data State & License</th>
              <th class="py-2.5 px-3">Operational Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-earth-border/60 text-earth-text">
            <tr class="hover:bg-sand-light/30 transition">
              <td class="py-3 px-3">
                <span class="font-bold text-forest-dark block">ESA Copernicus Sentinel-2</span>
                <span class="text-[11px] text-earth-muted">MSI Level-2A Surface Reflectance</span>
              </td>
              <td class="py-3 px-3">Land-Cover Neural Segmentation</td>
              <td class="py-3 px-3 font-mono">10.0m GSD (40.96 ha)</td>
              <td class="py-3 px-3">
                <span class="inline-block px-2 py-0.5 rounded-md bg-forest/10 text-forest font-bold text-[10px] mb-0.5">Verified / Model Inferred</span>
                <span class="text-[10px] text-earth-muted block">CC-BY 4.0 Open Access</span>
              </td>
              <td class="py-3 px-3"><span class="text-forest font-bold">● Active (PyTorch CUDA)</span></td>
            </tr>
            <tr class="hover:bg-sand-light/30 transition">
              <td class="py-3 px-3">
                <span class="font-bold text-forest-dark block">OpenStreetMap Contributors</span>
                <span class="text-[11px] text-earth-muted">Nominatim Geocoder & Overpass</span>
              </td>
              <td class="py-3 px-3">Geocoding & Administrative Borders</td>
              <td class="py-3 px-3 font-mono">Vector / Village Level</td>
              <td class="py-3 px-3">
                <span class="inline-block px-2 py-0.5 rounded-md bg-forest/10 text-forest font-bold text-[10px] mb-0.5">Verified</span>
                <span class="text-[10px] text-earth-muted block">ODbL 1.0</span>
              </td>
              <td class="py-3 px-3"><span class="text-forest font-bold">● Active (Real-Time Search)</span></td>
            </tr>
            <tr class="hover:bg-sand-light/30 transition">
              <td class="py-3 px-3">
                <span class="font-bold text-forest-dark block">Open-Meteo Weather Services</span>
                <span class="text-[11px] text-earth-muted">Global High-Resolution Forecast Grid</span>
              </td>
              <td class="py-3 px-3">Meteorology & Real-Time Rain</td>
              <td class="py-3 px-3 font-mono">1.0 km – 11.0 km Grid</td>
              <td class="py-3 px-3">
                <span class="inline-block px-2 py-0.5 rounded-md bg-forest/10 text-forest font-bold text-[10px] mb-0.5">Verified / Live</span>
                <span class="text-[10px] text-earth-muted block">CC-BY 4.0 Open Data</span>
              </td>
              <td class="py-3 px-3"><span class="text-forest font-bold">● Active (Telemetry API)</span></td>
            </tr>
            <tr class="hover:bg-sand-light/30 transition">
              <td class="py-3 px-3">
                <span class="font-bold text-forest-dark block">NASA / USGS SRTM</span>
                <span class="text-[11px] text-earth-muted">Shuttle Radar Topography Mission</span>
              </td>
              <td class="py-3 px-3">Digital Elevation Model & Slope</td>
              <td class="py-3 px-3 font-mono">1 Arc-Second (~30m)</td>
              <td class="py-3 px-3">
                <span class="inline-block px-2 py-0.5 rounded-md bg-sand-dark/20 text-[#936639] font-bold text-[10px] mb-0.5">Estimated</span>
                <span class="text-[10px] text-earth-muted block">NASA Public Domain</span>
              </td>
              <td class="py-3 px-3"><span class="text-forest font-bold">● Active</span></td>
            </tr>
            <tr class="hover:bg-sand-light/30 transition">
              <td class="py-3 px-3">
                <span class="font-bold text-forest-dark block">India Meteorological Dept (IMD)</span>
                <span class="text-[11px] text-earth-muted">30-Year Climate Normals (1991–2020)</span>
              </td>
              <td class="py-3 px-3">Seasonal Monsoon & Baseline Normals</td>
              <td class="py-3 px-3 font-mono">District Station Network</td>
              <td class="py-3 px-3">
                <span class="inline-block px-2 py-0.5 rounded-md bg-forest/10 text-forest font-bold text-[10px] mb-0.5">Verified Reference</span>
                <span class="text-[10px] text-earth-muted block">Govt of India Open Data</span>
              </td>
              <td class="py-3 px-3"><span class="text-forest font-bold">● Calibrated Baseline</span></td>
            </tr>
            <tr class="hover:bg-sand-light/30 transition">
              <td class="py-3 px-3">
                <span class="font-bold text-forest-dark block">State Revenue Depts (Jamabandi/Bhulekh)</span>
                <span class="text-[11px] text-earth-muted">Cadastral Deeds & Ownership Title</span>
              </td>
              <td class="py-3 px-3">Property Deeds & Boundary Non-Encumbrance</td>
              <td class="py-3 px-3 font-mono">Khasra / Parcel Level</td>
              <td class="py-3 px-3">
                <span class="inline-block px-2 py-0.5 rounded-md bg-terracotta/10 text-terracotta font-bold text-[10px] mb-0.5">Data Unavailable</span>
                <span class="text-[10px] text-earth-muted block">Official Land Records Required</span>
              </td>
              <td class="py-3 px-3"><span class="text-terracotta font-bold">○ Explicit Gap (Field Verification)</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Scientific Disclaimer Footer -->
      <div class="bg-sand-light/40 border border-sand-dark/30 rounded-2xl p-4 text-xs text-earth-muted space-y-1">
        <p class="font-bold text-earth-dark">Scientific Integrity & Zero-Fabrication Guarantee:</p>
        <p>KSHETRA never fabricates private land titles, subterranean chemical soil nutrients, or live rain gauge measurements. All satellite metrics represent remote physical observations calibrated from 10m Sentinel-2 multispectral reflectance and official public APIs.</p>
      </div>
    </div>
  </div>

  <!-- ========================================================================= -->
  <!-- 9. MY PLACES (SAVED LOCATIONS) SLIDE-OVER DRAWER (#savedPlacesDrawer)       -->
  <!-- ========================================================================= -->
  <div id="savedPlacesDrawer" class="hidden fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white border-l border-earth-border shadow-2xl flex flex-col justify-between">
    <!-- Header -->
    <div class="p-5 border-b border-earth-border flex items-center justify-between bg-earth-cardTint">
      <div class="flex items-center space-x-2.5">
        <div class="w-8 h-8 rounded-xl bg-forest text-white flex items-center justify-center font-bold">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-bold text-earth-dark">My Places</h3>
          <p class="text-[11px] text-earth-muted">Persisted Saved Locations & Survey Footprints</p>
        </div>
      </div>
      <button onclick="closeSavedPlacesDrawer()" class="text-earth-muted hover:text-earth-dark text-lg font-bold p-1">&times;</button>
    </div>

    <!-- Saved Places List / Empty State -->
    <div id="savedPlacesContent" class="flex-1 overflow-y-auto p-5 space-y-3">
      <!-- Dynamically populated or empty state rendered here -->
    </div>

    <!-- Drawer Footer -->
    <div class="p-4 border-t border-earth-border bg-earth-cardTint flex items-center justify-between text-xs">
      <span id="savedPlacesTotalLabel" class="text-earth-muted font-medium">0 saved parcels</span>
      <button onclick="promptSaveCurrentLocation()" class="px-3 py-1.5 bg-forest hover:bg-forest-dark text-white rounded-xl font-bold transition shadow-2xs">
        + Save Current Location
      </button>
    </div>
  </div>

  <!-- ========================================================================= -->
  <!-- 10. SAVE PLACE DIALOG MODAL (#savePlaceModal)                              -->
  <!-- ========================================================================= -->
  <div id="savePlaceModal" class="hidden fixed inset-0 z-50 overflow-y-auto bg-earth-dark/40 backdrop-blur-xs flex items-center justify-center p-4" onclick="if(event.target === this) closeSavePlaceModal()">
    <div class="bg-white border border-earth-border rounded-3xl max-w-sm w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-earth-border pb-3">
        <h3 class="text-sm font-bold text-forest-dark flex items-center space-x-2">
          <span>⭐ Save Location to My Places</span>
        </h3>
        <button onclick="closeSavePlaceModal()" class="text-earth-muted hover:text-earth-dark text-base">&times;</button>
      </div>
      <div class="space-y-3 text-xs">
        <div>
          <label class="block font-bold text-earth-dark mb-1">Custom Parcel Label:</label>
          <input id="savePlaceNameInput" type="text" class="w-full px-3 py-2 border border-earth-border rounded-xl focus:border-forest outline-none text-xs text-earth-dark" placeholder="e.g. Faridabad Commercial Plot 4" />
        </div>
        <div>
          <label class="block font-bold text-earth-dark mb-1">Notes / Due Diligence Tags:</label>
          <textarea id="savePlaceNotesInput" rows="2" class="w-full px-3 py-2 border border-earth-border rounded-xl focus:border-forest outline-none text-xs text-earth-dark" placeholder="e.g. Good road frontage, verify groundwater depth..."></textarea>
        </div>
        <div class="text-[11px] text-earth-muted bg-sand-light/50 p-2.5 rounded-xl border border-sand-dark/30 font-mono">
          <span id="savePlaceCoordLabel">Lat: -- | Lon: --</span>
        </div>
      </div>
      <div class="flex items-center justify-end space-x-2 pt-2 border-t border-earth-border">
        <button onclick="closeSavePlaceModal()" class="px-3 py-1.5 text-xs font-semibold text-earth-muted hover:text-earth-dark">Cancel</button>
        <button onclick="confirmSavePlace()" class="px-4 py-1.5 bg-forest hover:bg-forest-dark text-white rounded-xl text-xs font-bold transition shadow-xs">Save Place</button>
      </div>
    </div>
  </div>

  <!-- ========================================================================= -->
  <!-- 11. USER PROFILE, AUTH & SETTINGS MODAL (#authProfileModal)                 -->
  <!-- ========================================================================= -->
  <div id="authProfileModal" class="hidden fixed inset-0 z-50 overflow-y-auto bg-earth-dark/40 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6" onclick="if(event.target === this) closeAuthModal()">
    <div class="bg-white border border-earth-border rounded-3xl max-w-md w-full p-6 sm:p-7 shadow-2xl relative space-y-5 my-auto">
      <!-- Modal Header -->
      <div class="flex items-start justify-between border-b border-earth-border pb-3">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-2xl bg-forest text-white font-bold flex items-center justify-center font-serif text-lg">K</div>
          <div>
            <h3 class="text-base font-bold text-forest-dark font-serif">Account & Preferences</h3>
            <p class="text-[11px] text-earth-muted">KSHETRA Earth Intelligence Platform</p>
          </div>
        </div>
        <button onclick="closeAuthModal()" class="w-7 h-7 rounded-full bg-sand-light hover:bg-sand text-earth-dark flex items-center justify-center transition font-bold text-sm">&times;</button>
      </div>

      <!-- Tabs: Profile | Settings | Auth -->
      <div class="flex border-b border-earth-border text-xs font-bold text-earth-muted">
        <button onclick="switchAuthSubTab('profile')" id="btnAuthTab_profile" class="pb-2 px-3 text-forest border-b-2 border-forest">Profile</button>
        <button onclick="switchAuthSubTab('settings')" id="btnAuthTab_settings" class="pb-2 px-3 hover:text-earth-dark">Settings</button>
        <button onclick="switchAuthSubTab('auth')" id="btnAuthTab_auth" class="pb-2 px-3 hover:text-earth-dark">Cloud Sync</button>
      </div>

      <!-- Tab Content: Profile -->
      <div id="authPanel_profile" class="space-y-3 text-xs">
        <div class="bg-sand-light/50 border border-sand-dark/40 rounded-2xl p-4 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-earth-dark">User Identity:</span>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-forest/10 text-forest">Local Session</span>
          </div>
          <div class="text-earth-dark text-sm font-semibold">Geospatial Surveyor (Demo User)</div>
          <div class="text-[11px] text-earth-muted">Identity Tier: Earth Observation Professional</div>
        </div>
        <div class="space-y-2 pt-1 text-earth-muted">
          <div class="flex justify-between py-1 border-b border-earth-border/50">
            <span>Hardware Compute:</span>
            <span class="font-mono font-bold text-forest">NVIDIA RTX 3050 CUDA</span>
          </div>
          <div class="flex justify-between py-1 border-b border-earth-border/50">
            <span>Spatial Coverage:</span>
            <span class="font-semibold text-earth-dark">Republic of India</span>
          </div>
          <div class="flex justify-between py-1">
            <span>Satellite Neural Model:</span>
            <span class="font-mono text-earth-dark">SatelliteUNet (mIoU 0.4839)</span>
          </div>
        </div>
      </div>

      <!-- Tab Content: Settings -->
      <div id="authPanel_settings" class="hidden space-y-3 text-xs">
        <div>
          <label class="block font-bold text-earth-dark mb-1">Area Measurement Unit:</label>
          <select id="settingUnitSelect" class="w-full px-3 py-2 border border-earth-border rounded-xl text-xs bg-white text-earth-dark">
            <option value="ha">Hectares (Standard European / Metric)</option>
            <option value="acre">Acres (Regional Farmland Benchmark)</option>
            <option value="bigha">Bighas (North Indian Agricultural Reference)</option>
          </select>
        </div>
        <div>
          <label class="block font-bold text-earth-dark mb-1">Default Basemap Style:</label>
          <select id="settingMapSelect" onchange="setMapLayer(this.value)" class="w-full px-3 py-2 border border-earth-border rounded-xl text-xs bg-white text-earth-dark">
            <option value="satellite">Esri World Imagery (0.3m Satellite)</option>
            <option value="dark">Esri Dark Canvas (Contrast Focus)</option>
            <option value="osm">OpenStreetMap Standard</option>
          </select>
        </div>
        <div class="flex items-center justify-between pt-2">
          <span class="font-bold text-earth-dark">Reduced Motion Animations:</span>
          <input type="checkbox" id="settingReducedMotion" class="w-4 h-4 text-forest rounded" />
        </div>
      </div>

      <!-- Tab Content: Auth / Cloud Sync -->
      <div id="authPanel_auth" class="hidden space-y-3 text-xs">
        <div class="bg-forest/5 border border-forest/20 rounded-2xl p-4 text-earth-dark space-y-2">
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-forest"></span>
            <span class="font-bold text-forest-dark">Authentication Status: Local Storage Mode</span>
          </div>
          <p class="text-[11px] text-earth-muted">All saved places, history, and survey preferences are stored securely in your browser's private local storage. No unauthenticated data leaves this machine.</p>
        </div>
        <div class="p-3 bg-sand-light/50 border border-sand-dark/30 rounded-xl space-y-1 text-[11px] text-earth-muted">
          <span class="font-bold text-earth-dark">Supabase Cloud Sync Readiness:</span>
          <p>KSHETRA is configured for instant connection with Supabase Auth or PostgreSQL. Provide your <code>SUPABASE_URL</code> and <code>SUPABASE_KEY</code> in environment variables when cloud multi-tenant sync is required.</p>
        </div>
      </div>

      <!-- Footer -->
      <div class="pt-3 border-t border-earth-border flex items-center justify-end">
        <button onclick="closeAuthModal()" class="px-4 py-2 bg-forest hover:bg-forest-dark text-white rounded-xl text-xs font-bold transition shadow-xs">Done</button>
      </div>
    </div>
  </div>
'''

target_marker = '  <!-- ========================================================================= -->\n  <!-- TECHNICAL DIAGNOSTICS MODAL                                               -->\n  <!-- ========================================================================= -->\n  <div id="techModal"'

if target_marker in html:
    html = html.replace(target_marker, modals_html + '\n\n' + target_marker, 1)
    print("Modals inserted successfully!")
else:
    print("Error: target_marker for techModal not found!")

# 3. Update reverseGeocodeMapClick to immediately update titles
old_reverse = '''    // 4. Reverse Geocoding for Map Clicks
    async function reverseGeocodeMapClick(lat, lon) {
      try {
        const res = await fetch(`/api/geo/reverse?lat=${lat}&lon=${lon}`);
        if (res.ok) {
          const item = await res.json();
          selectSearchResult(item);
          return;
        }
      } catch (e) {}

      // Fallback: format generic point
      selectSearchResult({
        name: `Survey Point (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E)`,
        display_name: `Point ${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E, India`,
        latitude: lat,
        longitude: lon,
        data_state: 'Verified (Point Coordinates)'
      });
    }'''

new_reverse = '''    // 4. Reverse Geocoding for Map Clicks
    async function reverseGeocodeMapClick(lat, lon) {
      // Immediately set title and coordinates so UI responds instantly
      const titleEl = document.getElementById('heroLocationTitle');
      const subtitleEl = document.getElementById('heroLocationSubtitle');
      if (titleEl) titleEl.innerText = `Survey Point (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E)`;
      if (subtitleEl) subtitleEl.innerText = `Coordinates: ${lat.toFixed(5)}°N, ${lon.toFixed(5)}°E • Custom Ground Footprint (40.96 ha)`;

      try {
        const res = await fetch(`/api/geo/reverse?lat=${lat}&lon=${lon}`);
        if (res.ok) {
          const item = await res.json();
          selectSearchResult(item);
          return;
        }
      } catch (e) {}

      // Fallback: format generic point
      selectSearchResult({
        name: `Survey Point (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E)`,
        display_name: `Point ${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E, India`,
        latitude: lat,
        longitude: lon,
        data_state: 'Verified (Point Coordinates)'
      });
    }'''

if old_reverse in html:
    html = html.replace(old_reverse, new_reverse, 1)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Polish and modal updates completed successfully!")
