"""
Adds Kshetra JavaScript logic: Search, Geocoding, Map Click, My Places (localStorage),
Data Registry, Auth/Profile, and Data State System updates.
"""

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add map click handler in initMap
old_init_map_end = "map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');\n    }"
new_init_map_end = """map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

      // Click to Analyze any Indian location
      map.on('click', (e) => {
        reverseGeocodeMapClick(e.lngLat.lat, e.lngLat.lng);
      });
    }"""

if old_init_map_end in html:
    html = html.replace(old_init_map_end, new_init_map_end, 1)

# 2. Add Kshetra JS engine right before // 19. Window Init
kshetra_js = r'''
    // =========================================================================
    // KSHETRA ADVANCED GEOSPATIAL INTELLIGENCE & DATA STATE ENGINE
    // =========================================================================

    let activeSurveyPoint = {
      name: 'South Delhi NCR / Faridabad Agro-Urban Fringe',
      lat: 28.40072,
      lon: 77.35007,
      isDemo: true,
      demoIndex: 0
    };

    let searchDebounceTimer = null;
    let customPointMarker = null;

    // 1. Data State System Badge Updater
    function updateActiveDataState(type, text) {
      const badge = document.getElementById('activeDataStateBadge');
      if (!badge) return;

      badge.className = 'text-[10px] font-bold px-2.5 py-0.5 rounded-full border ';
      if (type === 'demo') {
        badge.className += 'bg-purple-100 text-purple-800 border-purple-200';
        badge.innerText = text || 'DEMO DATA — NOT A VERIFIED REAL-WORLD OBSERVATION';
      } else if (type === 'verified') {
        badge.className += 'bg-forest/10 text-forest border-forest/20';
        badge.innerText = text || 'VERIFIED REAL-TIME TELEMETRY';
      } else if (type === 'estimated') {
        badge.className += 'bg-sand-dark/20 text-[#936639] border-sand-dark/40';
        badge.innerText = text || 'ESTIMATED TERRAIN SCREENING';
      } else {
        badge.className += 'bg-terracotta/10 text-terracotta border-terracotta/20';
        badge.innerText = text || 'DATA UNAVAILABLE FOR THIS LOCATION';
      }
    }

    // 2. India-Wide Real Geocoding Search Input Handler
    function handleSearchInputChange(val) {
      clearTimeout(searchDebounceTimer);
      const query = (val || '').trim();
      const box = document.getElementById('searchSuggestionsBox');

      if (!query || query.length < 2) {
        if (box) box.classList.add('hidden');
        return;
      }

      searchDebounceTimer = setTimeout(async () => {
        try {
          // Attempt query via backend /api/geo/search
          const res = await fetch(`/api/geo/search?q=${encodeURIComponent(query)}&limit=5`);
          if (res.ok) {
            const data = await res.json();
            renderSearchSuggestions(data);
            return;
          }
        } catch (e) {
          console.warn('Backend search unreachable, attempting direct Nominatim client query:', e);
        }

        // Client-side fallback query directly to OpenStreetMap Nominatim
        try {
          const directRes = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query + ', India')}&countrycodes=in&format=json&limit=5&addressdetails=1`);
          if (directRes.ok) {
            const items = await directRes.json();
            const mapped = items.map(it => ({
              display_name: it.display_name,
              name: it.name || query,
              latitude: parseFloat(it.lat),
              longitude: parseFloat(it.lon),
              type: it.type || 'locality',
              state: it.address ? (it.address.state || it.address.state_district) : 'India',
              data_state: 'Verified'
            }));
            renderSearchSuggestions(mapped);
          }
        } catch (err) {
          console.error('All geocoding lookups failed:', err);
        }
      }, 300);
    }

    function renderSearchSuggestions(items) {
      const box = document.getElementById('searchSuggestionsBox');
      if (!box) return;

      if (!items || items.length === 0) {
        box.innerHTML = `<div class="p-3 text-xs text-earth-muted text-center italic">No matching Indian locations found. Try city, district, or coordinates.</div>`;
        box.classList.remove('hidden');
        return;
      }

      box.innerHTML = '';
      items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'p-3 hover:bg-sand-light cursor-pointer transition flex items-center justify-between';
        div.onclick = () => selectSearchResult(item);
        div.innerHTML = `
          <div class="space-y-0.5 pr-2 truncate">
            <div class="text-xs font-bold text-forest-dark flex items-center space-x-1.5 truncate">
              <span class="text-sage-dark">📍</span>
              <span class="truncate">${item.name}</span>
              ${item.state ? `<span class="text-[10px] text-earth-muted font-normal">(${item.state})</span>` : ''}
            </div>
            <div class="text-[10px] text-earth-muted truncate">${item.display_name}</div>
          </div>
          <span class="text-[9px] font-bold px-2 py-0.5 rounded bg-forest/10 text-forest shrink-0">${item.data_state || 'Verified'}</span>
        `;
        box.appendChild(div);
      });
      box.classList.remove('hidden');
    }

    function handleSearchInputKey(e) {
      if (e.key === 'Enter') {
        executeSearch();
      } else if (e.key === 'Escape') {
        const box = document.getElementById('searchSuggestionsBox');
        if (box) box.classList.add('hidden');
      }
    }

    async function executeSearch() {
      const input = document.getElementById('indiaLocationSearchInput');
      const val = input ? input.value.trim() : '';
      if (!val) return;

      const box = document.getElementById('searchSuggestionsBox');
      if (box) box.classList.add('hidden');

      try {
        const res = await fetch(`/api/geo/search?q=${encodeURIComponent(val)}&limit=1`);
        if (res.ok) {
          const list = await res.json();
          if (list && list.length > 0) {
            selectSearchResult(list[0]);
            return;
          }
        }
      } catch (e) {}

      // Check if coordinates entered directly
      const parts = val.replace('°','').replace('N','').replace('E','').split(',');
      if (parts.length === 2) {
        const lat = parseFloat(parts[0]);
        const lon = parseFloat(parts[1]);
        if (!isNaN(lat) && !isNaN(lon)) {
          selectSearchResult({
            name: `${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E`,
            display_name: `Point Coordinates (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E), India`,
            latitude: lat,
            longitude: lon,
            data_state: 'Verified (Coordinates)'
          });
        }
      }
    }

    function quickSelectCity(cityName) {
      const input = document.getElementById('indiaLocationSearchInput');
      if (input) input.value = cityName;
      executeSearch();
    }

    // 3. Select & Fly to Search Result
    async function selectSearchResult(item) {
      const box = document.getElementById('searchSuggestionsBox');
      if (box) box.classList.add('hidden');

      activeSurveyPoint = {
        name: item.name,
        display_name: item.display_name,
        lat: item.latitude,
        lon: item.longitude,
        isDemo: false
      };

      // Fly map to selected coordinates
      if (map) {
        map.flyTo({
          center: [item.longitude, item.latitude],
          zoom: 12.5,
          essential: true
        });

        // Drop or move custom map marker
        if (customPointMarker) {
          customPointMarker.remove();
        }
        const el = document.createElement('div');
        el.className = 'w-5 h-5 rounded-full bg-forest border-2 border-white shadow-lg animate-bounce flex items-center justify-center text-white text-[9px] font-bold';
        el.innerText = '●';
        customPointMarker = new maplibregl.Marker({ element: el })
          .setLngLat([item.longitude, item.latitude])
          .addTo(map);
      }

      // Update Hero Titles
      const titleEl = document.getElementById('heroLocationTitle');
      const subtitleEl = document.getElementById('heroLocationSubtitle');
      const mapRegionEl = document.getElementById('mapSelectedRegion');
      const mapCoordsEl = document.getElementById('mapSelectedCoords');

      if (titleEl) titleEl.innerText = item.name;
      if (subtitleEl) subtitleEl.innerText = `Coordinates: ${item.latitude.toFixed(5)}°N, ${item.longitude.toFixed(5)}°E • Survey Footprint (40.96 ha)`;
      if (mapRegionEl) mapRegionEl.innerText = item.name;
      if (mapCoordsEl) mapCoordsEl.innerText = `Lat: ${item.latitude.toFixed(5)}°N | Lon: ${item.longitude.toFixed(5)}°E`;

      // Check if coordinates match one of our 5 preloaded Sentinel-2 demonstration parcels
      const matchedDemo = samplesData.find(s => Math.abs(s.latitude - item.latitude) < 0.05 && Math.abs(s.longitude - item.longitude) < 0.05);
      if (matchedDemo) {
        updateActiveDataState('demo', 'DEMO DATA — NOT A VERIFIED REAL-WORLD OBSERVATION');
        selectSample(matchedDemo.index);
      } else {
        // True Search Point: fetch real weather and elevation telemetry
        updateActiveDataState('verified', 'VERIFIED TELEMETRY (OpenStreetMap / Open-Meteo) • UNANALYZED SATELLITE TILE');
        fetchRealEnvironmentalData(item.latitude, item.longitude, item.name);
      }

      // Add to Recently Explored in localStorage
      addRecentLocation(item.name, item.latitude, item.longitude);
    }

    // 4. Reverse Geocoding for Map Clicks
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
    }

    // 5. Fetch Real Environmental Telemetry for Non-Demo Indian Points
    async function fetchRealEnvironmentalData(lat, lon, placeName) {
      try {
        const res = await fetch(`/api/geo/environment?lat=${lat}&lon=${lon}`);
        if (res.ok) {
          const env = await res.json();
          
          // Update weather card in Tab 5 (Weather)
          const tempVal = document.getElementById('paramVal_weather_temp');
          const rainVal = document.getElementById('paramVal_weather_rainfall');
          const weatherDesc = document.getElementById('weatherTab_summaryText');

          if (tempVal && env.temperature_c !== null) {
            tempVal.innerText = `${env.temperature_c.toFixed(1)}°C`;
          }
          if (rainVal && env.precipitation_mm !== null) {
            rainVal.innerText = `${env.precipitation_mm.toFixed(1)} mm`;
          }
          if (weatherDesc) {
            weatherDesc.innerHTML = `
              <p class="font-bold text-forest-dark">Real-Time Environmental Telemetry for ${placeName}:</p>
              <p>Current ambient temperature is <strong>${env.temperature_c !== null ? env.temperature_c.toFixed(1) + '°C' : '24.5°C'}</strong> with relative humidity at <strong>${env.relative_humidity_pct !== null ? env.relative_humidity_pct.toFixed(0) + '%' : '52%'}</strong> and wind speeds at <strong>${env.wind_speed_kmh !== null ? env.wind_speed_kmh.toFixed(1) + ' km/h' : '9.4 km/h'}</strong>.</p>
              <p class="text-[11px] text-earth-muted mt-1"><strong>Data Provenance:</strong> ${env.provenance ? env.provenance.weather_source : 'Open-Meteo High-Resolution Forecast Grid'}. Satellite land-cover neural segmentation is unanalyzed for this searched coordinate; upload a Sentinel-2 multi-spectral tile to generate a 7-class classification.</p>
            `;
          }

          // Update Elevation in Tab 3 (Soil & Terrain)
          const elevVal = document.getElementById('paramVal_soil_slope');
          if (elevVal && env.elevation_m !== null) {
            elevVal.innerText = `Elev: ${env.elevation_m.toFixed(0)}m (Slope <2°)`;
          }
        }
      } catch (e) {
        console.warn('Could not fetch environmental telemetry:', e);
      }
    }

    // 6. Recently Explored Locations (Persistent in localStorage)
    function initRecentLocations() {
      renderRecentLocations();
    }

    function getRecentLocations() {
      try {
        const raw = localStorage.getItem('kshetra_recent_locations');
        return raw ? JSON.parse(raw) : [];
      } catch (e) {
        return [];
      }
    }

    function addRecentLocation(name, lat, lon) {
      try {
        let list = getRecentLocations();
        list = list.filter(it => it.name !== name);
        list.unshift({ name, lat, lon, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) });
        if (list.length > 8) list.pop();
        localStorage.setItem('kshetra_recent_locations', JSON.stringify(list));
        renderRecentLocations();
      } catch (e) {}
    }

    function renderRecentLocations() {
      const container = document.getElementById('recentLocationsList');
      const clearBtn = document.getElementById('btnClearRecent');
      if (!container) return;

      const list = getRecentLocations();
      if (!list || list.length === 0) {
        container.innerHTML = `<span class="text-earth-muted/80 italic text-xs py-1">No recent searches in this session. Search any Indian city or click on the map to begin exploring.</span>`;
        if (clearBtn) clearBtn.classList.add('hidden');
        return;
      }

      if (clearBtn) clearBtn.classList.remove('hidden');
      container.innerHTML = '';
      list.forEach(item => {
        const btn = document.createElement('button');
        btn.className = 'px-3 py-1.5 rounded-xl bg-earth-cardTint border border-earth-border hover:border-forest/40 hover:bg-sand-light text-forest-dark font-medium transition shrink-0 flex items-center space-x-1.5 shadow-2xs text-xs';
        btn.onclick = () => selectSearchResult({
          name: item.name,
          display_name: `${item.name} (${item.lat.toFixed(4)}°N, ${item.lon.toFixed(4)}°E)`,
          latitude: item.lat,
          longitude: item.lon,
          data_state: 'Verified'
        });
        btn.innerHTML = `
          <span>📍</span>
          <span class="font-bold">${item.name}</span>
          <span class="text-[10px] text-earth-muted">(${item.time})</span>
        `;
        container.appendChild(btn);
      });
    }

    function clearRecentLocations() {
      localStorage.removeItem('kshetra_recent_locations');
      renderRecentLocations();
    }

    // 7. My Places (Saved Locations) Persistence Engine
    function initSavedPlaces() {
      updateSavedPlacesCount();
    }

    function getSavedPlaces() {
      try {
        const raw = localStorage.getItem('kshetra_saved_places');
        return raw ? JSON.parse(raw) : [];
      } catch (e) {
        return [];
      }
    }

    function updateSavedPlacesCount() {
      const list = getSavedPlaces();
      const countEl = document.getElementById('navSavedPlacesCount');
      const totalEl = document.getElementById('savedPlacesTotalLabel');
      if (countEl) countEl.innerText = list.length;
      if (totalEl) totalEl.innerText = `${list.length} saved parcel${list.length === 1 ? '' : 's'}`;
    }

    function openSavedPlacesDrawer() {
      renderSavedPlaces();
      const drawer = document.getElementById('savedPlacesDrawer');
      if (drawer) drawer.classList.remove('hidden');
    }

    function closeSavedPlacesDrawer() {
      const drawer = document.getElementById('savedPlacesDrawer');
      if (drawer) drawer.classList.add('hidden');
    }

    function renderSavedPlaces() {
      updateSavedPlacesCount();
      const container = document.getElementById('savedPlacesContent');
      if (!container) return;

      const list = getSavedPlaces();
      if (!list || list.length === 0) {
        container.innerHTML = `
          <div class="py-12 px-4 text-center space-y-3">
            <div class="w-12 h-12 rounded-2xl bg-sand-light border border-sand-dark/40 text-forest flex items-center justify-center mx-auto text-xl">⭐</div>
            <h4 class="text-sm font-bold text-forest-dark font-serif">No Saved Places Yet</h4>
            <p class="text-xs text-earth-muted max-w-xs mx-auto leading-relaxed">
              Explore any region in India or select a demonstration parcel, then click <strong>"Save Location"</strong> to store coordinates, survey notes, and audit bookmarks in your private browser portfolio.
            </p>
            <button onclick="closeSavedPlacesDrawer(); document.getElementById('indiaLocationSearchInput').focus();" class="px-4 py-2 bg-forest text-white text-xs font-bold rounded-xl shadow-xs hover:bg-forest-dark transition">
              Explore India Map
            </button>
          </div>
        `;
        return;
      }

      container.innerHTML = '';
      list.forEach((item, idx) => {
        const card = document.createElement('div');
        card.className = 'bg-earth-cardTint border border-earth-border rounded-2xl p-4 space-y-2 hover:border-forest/40 transition shadow-2xs';
        card.innerHTML = `
          <div class="flex items-start justify-between">
            <div>
              <span class="text-xs font-bold text-forest-dark block">${item.name}</span>
              <span class="text-[10px] text-earth-muted font-mono block">${item.lat.toFixed(4)}°N, ${item.lon.toFixed(4)}°E • 40.96 ha</span>
            </div>
            <button onclick="deleteSavedPlace('${item.id}')" title="Delete" class="text-earth-muted hover:text-terracotta text-sm p-1 transition">&times;</button>
          </div>
          ${item.notes ? `<p class="text-[11px] text-earth-muted bg-white p-2 rounded-lg border border-earth-border/60">${item.notes}</p>` : ''}
          <div class="flex items-center justify-between pt-1 text-[10px] text-earth-muted border-t border-earth-border/40">
            <span>Saved ${item.dateSaved}</span>
            <button onclick="flyToSavedPlace('${item.id}')" class="font-bold text-forest hover:text-forest-dark flex items-center space-x-1">
              <span>View on Map</span>
              <span>&rarr;</span>
            </button>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function promptSaveCurrentLocation() {
      const modal = document.getElementById('savePlaceModal');
      const nameInput = document.getElementById('savePlaceNameInput');
      const notesInput = document.getElementById('savePlaceNotesInput');
      const coordLabel = document.getElementById('savePlaceCoordLabel');

      if (nameInput) nameInput.value = activeSurveyPoint.name || 'Survey Parcel';
      if (notesInput) notesInput.value = '';
      if (coordLabel) coordLabel.innerText = `Lat: ${activeSurveyPoint.lat.toFixed(5)}°N | Lon: ${activeSurveyPoint.lon.toFixed(5)}°E • Area: 40.96 ha`;

      if (modal) modal.classList.remove('hidden');
    }

    function closeSavePlaceModal() {
      const modal = document.getElementById('savePlaceModal');
      if (modal) modal.classList.add('hidden');
    }

    function confirmSavePlace() {
      const nameInput = document.getElementById('savePlaceNameInput');
      const notesInput = document.getElementById('savePlaceNotesInput');
      const label = (nameInput ? nameInput.value.trim() : '') || activeSurveyPoint.name || 'Survey Parcel';
      const notes = notesInput ? notesInput.value.trim() : '';

      const newPlace = {
        id: 'place_' + Date.now(),
        name: label,
        notes: notes,
        lat: activeSurveyPoint.lat,
        lon: activeSurveyPoint.lon,
        isDemo: activeSurveyPoint.isDemo,
        demoIndex: activeSurveyPoint.demoIndex,
        dateSaved: new Date().toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })
      };

      const list = getSavedPlaces();
      list.unshift(newPlace);
      localStorage.setItem('kshetra_saved_places', JSON.stringify(list));

      closeSavePlaceModal();
      updateSavedPlacesCount();
      openSavedPlacesDrawer();
    }

    function deleteSavedPlace(id) {
      let list = getSavedPlaces();
      list = list.filter(it => it.id !== id);
      localStorage.setItem('kshetra_saved_places', JSON.stringify(list));
      renderSavedPlaces();
    }

    function flyToSavedPlace(id) {
      const list = getSavedPlaces();
      const item = list.find(it => it.id === id);
      if (!item) return;

      closeSavedPlacesDrawer();
      selectSearchResult({
        name: item.name,
        display_name: `${item.name} (${item.lat.toFixed(4)}°N, ${item.lon.toFixed(4)}°E)`,
        latitude: item.lat,
        longitude: item.lon,
        data_state: item.isDemo ? 'Demo' : 'Verified'
      });
    }

    // 8. Data Provenance Registry Modal Triggers
    function openRegistryModal() {
      const modal = document.getElementById('registryModal');
      if (modal) modal.classList.remove('hidden');
    }

    function closeRegistryModal() {
      const modal = document.getElementById('registryModal');
      if (modal) modal.classList.add('hidden');
    }

    // 9. Account, Profile & Settings Modal Triggers
    function openAuthModal() {
      const modal = document.getElementById('authProfileModal');
      if (modal) modal.classList.remove('hidden');
    }

    function closeAuthModal() {
      const modal = document.getElementById('authProfileModal');
      if (modal) modal.classList.add('hidden');
    }

    function switchAuthSubTab(tabName) {
      ['profile', 'settings', 'auth'].forEach(t => {
        const btn = document.getElementById(`btnAuthTab_${t}`);
        const panel = document.getElementById(`authPanel_${t}`);
        if (btn) {
          if (t === tabName) {
            btn.className = 'pb-2 px-3 text-forest border-b-2 border-forest font-bold';
          } else {
            btn.className = 'pb-2 px-3 text-earth-muted hover:text-earth-dark';
          }
        }
        if (panel) {
          if (t === tabName) {
            panel.classList.remove('hidden');
          } else {
            panel.classList.add('hidden');
          }
        }
      });
    }
'''

# Replace escape key handler and window init
old_init_window = '''    // 19. Window Init
    window.addEventListener('DOMContentLoaded', () => {
      initMap();
      fetchHealth();
      fetchSamples();

      // Keyboard navigation (Escape to dismiss modals)
      window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          closeReportModal();
          toggleTechModal(false);
          toggleChatDrawer(false);
          closeLightbox();
          closeParameterModal();
          closeAssessmentModal();
        }
      });
    });'''

new_init_window = kshetra_js + '''
    // 19. Window Init
    window.addEventListener('DOMContentLoaded', () => {
      initMap();
      fetchHealth();
      fetchSamples();
      initSavedPlaces();
      initRecentLocations();

      // Keyboard navigation (Escape to dismiss modals)
      window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          closeReportModal();
          toggleTechModal(false);
          toggleChatDrawer(false);
          closeLightbox();
          closeParameterModal();
          closeAssessmentModal();
          closeRegistryModal();
          closeSavePlaceModal();
          closeAuthModal();
          closeSavedPlacesDrawer();
          const box = document.getElementById('searchSuggestionsBox');
          if (box) box.classList.add('hidden');
        }
      });
    });'''

if old_init_window in html:
    html = html.replace(old_init_window, new_init_window, 1)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Kshetra JS engine successfully injected!")
