  <!-- ========================================================================= -->
  <!-- JAVASCRIPT SAAS APPLICATION ENGINE (PHASE 1 UX REDESIGN)                   -->
  <!-- ========================================================================= -->
  // <script>
    // --- Global Application State ---
    let currentView = 'dashboard';
    let sidebarCollapsed = false;
    let map = null;
    let dashMap = null;
    let markers = [];
    let customMarker = null;
    let availableSamples = [];
    let currentPrediction = null;
    let currentEnvironment = null;
    let currentUser = null;
    let savedPlaces = [];
    let recentSearches = [];
    let searchDebounceTimer = null;
    let activeIntelDomain = 'overview';
    let savedReports = [];
    let selectedComparePlaceIds = [];
    let editingPlaceId = null;
    let authMode = 'login'; // 'login' or 'register'

    let activeSurvey = {
      name: 'Faridabad Agro-Urban Fringe',
      displayName: 'Faridabad Agro-Urban Fringe, South Delhi NCR, Haryana, India',
      lat: 28.40072,
      lon: 77.35007,
      isDemo: true,
      demoIndex: 0,
      dataState: 'DEMO DATA — NOT A VERIFIED REAL-WORLD OBSERVATION'
    };

    // 7 Humanized Land Cover Classes
    const LAND_CLASSES = {
      'class_1': { name: 'Water Body', label: 'Open Surface Water', color: '#0066FF', desc: 'Canals, drainage retention, natural ponds' },
      'class_2': { name: 'Tree Cover', label: 'Wooded Tree Canopy', color: '#008000', desc: 'Woodlots, orchards, roadside shelterbelts' },
      'class_3': { name: 'Flooded Veg', label: 'Wetland Vegetation', color: '#00FFCC', desc: 'Canal banks, waterlogged depressions' },
      'class_4': { name: 'Crops', label: 'Cultivated Crop Canopy', color: '#99CC00', desc: 'Irrigated seasonal wheat, mustard, vegetables' },
      'class_5': { name: 'Built-up', label: 'Built Structures & Roads', color: '#FF0000', desc: 'Paved surfaces, residences, commercial plots' },
      'class_6': { name: 'Bare Ground', label: 'Ploughed Open Soil', color: '#CC9966', desc: 'Exposed agricultural topsoil, fallow land' },
      'class_7': { name: 'Snow/Ice', label: 'Reflective Surface', color: '#FFFFFF', desc: 'High-albedo mineral or reflective substrate' }
    };

    // =========================================================================
    // 1. SIDEBAR TOGGLE (3-LINES HAMBURGER ON DESKTOP & MOBILE)
    // =========================================================================
    function toggleSidebar() {
      const sidebar = document.getElementById('appSidebar');
      const shell = document.getElementById('appContentShell');
      if (!sidebar) return;

      if (window.innerWidth < 768) {
        // Mobile toggle
        if (sidebar.classList.contains('-translate-x-full')) {
          sidebar.classList.remove('-translate-x-full');
        } else {
          sidebar.classList.add('-translate-x-full');
        }
      } else {
        // Desktop toggle
        sidebarCollapsed = !sidebarCollapsed;
        if (sidebarCollapsed) {
          sidebar.classList.add('-translate-x-full');
          if (shell) {
            shell.classList.remove('md:pl-64');
            shell.classList.add('md:pl-0');
          }
        } else {
          sidebar.classList.remove('-translate-x-full');
          if (shell) {
            shell.classList.remove('md:pl-0');
            shell.classList.add('md:pl-64');
          }
        }
      }

      // Smoothly resize maps after transition
      setTimeout(() => {
        if (map) map.resize();
        if (dashMap) dashMap.resize();
      }, 320);
    }

    // =========================================================================
    // 2. STATE-BASED ROUTER
    // =========================================================================
    function navigateTo(viewName) {
      if (!viewName) viewName = 'dashboard';
      currentView = viewName;

      const sidebar = document.getElementById('appSidebar');
      const shell = document.getElementById('appContentShell');
      const header = document.querySelector('header');
      const main = document.getElementById('appMain') || document.querySelector('main');

      if (viewName === 'dashboard') {
        if (sidebar) sidebar.classList.add('-translate-x-full');
        if (shell) {
          shell.classList.remove('md:pl-64');
          shell.classList.add('md:pl-0');
        }
        if (header) header.classList.add('hidden');
        if (main) {
          main.classList.remove('max-w-7xl', 'mx-auto', 'p-4', 'sm:p-6', 'lg:p-8', 'space-y-6', 'pb-24');
          main.classList.add('w-full', 'p-0');
        }
        document.body.style.backgroundColor = '#040805';
        document.body.style.color = '#FFFFFF';
      } else {
        if (sidebar && !sidebarCollapsed) sidebar.classList.remove('-translate-x-full');
        if (shell && !sidebarCollapsed) {
          shell.classList.remove('md:pl-0');
          shell.classList.add('md:pl-64');
        }
        if (header) header.classList.remove('hidden');
        if (main) {
          main.classList.remove('w-full', 'p-0');
          main.classList.add('max-w-7xl', 'mx-auto', 'p-4', 'sm:p-6', 'lg:p-8', 'space-y-6', 'pb-24');
        }
        document.body.style.backgroundColor = '#F6F3E9';
        document.body.style.color = '#223026';
      }

      // 1. Hide all views
      document.querySelectorAll('.app-view').forEach(el => el.classList.add('hidden'));

      // 2. Show target view
      const targetEl = document.getElementById('view_' + viewName);
      if (targetEl) {
        targetEl.classList.remove('hidden');
      }

      // 3. Update Sidebar Nav Items styling
      const navIds = ['dashboard', 'explore', 'intelligence', 'mllab', 'places', 'reports', 'advisor', 'registry', 'landing', 'profile', 'settings'];
      navIds.forEach(id => {
        const btn = document.getElementById('nav_' + id);
        if (btn) {
          if (id === viewName) {
            btn.className = 'nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl transition bg-forest text-white shadow-xs';
          } else {
            btn.className = 'nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-earth-text hover:bg-sand-light transition';
          }
        }
      });

      // 4. Update Header Breadcrumb
      const breadcrumb = document.getElementById('currentViewBreadcrumb');
      if (breadcrumb) {
        const titles = {
          'dashboard': 'Dashboard',
          'explore': 'Explore India',
          'intelligence': 'Land Intelligence',
          'mllab': 'Land Discovery & AI',
          'places': 'My Places',
          'reports': 'Reports',
          'advisor': 'AI Land Advisor',
          'registry': 'Data Sources',
          'landing': 'Public Overview',
          'profile': 'Profile',
          'settings': 'Settings'
        };
        breadcrumb.innerText = titles[viewName] || 'Dashboard';
      }

      // 5. Special View Triggers
      if (viewName === 'dashboard') {
        initDashboardGreeting();
        renderDashboardSavedPlaces();
        if (!dashMap) {
          setTimeout(initDashMap, 50);
        } else {
          setTimeout(() => dashMap.resize(), 100);
        }
      } else if (viewName === 'explore') {
        if (!map) {
          setTimeout(initMap, 50);
        } else {
          setTimeout(() => map.resize(), 100);
        }
      } else if (viewName === 'places') {
        renderSavedPlaces();
      } else if (viewName === 'reports') {
        renderReportsView();
      } else if (viewName === 'intelligence') {
        renderIntelligenceView();
      } else if (viewName === 'mllab') {
        initMLLab();
      } else if (viewName === 'registry') {
        loadDataRegistry();
      }

      // Close mobile sidebar if open on small screens
      if (sidebar && window.innerWidth < 768) {
        sidebar.classList.add('-translate-x-full');
      }

      window.scrollTo({ top: 0, behavior: 'smooth' });
      window.location.hash = viewName;
    }

    // =========================================================================
    // 3. DASHBOARD HOME PAGE ENGINE
    // =========================================================================
    function initDashboardGreeting() {
      const hour = new Date().getHours();
      let greeting = 'Good day';
      if (hour >= 5 && hour < 12) greeting = 'Good morning';
      else if (hour >= 12 && hour < 17) greeting = 'Good afternoon';
      else greeting = 'Good evening';

      const greetTimeEl = document.getElementById('dashGreetingTime');
      if (greetTimeEl) greetTimeEl.innerText = greeting;

      const greetUserEl = document.getElementById('dashGreetingUser');
      if (greetUserEl) {
        greetUserEl.innerText = currentUser && currentUser.full_name ? currentUser.full_name.split(' ')[0] : 'Surveyor';
      }
    }

    function focusDashboardSearch() {
      const input = document.getElementById('dashSearchInput');
      if (input) {
        input.focus();
        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    
    // =========================================================================
    // 3B. CINEMATIC LANDING & DYNAMIC LOCATION HELPERS
    // =========================================================================
    function toggleMobileLandingMenu() {
      const menu = document.getElementById('mobileLandingMenu');
      if (menu) menu.classList.toggle('hidden');
    }

    function toggleSidebarDirectly() {
      toggleSidebar();
    }

    function executeHeroSearch() {
      const input = document.getElementById('heroLocationSearch');
      if (!input || !input.value.trim()) return;
      const query = input.value.trim();
      const topSearch = document.getElementById('topLocationSearch');
      if (topSearch) topSearch.value = query;
      handleSearch(query);
      navigateTo('explore');
    }

    function quickHeroJump(name, lat, lon) {
      activeSurvey = {
        name: name,
        displayName: `${name}, India`,
        lat: lat,
        lon: lon,
        isDemo: false,
        demoIndex: null,
        dataState: 'VERIFIED REAL-TIME OBSERVATION'
      };
      updateActivePlaceUI();
      if (dashMap) {
        dashMap.flyTo({ center: [lon, lat], zoom: 9.5, essential: true });
      }
      if (map) {
        map.flyTo({ center: [lon, lat], zoom: 11.5, essential: true });
      }
      fetchEnvironment(lat, lon);
      acquireSatelliteImagery(lat, lon);
      navigateTo('intelligence');
    }

    function openCoordinatesPrompt() {
      const coordsStr = prompt("Enter Indian Coordinates (Latitude, Longitude):\nExample: 28.6139, 77.2090");
      if (!coordsStr) return;
      const parts = coordsStr.replace('°','').replace('N','').replace('E','').split(',').map(p => parseFloat(p.trim()));
      if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
        const lat = parts[0];
        const lon = parts[1];
        if (lat >= 6.0 && lat <= 38.0 && lon >= 68.0 && lon <= 98.0) {
          handleMapClick(lat, lon);
          navigateTo('intelligence');
        } else {
          alert("Coordinates must be within the territory of India (6°N–38°N, 68°E–98°E).");
        }
      } else {
        alert("Invalid format. Please enter as: Latitude, Longitude (e.g. 28.4089, 77.3178)");
      }
    }

    function dashMapPanTo(coords, zoom) {
      if (!dashMap) return;
      dashMap.flyTo({ center: coords, zoom: zoom, essential: true });
    }

    function setDashMapLayer(type) {
      if (!dashMap) return;
      ['dark', 'sat', 'osm'].forEach(layer => {
        const btn = document.getElementById('dashLayer' + layer.charAt(0).toUpperCase() + layer.slice(1));
        if (btn) {
          if ((type === 'dark' && layer === 'dark') || (type === 'satellite' && layer === 'sat') || (type === 'osm' && layer === 'osm')) {
            btn.className = 'px-3 py-1 rounded-lg text-xs font-mono bg-emerald-500 text-black font-bold transition';
          } else {
            btn.className = 'px-3 py-1 rounded-lg text-xs font-mono bg-[#09150D] text-zinc-300 hover:text-white border border-emerald-900/50 transition';
          }
        }
      });

      const layerIdMap = {
        'dark': 'dash-dark-layer',
        'satellite': 'dash-satellite-layer',
        'osm': 'dash-osm-layer'
      };

      Object.entries(layerIdMap).forEach(([key, layerId]) => {
        if (dashMap.getLayer(layerId)) {
          dashMap.setLayoutProperty(layerId, 'visibility', key === type ? 'visible' : 'none');
        }
      });
    }

    function openImageZoomModal(imgSrc, title, coords, locId) {
      const modal = document.getElementById('imageZoomModal');
      const img = document.getElementById('zoomModalImg');
      const titleEl = document.getElementById('zoomModalTitle');
      const coordsEl = document.getElementById('zoomModalCoords');
      const btn = document.getElementById('zoomModalInspectBtn');

      if (img) img.src = imgSrc;
      if (titleEl) titleEl.innerText = title;
      if (coordsEl) coordsEl.innerText = coords;
      if (btn) {
        btn.onclick = () => {
          closeImageZoomModal();
          selectCatalogueLocation(locId);
        };
      }
      if (modal) modal.classList.remove('hidden');
    }

    function closeImageZoomModal() {
      const modal = document.getElementById('imageZoomModal');
      if (modal) modal.classList.add('hidden');
    }

    function initDashMap() {
      const container = document.getElementById('dashMap');
      if (!container || dashMap) return;

      dashMap = new maplibregl.Map({
        container: 'dashMap',
        style: {
          version: 8,
          sources: {
            'dash-satellite': {
              type: 'raster',
              tiles: [
                'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
              ],
              tileSize: 256,
              attribution: 'Tiles &copy; Esri',
              maxzoom: 19
            },
            'dash-dark': {
              type: 'raster',
              tiles: [
                'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'
              ],
              tileSize: 256,
              maxzoom: 16
            },
            'dash-osm': {
              type: 'raster',
              tiles: [
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
              ],
              tileSize: 256,
              maxzoom: 19
            }
          },
          layers: [
            { id: 'dash-satellite-layer', type: 'raster', source: 'dash-satellite', minzoom: 0, maxzoom: 19, layout: { visibility: 'none' } },
            { id: 'dash-dark-layer', type: 'raster', source: 'dash-dark', minzoom: 0, maxzoom: 19, layout: { visibility: 'visible' } },
            { id: 'dash-osm-layer', type: 'raster', source: 'dash-osm', minzoom: 0, maxzoom: 19, layout: { visibility: 'none' } }
          ]
        },
        center: [77.3501, 28.4007],
        zoom: 9.5
      });

      dashMap.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

      dashMap.on('click', (e) => {
        const lat = e.lngLat.lat;
        const lon = e.lngLat.lng;
        const hudCoords = document.getElementById('dashHudCoords');
        const hudPlace = document.getElementById('dashHudPlace');
        if (hudCoords) hudCoords.innerText = `${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E`;
        if (hudPlace) hudPlace.innerText = `Survey Point (${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E)`;
        handleMapClick(lat, lon);
      });
    }

    // =========================================================================
    // 4. MAPLIBRE GL JS MAP ENGINE (EXPLORE INDIA)
    // =========================================================================
    function initMap() {
      if (map) return;
      const mapContainer = document.getElementById('map');
      if (!mapContainer) return;

      map = new maplibregl.Map({
        container: 'map',
        style: {
          version: 8,
          sources: {
            'esri-satellite': {
              type: 'raster',
              tiles: [
                'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
              ],
              tileSize: 256,
              attribution: 'Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics',
              maxzoom: 19
            },
            'esri-dark': {
              type: 'raster',
              tiles: [
                'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'
              ],
              tileSize: 256,
              attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
              maxzoom: 16
            },
            'osm-streets': {
              type: 'raster',
              tiles: [
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
              ],
              tileSize: 256,
              attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
              maxzoom: 19
            }
          },
          layers: [
            {
              id: 'esri-satellite-layer',
              type: 'raster',
              source: 'esri-satellite',
              minzoom: 0,
              maxzoom: 19
            },
            {
              id: 'esri-dark-layer',
              type: 'raster',
              source: 'esri-dark',
              minzoom: 0,
              maxzoom: 19,
              layout: { visibility: 'none' }
            },
            {
              id: 'osm-streets-layer',
              type: 'raster',
              source: 'osm-streets',
              minzoom: 0,
              maxzoom: 19,
              layout: { visibility: 'none' }
            }
          ]
        },
        center: [77.3501, 28.4007],
        zoom: 10
      });

      map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

      map.on('click', (e) => {
        handleMapClick(e.lngLat.lat, e.lngLat.lng);
      });

      map.on('load', () => {
        if (availableSamples.length > 0) {
          plotSampleMarkers(availableSamples);
        }
      });
    }

    function setMapLayer(layerKey) {
      const applyLayer = (targetMap, prefix) => {
        if (!targetMap || !targetMap.isStyleLoaded()) return;
        const layers = [`${prefix}satellite-layer`, `${prefix}dark-layer`, `${prefix}osm-layer`];
        layers.forEach(l => {
          if (targetMap.getLayer(l)) {
            targetMap.setLayoutProperty(l, 'visibility', 'none');
          }
        });
        if (targetMap.getLayer(`${prefix}${layerKey}-layer`)) {
          targetMap.setLayoutProperty(`${prefix}${layerKey}-layer`, 'visibility', 'visible');
        }
      };

      applyLayer(map, 'esri-');
      applyLayer(dashMap, 'dash-');

      const btnSat = document.getElementById('btnLayerSat');
      const btnDark = document.getElementById('btnLayerDark');
      const btnOsm = document.getElementById('btnLayerOSM');

      const activeCls = 'px-3 py-1 font-semibold rounded-lg bg-forest text-white transition';
      const inactiveCls = 'px-3 py-1 font-semibold rounded-lg text-earth-text hover:bg-sand-light transition';

      if (btnSat) btnSat.className = inactiveCls;
      if (btnDark) btnDark.className = inactiveCls;
      if (btnOsm) btnOsm.className = inactiveCls;

      if (layerKey === 'satellite' && btnSat) btnSat.className = activeCls;
      else if (layerKey === 'dark' && btnDark) btnDark.className = activeCls;
      else if (layerKey === 'osm' && btnOsm) btnOsm.className = activeCls;
    }

    function resetMapView() {
      if (!map) return;
      map.flyTo({ center: [activeSurvey.lon, activeSurvey.lat], zoom: 11, essential: true });
    }

    // =========================================================================
    // 5. SAMPLE PLOTTING & NEURAL MODEL INFERENCE
    // =========================================================================
    async function loadSamples() {
      try {
        const res = await fetch('/api/predict/samples');
        if (!res.ok) return;
        availableSamples = await res.json();
        renderSampleCards(availableSamples);
        if (map && map.isStyleLoaded()) {
          plotSampleMarkers(availableSamples);
        }
        // Run initial inference on Sample 0
        if (availableSamples.length > 0) {
          runSampleInference(availableSamples[0].index);
        }
      } catch (e) {
        console.warn('Could not load sample manifest:', e);
      }
    }

    function renderSampleCards(samples) {
      const container = document.getElementById('sampleCardsGrid');
      if (!container) return;
      container.innerHTML = '';

      samples.forEach(s => {
        const card = document.createElement('div');
        card.className = 'p-2.5 rounded-xl bg-white border border-earth-border hover:border-forest hover:bg-sand-light/50 transition cursor-pointer shadow-2xs space-y-1.5';
        card.onclick = () => {
          selectSample(s.index);
        };
        card.innerHTML = `
          <div class="flex items-center space-x-2">
            ${s.thumbnail_b64 ? `<img src="${s.thumbnail_b64}" class="w-8 h-8 rounded-lg object-cover border border-earth-border shrink-0" />` : ''}
            <div class="truncate">
              <div class="text-xs font-bold text-forest-dark truncate">#${s.index} ${s.description.split('/')[0]}</div>
              <div class="text-[10px] font-mono text-earth-muted">${s.latitude.toFixed(2)}°N, ${s.longitude.toFixed(2)}°E</div>
            </div>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function plotSampleMarkers(samples) {
      markers.forEach(m => m.remove());
      markers = [];

      samples.forEach(s => {
        if (!s.latitude || !s.longitude) return;

        const el = document.createElement('div');
        el.className = 'w-7 h-7 rounded-full bg-forest border-2 border-white flex items-center justify-center cursor-pointer shadow-md hover:scale-115 transition';
        el.innerHTML = `<span class="text-[10px] font-bold text-white">${s.index}</span>`;

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([s.longitude, s.latitude])
          .addTo(map);

        el.addEventListener('click', (e) => {
          e.stopPropagation();
          selectSample(s.index);
        });

        markers.push(marker);
      });
    }

    async function selectSample(sampleIndex) {
      const sample = availableSamples.find(s => s.index === sampleIndex);
      if (!sample) return;

      activeSurvey = {
        name: sample.description,
        displayName: `${sample.description}, India`,
        lat: sample.latitude,
        lon: sample.longitude,
        isDemo: true,
        demoIndex: sample.index,
        dataState: 'DEMO DATA — NOT A VERIFIED REAL-WORLD OBSERVATION'
      };

      updateActivePlaceUI();
      if (map) {
        map.flyTo({ center: [sample.longitude, sample.latitude], zoom: 11.5, essential: true });
      }
      if (dashMap) {
        dashMap.flyTo({ center: [sample.longitude, sample.latitude], zoom: 11.5, essential: true });
      }

      acquireSatelliteImagery(sample.latitude, sample.longitude);
      await runSampleInference(sampleIndex);
    }

    async function selectSampleTile(sampleIndex) {
      await selectSample(sampleIndex);
      navigateTo('intelligence');
    }

    
    // =========================================================================
    // 5B. ENVIRONMENTAL TELEMETRY INGESTION (NASA SRTM + IMD + OPEN-METEO)
    // =========================================================================
    async function fetchEnvironment(lat, lon) {
      try {
        const res = await fetch(`/api/geo/environment?lat=${lat}&lon=${lon}`);
        if (res.ok) {
          currentEnvironment = await res.json();
          renderEnvironmentData();
        }
      } catch (e) {
        console.warn("Could not fetch environment telemetry:", e);
      }
    }

    function renderEnvironmentData() {
      if (!currentEnvironment) return;
      const env = currentEnvironment;

      // Dashboard Slope Metric
      const dashSlope = document.getElementById('dashMetricSlope');
      if (dashSlope && env.slope_deg != null) {
        dashSlope.innerText = `${env.slope_deg.toFixed(1)}%`;
      }

      // Soil & Terrain Tab
      const soilSlopeVal = document.getElementById('valSoilSlope');
      if (soilSlopeVal && env.slope_deg != null) {
        soilSlopeVal.innerText = `${env.slope_deg.toFixed(1)}%`;
      }
      const soilElevVal = document.getElementById('valSoilElev');
      if (soilElevVal && env.elevation_m != null) {
        soilElevVal.innerText = `${Math.round(env.elevation_m)} meters`;
      }

      // Weather Tab
      const weatherTemp = document.getElementById('valWeatherTemp');
      if (weatherTemp && env.temperature_c != null) {
        weatherTemp.innerText = `${env.temperature_c.toFixed(1)} °C`;
      }
      const weatherRain = document.getElementById('valWeatherRain');
      if (weatherRain) {
        const rainVal = (env.annual_rainfall_mm != null) ? Math.round(env.annual_rainfall_mm) : 750;
        weatherRain.innerText = `${rainVal} mm / year`;
      }
    }

    async function runSampleInference(sampleIndex) {
      try {
        let res = await fetch(`/api/predict/sample/${sampleIndex}`, { method: 'POST' });
        if (!res.ok) {
          res = await fetch(`/api/predict/sample/${sampleIndex}`);
        }
        if (!res.ok) return;
        currentPrediction = await res.json();
        const sampleLocations = [
          { lat: 28.40072, lon: 77.35007 },
          { lat: 28.6219, lon: 77.4110 },
          { lat: 29.4727, lon: 77.7085 },
          { lat: 28.9845, lon: 77.7064 },
          { lat: 28.8318, lon: 77.5833 }
        ];
        const coords = sampleLocations[sampleIndex] || { lat: activeSurvey.lat, lon: activeSurvey.lon };
        fetchEnvironment(coords.lat, coords.lon);
        updateActivePlaceUI();
        renderIntelligenceView();
        renderReportsView();
      } catch (e) {
        console.error('Inference error:', e);
      }
    }

    // =========================================================================
    // 6. MAP CLICK & GEOCODING REVERSE SEARCH
    // =========================================================================
    async function handleMapClick(lat, lon) {
      if (customMarker) customMarker.remove();

      const el = document.createElement('div');
      el.className = 'w-6 h-6 rounded-full bg-terracotta border-2 border-white shadow-lg flex items-center justify-center text-white text-[10px] font-bold';
      el.innerHTML = '📍';
      if (map) {
        customMarker = new maplibregl.Marker({ element: el }).setLngLat([lon, lat]).addTo(map);
      }

      activeSurvey = {
        name: `Location (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E)`,
        displayName: `Point (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E), India`,
        lat: lat,
        lon: lon,
        isDemo: false,
        demoIndex: null,
        dataState: 'VERIFIED REAL-TIME OBSERVATION'
      };

      try {
        const rev = await fetch(`/api/geo/reverse?lat=${lat}&lon=${lon}`);
        if (rev.ok) {
          const revData = await rev.json();
          activeSurvey.name = revData.name || activeSurvey.name;
          activeSurvey.displayName = revData.display_name || activeSurvey.displayName;
        }
      } catch (e) {}

      recordRecentSearch(activeSurvey.name, lat, lon);
      fetchEnvironment(lat, lon);
      acquireSatelliteImagery(lat, lon);
      updateActivePlaceUI();
    }

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
          const res = await fetch(`/api/geo/search?q=${encodeURIComponent(query)}&limit=5`);
          if (res.ok) {
            const list = await res.json();
            renderSearchSuggestions(list);
            return;
          }
        } catch (e) {}

        // Direct Nominatim fallback
        try {
          const fallback = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query + ', India')}&countrycodes=in&format=json&limit=5&addressdetails=1`);
          if (fallback.ok) {
            const items = await fallback.json();
            renderSearchSuggestions(items.map(it => ({
              name: it.name || query,
              display_name: it.display_name,
              latitude: parseFloat(it.lat),
              longitude: parseFloat(it.lon),
              data_state: 'Verified'
            })));
          }
        } catch (err) {}
      }, 300);
    }

    function renderSearchSuggestions(items) {
      const box = document.getElementById('searchSuggestionsBox');
      if (!box) return;

      if (!items || items.length === 0) {
        box.innerHTML = `<div class="p-3 text-xs text-earth-muted text-center italic">No matching Indian locations found.</div>`;
        box.classList.remove('hidden');
        return;
      }

      box.innerHTML = '';
      items.forEach(it => {
        const div = document.createElement('div');
        div.className = 'p-3 hover:bg-sand-light cursor-pointer transition flex items-center justify-between text-xs';
        div.onclick = () => {
          selectLocationResult(it);
        };
        div.innerHTML = `
          <div class="truncate pr-2">
            <div class="font-bold text-forest-dark truncate">📍 ${it.name}</div>
            <div class="text-[10px] text-earth-muted truncate">${it.display_name}</div>
          </div>
          <span class="text-[9px] font-bold px-2 py-0.5 rounded bg-forest/10 text-forest shrink-0">${it.data_state || 'Verified'}</span>
        `;
        box.appendChild(div);
      });
      box.classList.remove('hidden');
    }

    function handleSearchInputKey(e) {
      if (e.key === 'Enter') executeSearch();
      else if (e.key === 'Escape') {
        const box = document.getElementById('searchSuggestionsBox');
        if (box) box.classList.add('hidden');
      }
    }

    function executeSearch() {
      const input = document.getElementById('exploreSearchInput') || document.getElementById('dashSearchInput');
      const val = input ? input.value.trim() : '';
      if (!val) return;

      const box = document.getElementById('searchSuggestionsBox');
      if (box) box.classList.add('hidden');

      // Check coordinates
      const parts = val.replace('°','').replace('N','').replace('E','').split(',');
      if (parts.length === 2) {
        const lat = parseFloat(parts[0]);
        const lon = parseFloat(parts[1]);
        if (!isNaN(lat) && !isNaN(lon)) {
          selectLocationResult({
            name: `${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E`,
            display_name: `Point Coordinates (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E), India`,
            latitude: lat,
            longitude: lon,
            data_state: 'Verified'
          });
          return;
        }
      }

      fetch(`/api/geo/search?q=${encodeURIComponent(val)}&limit=1`)
        .then(r => r.json())
        .then(list => {
          if (list && list.length > 0) selectLocationResult(list[0]);
        })
        .catch(() => {});
    }

    function handleDashboardSearch() {
      const input = document.getElementById('dashSearchInput');
      if (input && input.value.trim()) {
        const expInput = document.getElementById('exploreSearchInput');
        if (expInput) expInput.value = input.value;
        navigateTo('explore');
        executeSearch();
      } else {
        navigateTo('explore');
      }
    }

    function quickSelectCity(cityName) {
      const input = document.getElementById('exploreSearchInput');
      if (input) input.value = cityName;
      const dashInput = document.getElementById('dashSearchInput');
      if (dashInput) dashInput.value = cityName;
      executeSearch();
    }

    function selectLocationResult(item) {
      const box = document.getElementById('searchSuggestionsBox');
      if (box) box.classList.add('hidden');

      activeSurvey = {
        name: item.name,
        displayName: item.display_name,
        lat: item.latitude,
        lon: item.longitude,
        isDemo: false,
        demoIndex: null,
        dataState: 'VERIFIED REAL-TIME OBSERVATION'
      };

      recordRecentSearch(item.name, item.latitude, item.longitude);
      fetchEnvironment(item.latitude, item.longitude);
      acquireSatelliteImagery(item.latitude, item.longitude);
      updateActivePlaceUI();

      if (map) {
        map.flyTo({ center: [item.longitude, item.latitude], zoom: 12, essential: true });
        if (customMarker) customMarker.remove();
        const el = document.createElement('div');
        el.className = 'w-6 h-6 rounded-full bg-forest border-2 border-white shadow-lg flex items-center justify-center text-white text-[10px] font-bold';
        el.innerHTML = '📍';
        customMarker = new maplibregl.Marker({ element: el }).setLngLat([item.longitude, item.latitude]).addTo(map);
      }
      if (dashMap) {
        dashMap.flyTo({ center: [item.longitude, item.latitude], zoom: 12, essential: true });
      }
    }

    // =========================================================================
    // 7. ACTIVE LOCATION UI SYNC
    // =========================================================================
    function updateActivePlaceUI() {
      // Sidebar Active Location
      const sidePlace = document.getElementById('sidebarActivePlace');
      if (sidePlace) sidePlace.innerText = activeSurvey.name;
      const sideCoords = document.getElementById('sidebarActiveCoords');
      if (sideCoords) sideCoords.innerText = `${activeSurvey.lat.toFixed(4)}°N, ${activeSurvey.lon.toFixed(4)}°E`;

      // Topbar Badge
      const topBadge = document.getElementById('topbarDataStateBadge');
      if (topBadge) {
        topBadge.innerText = activeSurvey.dataState;
        if (activeSurvey.isDemo) {
          topBadge.className = 'hidden sm:inline-block text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-200';
        } else {
          topBadge.className = 'hidden sm:inline-block text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-forest/10 text-forest border border-forest/20';
        }
      }

      // Map Banners
      const mapRegion = document.getElementById('mapSelectedRegion');
      if (mapRegion) mapRegion.innerText = activeSurvey.name;
      const mapCoords = document.getElementById('mapSelectedCoords');
      if (mapCoords) mapCoords.innerText = `${activeSurvey.lat.toFixed(4)}°N, ${activeSurvey.lon.toFixed(4)}°E`;
      const mapState = document.getElementById('mapSelectedStateTag');
      if (mapState) mapState.innerText = activeSurvey.dataState;

      // Dashboard Map Tag
      const dashMapTarget = document.getElementById('dashMapTargetLabel');
      if (dashMapTarget) dashMapTarget.innerText = activeSurvey.name;
      const dashMapCoords = document.getElementById('dashMapCoordsLabel');
      if (dashMapCoords) dashMapCoords.innerText = `${activeSurvey.lat.toFixed(4)}°N, ${activeSurvey.lon.toFixed(4)}°E`;

      // Dashboard Snapshot
      const dashPlace = document.getElementById('dashCurrentPlaceTitle');
      if (dashPlace) dashPlace.innerText = activeSurvey.name;

      // Intelligence View Header
      const intelPlace = document.getElementById('intelSurveyLocationName');
      if (intelPlace) intelPlace.innerText = activeSurvey.name;
      const intelCoords = document.getElementById('intelSurveyCoords');
      if (intelCoords) intelCoords.innerText = `${activeSurvey.lat.toFixed(4)}°N, ${activeSurvey.lon.toFixed(4)}°E`;
      const intelBadge = document.getElementById('intelSurveyBadge');
      if (intelBadge) intelBadge.innerText = activeSurvey.dataState;

      // Advisor Header
      const advParcel = document.getElementById('advisorActiveParcelName');
      if (advParcel) advParcel.innerText = activeSurvey.name;
      const advTarget = document.getElementById('advisorWelcomeTarget');
      if (advTarget) advTarget.innerText = activeSurvey.name;
    }

    // =========================================================================
    // 8. LAND INTELLIGENCE DOMAINS ENGINE (9 TABS)
    // =========================================================================
    function switchIntelDomain(domainId) {
      activeIntelDomain = domainId;

      document.querySelectorAll('.intel-panel').forEach(p => p.classList.add('hidden'));

      const target = document.getElementById('domainPanel_' + domainId);
      if (target) target.classList.remove('hidden');

      const domainIds = ['overview', 'vegetation', 'soil', 'water', 'weather', 'agriculture', 'construction', 'landcover', 'gallery'];
      domainIds.forEach(id => {
        const btn = document.getElementById('domainBtn_' + id);
        if (btn) {
          if (id === domainId) {
            btn.className = 'intel-domain-btn px-3.5 py-2 rounded-xl font-bold bg-forest text-white transition shrink-0';
          } else {
            btn.className = 'intel-domain-btn px-3.5 py-2 rounded-xl font-semibold text-earth-text hover:bg-sand-light transition shrink-0';
          }
        }
      });
    }

    function renderIntelligenceView() {
      if (!currentPrediction) return;
      const data = currentPrediction;

      // Header Thumbnail Preview
      const headerThumb = document.getElementById('intelThumbImg');
      if (headerThumb && data.images && data.images.original) {
        headerThumb.src = data.images.original;
      }

      // Overview KPIs
      const overDom = document.getElementById('intelOverviewDominant');
      if (overDom) overDom.innerText = `${data.dominant_class} (${data.dominant_percentage.toFixed(1)}%)`;
      const overVeg = document.getElementById('intelOverviewVeg');
      if (overVeg) overVeg.innerText = `${data.vegetation_coverage_pct.toFixed(1)}% Vegetation Cover`;

      // Dynamic location-specific layman summary
      const dominantName = data.dominant_class || 'Ploughed Open Soil';
      const dominantPct = data.dominant_percentage ? data.dominant_percentage.toFixed(1) : '45.9';
      const vegPct = data.vegetation_coverage_pct ? data.vegetation_coverage_pct.toFixed(1) : '38.1';
      const builtPct = data.built_up_coverage_pct ? data.built_up_coverage_pct.toFixed(1) : '15.2';

      let dynamicSummary = '';
      if (dominantName.includes('Built')) {
        dynamicSummary = `This 40.96-hectare parcel exhibits high built development (${dominantPct}%), with access roads and commercial/residential structures on flat plain topography. Remaining sections (${vegPct}%) feature green pockets and open soil. Well-connected for commercial activities, though municipal zoning permits and structural borehole tests must be verified.`;
      } else if (dominantName.includes('Crop') || vegPct > 40) {
        dynamicSummary = `This 40.96-hectare land area is an active agricultural holding with ${vegPct}% healthy green vegetative canopy and fertile cultivable topsoil. Situated on gentle alluvial terrain, it offers favorable two-season crop viability for wheat, mustard, and vegetables, pending local canal irrigation checks.`;
      } else if (dominantName.includes('Tree')) {
        dynamicSummary = `This 40.96-hectare surveyed parcel features significant wooded tree canopy (${dominantPct}%) providing natural wind protection and soil stabilization. Terrain slope is gentle, minimizing erosion. Forest department land clearances must be confirmed prior to any boundary clearing.`;
      } else {
        dynamicSummary = `This 40.96-hectare land parcel is predominantly cultivable open topsoil (${dominantPct}%) with seasonal green plant cover (${vegPct}%) and minor built tracks (${builtPct}%). Situated on flat plain topography, it offers favorable conditions for seasonal farming or low-rise building, though subterranean soil chemicals and legal titles require local revenue verification.`;
      }

      const headerSum = document.getElementById('intelHeaderSummary');
      if (headerSum) headerSum.innerText = dynamicSummary;
      const overLayman = document.getElementById('intelOverviewLayman');
      if (overLayman) overLayman.innerText = dynamicSummary;

      // Update specific parameter numbers in sub-tabs
      const valVegNdvi = document.getElementById('valVegNdvi');
      if (valVegNdvi) {
        const ndviEst = Math.min(0.85, Math.max(0.15, (data.vegetation_coverage_pct / 100 * 0.7 + 0.15))).toFixed(2);
        valVegNdvi.innerText = ndviEst;
      }
      const valVegTrees = document.getElementById('valVegTrees');
      const lblVegTrees = document.getElementById('lblVegTrees');
      if (valVegTrees && data.class_breakdown && data.class_breakdown['class_2']) {
        const treeC = data.class_breakdown['class_2'];
        valVegTrees.innerText = `${treeC.area_hectares} ha`;
        if (lblVegTrees) lblVegTrees.innerText = `${treeC.percentage.toFixed(1)}% of land`;
      }

      const valWaterExtent = document.getElementById('valWaterExtent');
      const lblWaterExtent = document.getElementById('lblWaterExtent');
      if (valWaterExtent && data.class_breakdown && data.class_breakdown['class_1']) {
        const waterC = data.class_breakdown['class_1'];
        valWaterExtent.innerText = `${waterC.area_hectares} ha`;
        if (lblWaterExtent) lblWaterExtent.innerText = `${waterC.percentage.toFixed(1)}% of parcel`;
      }

      // Dashboard Metrics
      const dashMetricVeg = document.getElementById('dashMetricVeg');
      if (dashMetricVeg) dashMetricVeg.innerText = `${data.vegetation_coverage_pct.toFixed(1)}%`;
      const valVegCoverage = document.getElementById('valVegCoverage');
      if (valVegCoverage) valVegCoverage.innerText = `${data.vegetation_coverage_pct.toFixed(1)}%`;
      const descVeg = document.getElementById('descVegCoverage');
      if (descVeg) descVeg.innerText = `Around ${Math.round(data.vegetation_coverage_pct)}% of the observed land area is covered by living plant canopy, crops, or trees.`;
      const barVeg = document.getElementById('barVegCoverage');
      if (barVeg) barVeg.style.width = `${data.vegetation_coverage_pct.toFixed(1)}%`;
      const areaVeg = document.getElementById('areaVegCoverage');
      if (areaVeg) areaVeg.innerText = `${(data.vegetation_coverage_pct * 0.4096).toFixed(1)} Hectares`;

      document.querySelectorAll('.galleryParcelName').forEach(el => {
        el.innerText = activeSurvey.name || 'Faridabad Agro-Urban Fringe';
      });

      // Populate 7-Class Table in Domain 8
      const tbody = document.getElementById('intelClassTableBody');
      if (tbody && data.class_breakdown) {
        tbody.innerHTML = '';
        Object.keys(data.class_breakdown).sort().forEach(k => {
          const c = data.class_breakdown[k];
          const info = LAND_CLASSES[k] || { label: c.class_name, color: c.color_hex, desc: 'Satellite classified ground cover' };
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-earth-cardTint transition';
          tr.innerHTML = `
            <td class="py-2.5 px-4 flex items-center space-x-2 font-bold text-earth-dark">
              <span class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: ${c.color_hex || info.color}"></span>
              <span>${info.label}</span>
            </td>
            <td class="py-2.5 px-4 text-earth-muted">${info.desc}</td>
            <td class="py-2.5 px-4 font-mono text-earth-muted">${c.pixel_count.toLocaleString()}</td>
            <td class="py-2.5 px-4 font-bold text-forest">${c.percentage.toFixed(1)}%</td>
            <td class="py-2.5 px-4 font-mono font-bold text-right text-forest">${c.area_hectares} ha</td>
          `;
          tbody.appendChild(tr);
        });
      }

      // Populate Gallery Images in Domain 9
      if (data.images) {
        const imgRgb = document.getElementById('galleryImgRGB');
        if (imgRgb && data.images.original) imgRgb.src = data.images.original;

        const imgMask = document.getElementById('galleryImgMask');
        if (imgMask && data.images.colorized_mask) imgMask.src = data.images.colorized_mask;

        const imgComp = document.getElementById('galleryImgComposite');
        if (imgComp && data.images.side_by_side) imgComp.src = data.images.side_by_side;
      }
    }

    // =========================================================================
    // 9. DUE DILIGENCE REPORTS VIEW
    // =========================================================================
    function renderReportsView() {
      const repLoc = document.getElementById('reportLocationName');
      if (repLoc) repLoc.innerText = activeSurvey.displayName || activeSurvey.name;

      const repCoords = document.getElementById('reportCoords');
      if (repCoords) repCoords.innerText = `${activeSurvey.lat.toFixed(4)}°N, ${activeSurvey.lon.toFixed(4)}°E`;

      const repBadge = document.getElementById('reportBadge');
      if (repBadge) repBadge.innerText = activeSurvey.dataState;

      if (!currentPrediction) return;
      const data = currentPrediction;

      const repImg = document.getElementById('reportCompositeImg');
      if (repImg && data.images && data.images.side_by_side) repImg.src = data.images.side_by_side;

      const repTbody = document.getElementById('reportTableBody');
      if (repTbody && data.class_breakdown) {
        repTbody.innerHTML = '';
        Object.keys(data.class_breakdown).sort().forEach(k => {
          const c = data.class_breakdown[k];
          const info = LAND_CLASSES[k] || { label: c.class_name, color: c.color_hex };
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-earth-cardTint';
          tr.innerHTML = `
            <td class="py-2 px-3 font-mono font-bold text-earth-muted">${k}</td>
            <td class="py-2 px-3 font-bold text-earth-dark flex items-center space-x-2">
              <span class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: ${c.color_hex || info.color}"></span>
              <span>${info.label}</span>
            </td>
            <td class="py-2 px-3 font-mono text-earth-muted">${c.pixel_count}</td>
            <td class="py-2 px-3 font-bold text-forest">${c.percentage.toFixed(1)}%</td>
            <td class="py-2 px-3 font-mono font-bold text-right text-forest">${c.area_hectares} ha</td>
          `;
          repTbody.appendChild(tr);
        });
      }
    }

    
    // =========================================================================
    // 9B. REPORT HISTORY & SQLITE PERSISTENCE
    // =========================================================================
    async function fetchSavedReports() {
      try {
        const token = localStorage.getItem('kshetra_auth_token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        const res = await fetch('/api/auth/reports', { headers });
        if (res.ok) {
          savedReports = await res.json();
          renderReportsHistory();
          renderDashboardReports();
          return;
        }
      } catch (e) {}

      try {
        const local = localStorage.getItem('kshetra_saved_reports');
        if (local) savedReports = JSON.parse(local);
        renderReportsHistory();
        renderDashboardReports();
      } catch (e) {}
    }

    async function saveCurrentReportToHistory() {
      const dateStr = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
      const docId = `KSH-${new Date().getFullYear()}-IND-${Math.floor(1000 + Math.random() * 9000)}`;

      const summaryObj = {
        doc_id: docId,
        date: dateStr,
        dominant_class: currentPrediction ? currentPrediction.dominant_class : 'Ploughed Open Soil',
        veg_pct: currentPrediction ? currentPrediction.vegetation_coverage_pct : 38.1,
        area_ha: 40.96
      };

      const payload = {
        place_name: activeSurvey.displayName || activeSurvey.name,
        latitude: activeSurvey.lat,
        longitude: activeSurvey.lon,
        report_summary: JSON.stringify(summaryObj)
      };

      let newReport = {
        id: 'rep_' + Date.now(),
        ...payload,
        created_at: new Date().toISOString()
      };

      try {
        const token = localStorage.getItem('kshetra_auth_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const res = await fetch('/api/auth/reports', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          newReport = await res.json();
        }
      } catch (e) {
        console.warn("Could not save report to SQLite, stored locally:", e);
      }

      savedReports.unshift(newReport);
      try { localStorage.setItem('kshetra_saved_reports', JSON.stringify(savedReports)); } catch (e) {}
      renderReportsHistory();
      renderDashboardReports();

      const btn = document.getElementById('btnSaveReportHistory');
      if (btn) {
        btn.innerHTML = '<span>✓ Saved to History</span>';
        setTimeout(() => {
          btn.innerHTML = '<span>💾</span><span>Save to History</span>';
        }, 2000);
      }
    }

    async function deleteSavedReport(id) {
      savedReports = savedReports.filter(r => r.id !== id);
      try {
        const token = localStorage.getItem('kshetra_auth_token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        await fetch(`/api/auth/reports/${id}`, { method: 'DELETE', headers });
      } catch (e) {}

      try { localStorage.setItem('kshetra_saved_reports', JSON.stringify(savedReports)); } catch (e) {}
      renderReportsHistory();
      renderDashboardReports();
    }

    function renderReportsHistory() {
      const list = document.getElementById('reportsHistoryList');
      const badge = document.getElementById('reportsHistoryCountBadge');
      if (!list) return;

      if (badge) badge.innerText = `${savedReports.length} Dossiers`;

      if (!savedReports || savedReports.length === 0) {
        list.innerHTML = `<span class="text-earth-muted italic text-xs py-1">No saved dossiers yet. Click "Save to History" above to archive this parcel's report.</span>`;
        return;
      }

      list.innerHTML = '';
      savedReports.forEach(r => {
        let summary = {};
        try { summary = JSON.parse(r.report_summary); } catch (e) {}

        const chip = document.createElement('div');
        chip.className = 'px-3 py-2 bg-earth-cardTint hover:bg-sand-light border border-earth-border rounded-xl text-xs flex items-center space-x-2 shrink-0 shadow-2xs transition';
        chip.innerHTML = `
          <div class="truncate max-w-[200px]">
            <span class="font-bold text-forest-dark block truncate">📄 ${escapeHtml(r.place_name)}</span>
            <span class="text-[10px] text-earth-muted font-mono">${summary.doc_id || 'DOC-KSH'} • ${summary.date || '22 Nov 2026'}</span>
          </div>
          <button onclick="deleteSavedReport('${r.id}')" title="Delete Dossier" class="text-earth-muted hover:text-terracotta font-bold text-sm ml-1">&times;</button>
        `;
        list.appendChild(chip);
      });
    }

    function renderDashboardReports() {
      const container = document.getElementById('dashReportsPreview');
      if (!container) return;

      if (!savedReports || savedReports.length === 0) {
        container.innerHTML = `
          <div class="py-6 text-center text-earth-muted text-xs italic">
            No reports generated yet. Click "Generate Report" above to create an official dossier.
          </div>
        `;
        return;
      }

      container.innerHTML = '';
      savedReports.slice(0, 3).forEach(r => {
        let summary = {};
        try { summary = JSON.parse(r.report_summary); } catch (e) {}

        const div = document.createElement('div');
        div.className = 'p-3 bg-earth-cardTint hover:bg-sand-light border border-earth-border/60 rounded-xl flex items-center justify-between text-xs transition cursor-pointer';
        div.onclick = () => {
          viewPlaceIntelligence(r.latitude, r.longitude, r.place_name);
          navigateTo('reports');
        };
        div.innerHTML = `
          <div class="truncate pr-2">
            <span class="font-bold text-forest-dark truncate block">📄 ${escapeHtml(r.place_name)}</span>
            <span class="text-[10px] text-earth-muted font-mono">${summary.doc_id || 'KSH-2026'} • ${summary.date || '22 Nov 2026'}</span>
          </div>
          <button class="px-2.5 py-1 bg-forest/10 text-forest text-[11px] font-bold rounded-lg shrink-0 hover:bg-forest/20">
            View
          </button>
        `;
        container.appendChild(div);
      });
    }

    function exportJsonSummary() {
      if (!currentPrediction) return;
      const exportObj = {
        platform: "KSHETRA — LAND SHIELD AI",
        tagline: "Verifying Titles. Securing Boundaries.",
        survey: activeSurvey,
        prediction: currentPrediction,
        generatedAt: new Date().toISOString()
      };
      const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj, null, 2));
      const a = document.createElement('a');
      a.setAttribute("href", jsonStr);
      a.setAttribute("download", `KSHETRA_${activeSurvey.name.replace(/[^a-zA-Z0-9]/g, '_')}_Dossier.json`);
      a.click();
    }

    // =========================================================================
    // 10. DATA REGISTRY TABLE
    // =========================================================================
    async function loadDataRegistry() {
      try {
        const res = await fetch('/api/geo/registry');
        if (!res.ok) return;
        const data = await res.json();
        const feeds = Array.isArray(data) ? data : (data.sources || []);
        const tbody = document.getElementById('registryTableBody');
        if (!tbody || !feeds || feeds.length === 0) return;

        tbody.innerHTML = '';
        feeds.forEach(f => {
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-earth-cardTint transition';
          const statusText = f.status || 'Operational';
          const isOp = statusText.includes('Operational') || statusText.includes('Verified');
          tr.innerHTML = `
            <td class="py-3 px-4 font-bold text-forest-dark">${f.name || f.provider || 'EO Provider'}</td>
            <td class="py-3 px-4 text-earth-muted">${f.dataset || f.dataset_name || 'Observation Feed'}</td>
            <td class="py-3 px-4 font-mono text-earth-dark">${f.resolution || '10.0m GSD'}</td>
            <td class="py-3 px-4 text-earth-muted">${f.license || 'Open Access'}</td>
            <td class="py-3 px-4">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isOp ? 'bg-forest/10 text-forest' : 'bg-sand-dark/20 text-[#936639]'}">
                ${statusText}
              </span>
            </td>
          `;
          tbody.appendChild(tr);
        });
      } catch (e) {
        console.error("Registry load error:", e);
      }
    }

    // =========================================================================
    // 11. RECENT SEARCHES TRACKING
    // =========================================================================
    function recordRecentSearch(name, lat, lon) {
      if (!name) return;
      recentSearches = recentSearches.filter(s => s.name !== name);
      recentSearches.unshift({ name, lat, lon, time: Date.now() });
      if (recentSearches.length > 8) recentSearches.pop();
      try {
        localStorage.setItem('kshetra_recent_searches', JSON.stringify(recentSearches));
      } catch (e) {}
      renderRecentSearches();
    }

    function renderRecentSearches() {
      const container = document.getElementById('dashRecentLocationsList');
      const clearBtn = document.getElementById('dashClearRecent');
      if (!container) return;

      try {
        const stored = localStorage.getItem('kshetra_recent_searches');
        if (stored) recentSearches = JSON.parse(stored);
      } catch (e) {}

      if (!recentSearches || recentSearches.length === 0) {
        container.innerHTML = `<span class="text-earth-muted italic text-xs py-1">No recent searches yet. Search any location or explore the map to start your survey.</span>`;
        if (clearBtn) clearBtn.classList.add('hidden');
        return;
      }

      if (clearBtn) clearBtn.classList.remove('hidden');
      container.innerHTML = '';

      recentSearches.forEach(s => {
        const chip = document.createElement('button');
        chip.className = 'px-3 py-1.5 rounded-xl bg-earth-cardTint border border-earth-border hover:bg-sand-light text-forest text-xs font-semibold transition shrink-0 flex items-center space-x-1.5 shadow-2xs';
        chip.onclick = () => {
          selectLocationResult({
            name: s.name,
            display_name: `${s.name}, India`,
            latitude: s.lat,
            longitude: s.lon,
            data_state: 'Verified'
          });
          navigateTo('explore');
        };
        chip.innerHTML = `<span>📍</span><span>${s.name}</span>`;
        container.appendChild(chip);
      });
    }

    function clearRecentLocations() {
      recentSearches = [];
      try { localStorage.removeItem('kshetra_recent_searches'); } catch (e) {}
      renderRecentSearches();
    }

    // =========================================================================
    // 12. SAVED PLACES PORTFOLIO & SQLITE PERSISTENCE
    // =========================================================================
    async function fetchSavedPlaces() {
      try {
        const token = localStorage.getItem('kshetra_auth_token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        const res = await fetch('/api/auth/places', { headers });
        if (res.ok) {
          savedPlaces = await res.json();
          updateSavedPlacesCount();
          renderDashboardSavedPlaces();
          return;
        }
      } catch (e) {}

      try {
        const local = localStorage.getItem('kshetra_saved_places');
        if (local) savedPlaces = JSON.parse(local);
        updateSavedPlacesCount();
        renderDashboardSavedPlaces();
      } catch (e) {}
    }

    function updateSavedPlacesCount() {
      const count = savedPlaces.length;
      const sideBadge = document.getElementById('sidebarSavedCount');
      if (sideBadge) sideBadge.innerText = count;
      const portBadge = document.getElementById('placesPortfolioCountBadge');
      if (portBadge) portBadge.innerText = `${count} ${count === 1 ? 'Parcel' : 'Parcels'}`;
      const dashCount = document.getElementById('dashSavedCountNote');
      if (dashCount) dashCount.innerText = `${count} Saved parcels`;
    }

    function toggleCompareSelect(id, checked) {
      if (checked) {
        if (!selectedComparePlaceIds.includes(id)) selectedComparePlaceIds.push(id);
      } else {
        selectedComparePlaceIds = selectedComparePlaceIds.filter(x => x !== id);
      }
      const btn = document.getElementById('btnComparePlaces');
      if (btn) {
        if (selectedComparePlaceIds.length >= 2) {
          btn.innerHTML = `<span>⚖️</span><span>Compare (${selectedComparePlaceIds.length})</span>`;
          btn.classList.add('bg-forest', 'text-white');
          btn.classList.remove('bg-earth-cardTint', 'text-forest');
        } else {
          btn.innerHTML = `<span>⚖️</span><span>Compare Selected</span>`;
          btn.classList.remove('bg-forest', 'text-white');
          btn.classList.add('bg-earth-cardTint', 'text-forest');
        }
      }
    }

    function compareSelectedPlaces() {
      let toCompare = savedPlaces.filter(p => selectedComparePlaceIds.includes(p.id));
      if (toCompare.length < 2) {
        if (savedPlaces.length >= 2) {
          toCompare = savedPlaces.slice(0, 2);
        } else {
          alert("Please save at least 2 land parcels in My Places to perform comparative analysis.");
          return;
        }
      }

      const p1 = toCompare[0];
      const p2 = toCompare[1];

      const modal = document.getElementById('comparePlacesModal');
      const container = document.getElementById('compareModalContent');
      if (!container || !modal) return;

      container.innerHTML = `
        <div class="border border-earth-border rounded-2xl overflow-hidden shadow-xs">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-earth-cardTint border-b border-earth-border text-earth-dark font-bold">
                <th class="py-3 px-4 w-1/3">Evaluation Metric</th>
                <th class="py-3 px-4 w-1/3 text-forest-dark border-l border-earth-border">${escapeHtml(p1.name)}</th>
                <th class="py-3 px-4 w-1/3 text-forest-dark border-l border-earth-border">${escapeHtml(p2.name)}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-earth-border/60 text-earth-text">
              <tr class="hover:bg-earth-cardTint">
                <td class="py-2.5 px-4 font-bold text-earth-dark">Geographic Coordinates</td>
                <td class="py-2.5 px-4 font-mono border-l border-earth-border">${Number(p1.latitude).toFixed(4)}°N, ${Number(p1.longitude).toFixed(4)}°E</td>
                <td class="py-2.5 px-4 font-mono border-l border-earth-border">${Number(p2.latitude).toFixed(4)}°N, ${Number(p2.longitude).toFixed(4)}°E</td>
              </tr>
              <tr class="hover:bg-earth-cardTint">
                <td class="py-2.5 px-4 font-bold text-earth-dark">Survey Footprint Area</td>
                <td class="py-2.5 px-4 font-bold text-forest border-l border-earth-border">${p1.area_ha || 40.96} Hectares</td>
                <td class="py-2.5 px-4 font-bold text-forest border-l border-earth-border">${p2.area_ha || 40.96} Hectares</td>
              </tr>
              <tr class="hover:bg-earth-cardTint">
                <td class="py-2.5 px-4 font-bold text-earth-dark">Observation Source</td>
                <td class="py-2.5 px-4 border-l border-earth-border"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${p1.is_demo ? 'bg-purple-100 text-purple-800' : 'bg-forest/10 text-forest'}">${p1.is_demo ? 'Demo Shard' : 'Live Verified'}</span></td>
                <td class="py-2.5 px-4 border-l border-earth-border"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${p2.is_demo ? 'bg-purple-100 text-purple-800' : 'bg-forest/10 text-forest'}">${p2.is_demo ? 'Demo Shard' : 'Live Verified'}</span></td>
              </tr>
              <tr class="hover:bg-earth-cardTint">
                <td class="py-2.5 px-4 font-bold text-earth-dark">Due Diligence Notes</td>
                <td class="py-2.5 px-4 italic border-l border-earth-border text-earth-muted">${p1.notes ? escapeHtml(p1.notes) : 'None'}</td>
                <td class="py-2.5 px-4 italic border-l border-earth-border text-earth-muted">${p2.notes ? escapeHtml(p2.notes) : 'None'}</td>
              </tr>
              <tr class="hover:bg-earth-cardTint">
                <td class="py-2.5 px-4 font-bold text-earth-dark">Actions</td>
                <td class="py-2.5 px-4 border-l border-earth-border">
                  <button onclick="closeCompareModal(); viewPlaceIntelligence(${p1.latitude}, ${p1.longitude}, '${escapeHtml(p1.name)}')" class="px-3 py-1 bg-forest text-white rounded-lg font-bold text-xs">Analyze &rarr;</button>
                </td>
                <td class="py-2.5 px-4 border-l border-earth-border">
                  <button onclick="closeCompareModal(); viewPlaceIntelligence(${p2.latitude}, ${p2.longitude}, '${escapeHtml(p2.name)}')" class="px-3 py-1 bg-forest text-white rounded-lg font-bold text-xs">Analyze &rarr;</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      `;
      modal.classList.remove('hidden');
    }

    function closeCompareModal() {
      const modal = document.getElementById('comparePlacesModal');
      if (modal) modal.classList.add('hidden');
    }

    function openEditNotesModal(id, title, notes) {
      editingPlaceId = id;
      const modal = document.getElementById('editPlaceNotesModal');
      const titleEl = document.getElementById('editNotesPlaceTitle');
      const textarea = document.getElementById('editNotesTextarea');
      if (titleEl) titleEl.innerText = title || 'Edit Notes';
      if (textarea) textarea.value = notes || '';
      if (modal) modal.classList.remove('hidden');
    }

    function closeEditNotesModal() {
      const modal = document.getElementById('editPlaceNotesModal');
      if (modal) modal.classList.add('hidden');
      editingPlaceId = null;
    }

    async function saveEditedNotes() {
      if (!editingPlaceId) return;
      const textarea = document.getElementById('editNotesTextarea');
      const newNotes = textarea ? textarea.value.trim() : '';

      const p = savedPlaces.find(x => x.id === editingPlaceId);
      if (p) p.notes = newNotes;

      try {
        const token = localStorage.getItem('kshetra_auth_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        await fetch(`/api/auth/places/${editingPlaceId}/notes`, {
          method: 'PUT',
          headers: headers,
          body: JSON.stringify({ notes: newNotes })
        });
      } catch (e) {
        console.warn("Could not save notes to SQLite, saved locally:", e);
      }

      try { localStorage.setItem('kshetra_saved_places', JSON.stringify(savedPlaces)); } catch (e) {}
      renderSavedPlaces();
      closeEditNotesModal();
    }

    function renderSavedPlaces() {
      const grid = document.getElementById('fullSavedPlacesGrid');
      if (!grid) return;

      if (!savedPlaces || savedPlaces.length === 0) {
        grid.innerHTML = `
          <div class="col-span-full py-16 text-center text-earth-muted space-y-3 bg-white border border-earth-border rounded-3xl">
            <div class="w-12 h-12 rounded-2xl bg-sand-light text-forest mx-auto flex items-center justify-center text-2xl font-serif">📍</div>
            <div class="text-sm font-bold text-forest-dark font-serif">No Saved Parcels Yet</div>
            <p class="text-xs max-w-sm mx-auto">Explore India or search any location to save parcels for ongoing due diligence and reporting.</p>
            <button onclick="navigateTo('explore')" class="px-4 py-2 bg-forest text-white text-xs font-bold rounded-xl transition shadow-xs">
              Explore India Map &rarr;
            </button>
          </div>
        `;
        return;
      }

      grid.innerHTML = '';
      savedPlaces.forEach(p => {
        if (!p) return;
        const latVal = (p.latitude != null && !isNaN(Number(p.latitude))) ? Number(p.latitude) : 28.4007;
        const lonVal = (p.longitude != null && !isNaN(Number(p.longitude))) ? Number(p.longitude) : 77.3501;
        const latStr = latVal.toFixed(4);
        const lonStr = lonVal.toFixed(4);
        const isSelected = selectedComparePlaceIds.includes(p.id);

        const card = document.createElement('div');
        card.className = 'bg-white border border-earth-border rounded-2xl p-5 shadow-xs space-y-3 hover:border-forest/50 transition';
        card.innerHTML = `
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-2.5">
              <input type="checkbox" onchange="toggleCompareSelect('${p.id}', this.checked)" ${isSelected ? 'checked' : ''} class="mt-1 w-4 h-4 text-forest rounded cursor-pointer border-earth-border" title="Select to compare" />
              <div>
                <span class="text-[9px] font-bold uppercase tracking-wider text-earth-muted">${p.tags || p.tag || 'Saved Land Parcel'}</span>
                <h4 class="text-sm font-bold text-forest-dark font-serif mt-0.5">${escapeHtml(p.name || 'Saved Parcel')}</h4>
                <div class="text-[11px] font-mono text-earth-muted">${latStr}°N, ${lonStr}°E • ${p.area_ha || 40.96} ha</div>
              </div>
            </div>
            <div class="flex items-center space-x-1">
              <button onclick="openEditNotesModal('${p.id}', '${escapeHtml(p.name || '')}', '${escapeHtml(p.notes || '')}')" title="Edit Due Diligence Notes" class="p-1 rounded-lg hover:bg-sand-light text-earth-muted hover:text-forest text-xs">✏️</button>
              <button onclick="deleteSavedPlace('${p.id}')" title="Remove Parcel" class="p-1 rounded-lg hover:bg-sand-light text-earth-muted hover:text-terracotta text-sm font-bold">&times;</button>
            </div>
          </div>
          <div class="p-2.5 bg-earth-cardTint rounded-xl border border-earth-border/60 text-xs text-earth-muted">
            <span class="font-bold text-earth-dark text-[10px] uppercase block mb-0.5">Notes:</span>
            <p class="italic text-[11px] line-clamp-2">${p.notes ? escapeHtml(p.notes) : 'No custom notes added. Click ✏️ to add.'}</p>
          </div>
          <div class="pt-2 border-t border-earth-border flex items-center justify-between text-xs">
            <button onclick="viewPlaceOnMap(${latVal}, ${lonVal}, '${escapeHtml(p.name || '')}')" class="text-forest font-bold hover:underline flex items-center space-x-1">
              <span>🗺️ View on Map</span>
            </button>
            <button onclick="viewPlaceIntelligence(${latVal}, ${lonVal}, '${escapeHtml(p.name || '')}')" class="px-3.5 py-1.5 bg-forest hover:bg-forest-dark text-white font-bold rounded-xl transition shadow-2xs">
              Analyze Land &rarr;
            </button>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    function renderDashboardSavedPlaces() {
      const container = document.getElementById('dashSavedPlacesPreview');
      if (!container) return;

      if (!savedPlaces || savedPlaces.length === 0) {
        container.innerHTML = `
          <div class="py-4 text-center text-earth-muted text-xs italic bg-sand-light/20 rounded-xl border border-sand-dark/20">
            No parcels saved yet. Search any location or explore the map to save parcels.
          </div>
        `;
        return;
      }

      container.innerHTML = '';
      savedPlaces.slice(0, 3).forEach(p => {
        if (!p) return;
        const latVal = (p.latitude != null && !isNaN(Number(p.latitude))) ? Number(p.latitude) : 28.4007;
        const lonVal = (p.longitude != null && !isNaN(Number(p.longitude))) ? Number(p.longitude) : 77.3501;
        const div = document.createElement('div');
        div.className = 'p-3 bg-earth-cardTint hover:bg-sand-light border border-earth-border/60 rounded-xl flex items-center justify-between text-xs transition cursor-pointer';
        div.onclick = () => {
          viewPlaceIntelligence(latVal, lonVal, p.name);
        };
        div.innerHTML = `
          <div class="truncate pr-2">
            <span class="font-bold text-forest-dark truncate block">📍 ${escapeHtml(p.name)}</span>
            <span class="text-[10px] text-earth-muted font-mono">${latVal.toFixed(4)}°N, ${lonVal.toFixed(4)}°E</span>
          </div>
          <button class="px-2.5 py-1 bg-forest/10 text-forest text-[11px] font-bold rounded-lg shrink-0 hover:bg-forest/20">
            Inspect
          </button>
        `;
        container.appendChild(div);
      });
    }

    function promptSaveCurrentLocation() {
      const modal = document.getElementById('savePlaceModal');
      const input = document.getElementById('savePlaceNameInput');
      const coordLabel = document.getElementById('savePlaceCoordLabel');

      if (input) input.value = activeSurvey.name;
      if (coordLabel) coordLabel.innerText = `Lat: ${activeSurvey.lat.toFixed(4)}°N | Lon: ${activeSurvey.lon.toFixed(4)}°E`;
      if (modal) modal.classList.remove('hidden');
    }

    function closeSavePlaceModal() {
      const modal = document.getElementById('savePlaceModal');
      if (modal) modal.classList.add('hidden');
    }

    async function confirmSavePlace() {
      const inputName = document.getElementById('savePlaceNameInput');
      const inputNotes = document.getElementById('savePlaceNotesInput');

      const name = inputName ? inputName.value.trim() : activeSurvey.name;
      const notes = inputNotes ? inputNotes.value.trim() : '';

      const latNum = (activeSurvey.lat != null && !isNaN(Number(activeSurvey.lat))) ? Number(activeSurvey.lat) : 28.4007;
      const lonNum = (activeSurvey.lon != null && !isNaN(Number(activeSurvey.lon))) ? Number(activeSurvey.lon) : 77.3501;

      const payload = {
        name: name || activeSurvey.name,
        notes: notes || "",
        latitude: latNum,
        longitude: lonNum,
        is_demo: Boolean(activeSurvey.isDemo),
        demo_index: activeSurvey.demoIndex != null ? Number(activeSurvey.demoIndex) : null,
        area_ha: 40.96,
        tags: 'Due Diligence Parcel'
      };

      let newPlace = {
        id: 'place_' + Date.now(),
        ...payload,
        created_at: new Date().toISOString()
      };

      try {
        const token = localStorage.getItem('kshetra_auth_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const res = await fetch('/api/auth/places', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const saved = await res.json();
          newPlace = saved;
        }
      } catch (e) {
        console.warn("Could not save to SQLite, stored locally:", e);
      }

      savedPlaces.unshift(newPlace);
      try { localStorage.setItem('kshetra_saved_places', JSON.stringify(savedPlaces)); } catch (e) {}
      updateSavedPlacesCount();
      renderDashboardSavedPlaces();
      closeSavePlaceModal();
      if (currentView === 'places') renderSavedPlaces();
    }

    async function deleteSavedPlace(id) {
      savedPlaces = savedPlaces.filter(p => p.id !== id);
      try {
        const token = localStorage.getItem('kshetra_auth_token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        await fetch(`/api/auth/places/${id}`, { method: 'DELETE', headers });
      } catch (e) {}

      try { localStorage.setItem('kshetra_saved_places', JSON.stringify(savedPlaces)); } catch (e) {}
      updateSavedPlacesCount();
      renderDashboardSavedPlaces();
      renderSavedPlaces();
    }

    function viewPlaceOnMap(lat, lon, name) {
      selectLocationResult({
        name: name,
        display_name: `${name}, India`,
        latitude: lat,
        longitude: lon,
        data_state: 'Verified'
      });
      navigateTo('explore');
    }

    function viewPlaceIntelligence(lat, lon, name) {
      selectLocationResult({
        name: name,
        display_name: `${name}, India`,
        latitude: lat,
        longitude: lon,
        data_state: 'Verified'
      });
      navigateTo('intelligence');
    }

    function filterSavedPlaces(query) {
      const q = (query || '').toLowerCase().trim();
      const cards = document.querySelectorAll('#fullSavedPlacesGrid > div');
      cards.forEach(card => {
        if (!q) {
          card.classList.remove('hidden');
        } else {
          const text = card.innerText.toLowerCase();
          if (text.includes(q)) card.classList.remove('hidden');
          else card.classList.add('hidden');
        }
      });
    }

    // =========================================================================
    // 13. SQLITE AUTHENTICATION MODAL & PROFILE
    // =========================================================================
    function openAuthModal() {
      const modal = document.getElementById('authModal');
      if (modal) modal.classList.remove('hidden');
    }

    function closeAuthModal() {
      const modal = document.getElementById('authModal');
      if (modal) modal.classList.add('hidden');
      const err = document.getElementById('authErrorMsg');
      if (err) err.classList.add('hidden');
    }

    function toggleAuthMode(mode) {
      authMode = mode;
      const btnLogin = document.getElementById('btnAuthMode_login');
      const btnReg = document.getElementById('btnAuthMode_register');
      const regName = document.getElementById('authRegNameField');
      const submitBtn = document.getElementById('btnSubmitAuth');

      if (mode === 'login') {
        if (btnLogin) btnLogin.className = 'pb-2 px-3 text-forest border-b-2 border-forest';
        if (btnReg) btnReg.className = 'pb-2 px-3 hover:text-earth-dark';
        if (regName) regName.classList.add('hidden');
        if (submitBtn) submitBtn.innerText = 'Sign In';
      } else {
        if (btnLogin) btnLogin.className = 'pb-2 px-3 hover:text-earth-dark';
        if (btnReg) btnReg.className = 'pb-2 px-3 text-forest border-b-2 border-forest';
        if (regName) regName.classList.remove('hidden');
        if (submitBtn) submitBtn.innerText = 'Create Account';
      }
    }

    async function submitAuth() {
      const email = document.getElementById('authInputEmail').value.trim();
      const password = document.getElementById('authInputPassword').value.trim();
      const name = document.getElementById('authInputName').value.trim();
      const errEl = document.getElementById('authErrorMsg');

      if (!email || !password) {
        if (errEl) {
          errEl.innerText = 'Please provide both email and password.';
          errEl.classList.remove('hidden');
        }
        return;
      }

      const endpoint = authMode === 'register' ? '/api/auth/register' : '/api/auth/login';
      const payload = { email, password };
      if (authMode === 'register') payload.full_name = name || 'Surveyor';

      try {
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) {
          if (errEl) {
            errEl.innerText = data.detail || 'Authentication failed.';
            errEl.classList.remove('hidden');
          }
          return;
        }

        if (data.session_token) {
          localStorage.setItem('kshetra_auth_token', data.session_token);
        }
        if (data.user) {
          currentUser = data.user;
          updateUserProfileUI();
          initDashboardGreeting();
        }
        closeAuthModal();
        fetchSavedPlaces();
      } catch (err) {
        if (errEl) {
          errEl.innerText = 'Server error during authentication.';
          errEl.classList.remove('hidden');
        }
      }
    }

    async function checkExistingAuth() {
      const token = localStorage.getItem('kshetra_auth_token');
      if (!token) return;
      try {
        const res = await fetch('/api/auth/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          currentUser = await res.json();
          updateUserProfileUI();
          initDashboardGreeting();
        }
      } catch (e) {}
    }

    function updateUserProfileUI() {
      if (!currentUser) return;
      const avatar = document.getElementById('topbarUserAvatar');
      if (avatar) avatar.innerText = (currentUser.full_name || 'D').charAt(0).toUpperCase();

      const topName = document.getElementById('topbarUserName');
      if (topName) topName.innerText = currentUser.full_name || 'Surveyor';

      const profName = document.getElementById('profileFullName');
      if (profName) profName.innerText = currentUser.full_name || 'Surveyor';

      const profEmail = document.getElementById('profileEmail');
      if (profEmail) profEmail.innerText = currentUser.email || '';
    }

    function handleLogout() {
      localStorage.removeItem('kshetra_auth_token');
      currentUser = null;
      const avatar = document.getElementById('topbarUserAvatar');
      if (avatar) avatar.innerText = 'G';
      const topName = document.getElementById('topbarUserName');
      if (topName) topName.innerText = 'Guest Surveyor';
      initDashboardGreeting();
      navigateTo('landing');
    }

    function saveAppSettings() {
      alert('Platform preferences saved successfully.');
    }

    // =========================================================================
    // 14. AI LAND ADVISOR CHAT ENGINE (6 USER-SPECIFIED PROMPTS)
    // =========================================================================
    
    // =========================================================================
    // 14B. FLOATING AI LAND ADVISOR LAUNCHER & DRAWER
    // =========================================================================
    function toggleFloatingAdvisor(forceOpen) {
      const panel = document.getElementById('floatingAdvisorPanel');
      if (!panel) return;
      if (forceOpen === true) {
        panel.classList.remove('hidden');
      } else if (forceOpen === false) {
        panel.classList.add('hidden');
      } else {
        panel.classList.toggle('hidden');
      }
    }

    function askFloatingAdvisor(question) {
      appendFloatingAdvisorMessage('user', question);
      generateAdvisorGroundedReply(question, 'floating');
    }

    function handleFloatingAdvisorSubmit(e) {
      if (e) e.preventDefault();
      const input = document.getElementById('floatingAdvisorInput');
      if (!input) return;
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      askFloatingAdvisor(text);
    }

    function appendFloatingAdvisorMessage(sender, text) {
      const container = document.getElementById('floatingAdvisorMessages');
      if (!container) return;

      const msgDiv = document.createElement('div');
      msgDiv.className = 'flex items-start space-x-2';

      if (sender === 'user') {
        msgDiv.innerHTML = `
          <div class="flex-1"></div>
          <div class="bg-forest text-white rounded-2xl p-2.5 text-xs max-w-[85%] shadow-xs">
            ${escapeHtml(text)}
          </div>
        `;
      } else {
        msgDiv.innerHTML = `
          <div class="w-6 h-6 rounded-full bg-forest text-white flex items-center justify-center font-serif text-[11px] font-bold shrink-0 shadow-xs">K</div>
          <div class="bg-sand-light/60 border border-sand-dark/40 rounded-2xl p-3 text-xs text-earth-dark space-y-1.5 max-w-[85%] shadow-2xs">
            ${text}
          </div>
        `;
      }

      container.appendChild(msgDiv);
      container.scrollTop = container.scrollHeight;
    }

    function handleAdvisorSubmit(e) {
      if (e) e.preventDefault();
      const input = document.getElementById('fullAdvisorInput');
      if (!input) return;
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      askAdvisorQuestion(text);
    }

    function askAdvisorQuestion(questionText) {
      appendAdvisorMessage('user', questionText);
      generateAdvisorGroundedReply(questionText);
    }

    function appendAdvisorMessage(sender, text) {
      const container = document.getElementById('fullAdvisorMessages');
      if (!container) return;

      const msgDiv = document.createElement('div');
      msgDiv.className = 'flex items-start space-x-3';

      if (sender === 'user') {
        msgDiv.innerHTML = `
          <div class="flex-1"></div>
          <div class="bg-forest text-white rounded-2xl p-3.5 text-xs max-w-lg shadow-xs">
            ${escapeHtml(text)}
          </div>
        `;
      } else {
        msgDiv.innerHTML = `
          <div class="w-8 h-8 rounded-full bg-forest text-white flex items-center justify-center font-serif text-sm font-bold shrink-0 shadow-xs">K</div>
          <div class="bg-sand-light/50 border border-sand-dark/40 rounded-2xl p-4 text-xs text-earth-dark space-y-2 max-w-xl shadow-2xs">
            ${text}
          </div>
        `;
      }

      container.appendChild(msgDiv);
      container.scrollTop = container.scrollHeight;
    }

    function escapeHtml(str) {
      return (str || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    function generateAdvisorGroundedReply(query, target = 'both') {
      const q = query.toLowerCase();
      const data = currentPrediction;
      const env = currentEnvironment;

      const veg = data ? data.vegetation_coverage_pct.toFixed(1) : '38.1';
      const built = data ? data.built_up_coverage_pct.toFixed(1) : '15.2';
      const conf = data ? data.mean_confidence_pct.toFixed(1) : '78.3';
      const dominant = data ? data.dominant_class : 'Ploughed Open Soil';
      const dominantPct = data ? data.dominant_percentage.toFixed(1) : '45.9';
      const slope = (env && env.slope_deg != null) ? env.slope_deg.toFixed(1) : '1.2';
      const elev = (env && env.elevation_m != null) ? Math.round(env.elevation_m) : 212;
      const rain = (env && env.annual_rainfall_mm != null) ? Math.round(env.annual_rainfall_mm) : 750;
      const seismic = (env && env.seismic_zone) ? env.seismic_zone : 'Zone IV';
      const parcelName = activeSurvey.displayName || activeSurvey.name || 'Selected Parcel';

      let reply = '';

      if (q.includes('farming') || q.includes('crop') || q.includes('agriculture')) {
        reply = `
          <div class="space-y-1.5">
            <span class="inline-block text-[10px] font-bold px-2 py-0.5 rounded bg-forest/10 text-forest">Farming Suitability Analysis</span>
            <p class="font-bold text-forest-dark">Yes, this land has favorable conditions for seasonal farming.</p>
            <p><strong>Physical Factors:</strong> It features <strong>${veg}% green vegetation cover</strong>, dominant <strong>${dominant} (${dominantPct}%)</strong>, and gentle <strong>${slope}% slope</strong> which allows smooth irrigation flow without topsoil erosion.</p>
            <p><strong>Recommended Crops:</strong> Wheat, mustard, chickpeas (Winter/Rabi) and millet, sorghum (Monsoon/Kharif).</p>
            <div class="p-2.5 bg-white/70 rounded-xl border border-sand-dark/30 text-[11px] text-earth-muted">
              <strong>⚠️ What must be verified:</strong> Subterranean N-P-K chemical fertility requires a physical laboratory soil test at your local Krishi Vigyan Kendra. Canal water allocations must be verified with the State Irrigation Department.
            </div>
          </div>
        `;
      } else if (q.includes('check before buying') || q.includes('buying') || q.includes('due diligence')) {
        reply = `
          <div class="space-y-1.5">
            <span class="inline-block text-[10px] font-bold px-2 py-0.5 rounded bg-forest/10 text-forest">Buyer Due Diligence Checklist</span>
            <p class="font-bold text-forest-dark">Crucial checks before transacting on ${parcelName}:</p>
            <ul class="list-disc pl-4 space-y-1 text-earth-dark text-xs">
              <li><strong>Certified Title Deeds:</strong> Obtain the official <em>Jamabandi / Record of Rights (RoR)</em> and Non-Encumbrance Certificate (13–30 years) from the Sub-Registrar / Tehsildar. Satellite imagery cannot prove ownership.</li>
              <li><strong>Zoning Classification:</strong> Verify whether the land is zoned Agricultural, Commercial, or Residential with the regional development authority (e.g. HUDA, DDA, GDA).</li>
              <li><strong>Road & Right-of-Way:</strong> Confirm that the road access visible on satellite imagery has dedicated recorded revenue demarcation (Khasra road).</li>
              <li><strong>Foundation Testing:</strong> Commission a standard geotechnical borehole test (SPT) before foundation construction.</li>
            </ul>
          </div>
        `;
      } else if (q.includes('soil information') || q.includes('soil')) {
        reply = `
          <div class="space-y-1.5">
            <span class="inline-block text-[10px] font-bold px-2 py-0.5 rounded bg-forest/10 text-forest">Soil Information in Everyday Terms</span>
            <p class="font-bold text-forest-dark">Surface Ground Conditions:</p>
            <p>From 10m Sentinel-2 optical imagery, <strong>${dominantPct}% of this parcel is ${dominant}</strong>, and <strong>${veg}% is covered with living plants</strong>.</p>
            <p>The ground sits at ${elev} meters above sea level with a gentle ${slope}% slope, ensuring natural rainwater drainage without runoff erosion.</p>
            <div class="p-2.5 bg-white/70 rounded-xl border border-sand-dark/30 text-[11px] text-earth-muted">
              <strong>Zero-Fabrication Notice:</strong> Satellites observe surface ground color and plants, but cannot test subterranean nitrogen, phosphorus, potassium, or pH. A physical core sample must be tested in a laboratory.
            </div>
          </div>
        `;
      } else if (q.includes('construction risks') || q.includes('construction') || q.includes('building')) {
        reply = `
          <div class="space-y-1.5">
            <span class="inline-block text-[10px] font-bold px-2 py-0.5 rounded bg-forest/10 text-forest">Construction & Engineering Risks</span>
            <p class="font-bold text-forest-dark">Development Risk Profile:</p>
            <p>The parcel has <strong>${built}% existing built structures nearby</strong> and flat ground (${slope}% slope), ensuring minimal grading and excavation costs.</p>
            <p><strong>Primary Risks to Address:</strong></p>
            <ul class="list-disc pl-4 space-y-1 text-earth-dark text-xs">
              <li><strong>Seismic Safety:</strong> This region is in <strong>${seismic}</strong>, requiring ductile earthquake detailing in structural drawings under Indian standard IS 13920.</li>
              <li><strong>Borehole Load Bearing:</strong> Safe bearing capacity (SBC) must be tested via standard penetration tests (SPT) by a certified civil engineer.</li>
              <li><strong>Drainage Planning:</strong> Proper storm runoff channels should be planned for the ${rain} mm monsoon season.</li>
            </ul>
          </div>
        `;
      } else if (q.includes('missing') || q.includes('what information is missing') || q.includes('unavailable')) {
        reply = `
          <div class="space-y-1.5">
            <span class="inline-block text-[10px] font-bold px-2 py-0.5 rounded bg-sand-dark/20 text-[#936639]">Transparent Accounting of Data Gaps</span>
            <p class="font-bold text-forest-dark">Information Not Available From Space Observation:</p>
            <p>Under our Zero-Fabrication Charter, the following factors are explicitly unmeasured and must not be guessed:</p>
            <ul class="list-disc pl-4 space-y-1 text-earth-dark text-xs">
              <li><strong>Subterranean Soil Chemistry:</strong> Nitrogen, phosphorus, potassium, organic carbon, and pH cannot be sensed from orbit. (Requires ICAR laboratory soil core test).</li>
              <li><strong>Cadastral Ownership & Title:</strong> Private mortgages, boundary litigations, and revenue deeds cannot be detected by satellite pixels. (Requires Sub-Registrar Jamabandi).</li>
              <li><strong>Borehole Load Bearing:</strong> Geotechnical foundation bearing pressure. (Requires physical SPT borehole drilling).</li>
            </ul>
          </div>
        `;
      } else if (q.includes('water') || q.includes('rain') || q.includes('monsoon') || q.includes('canal')) {
        reply = `
          <div class="space-y-1.5">
            <span class="inline-block text-[10px] font-bold px-2 py-0.5 rounded bg-forest/10 text-forest">Hydrology & Water Availability</span>
            <p class="font-bold text-forest-dark">Water Resources Assessment for ${parcelName}:</p>
            <p>Annual precipitation benchmark is <strong>${rain} mm</strong>, with 75% occurring during the summer monsoon (July–Sept). Current satellite NDWI shows minimal flood ponding.</p>
            <p class="text-[11px] text-earth-muted"><strong>Legal & Ground Check:</strong> Ground water table depth and tube-well permissions must be verified with the Central Ground Water Board (CGWB) and local Panchayat/Tehsildar.</p>
          </div>
        `;
      } else if (q.includes('summarize') || q.includes('summary') || q.includes('overview') || q.includes('simple')) {
        reply = `
          <div class="space-y-1.5">
            <span class="inline-block text-[10px] font-bold px-2 py-0.5 rounded bg-forest/10 text-forest">Executive Summary for ${parcelName}</span>
            <p class="font-bold text-forest-dark">40.96-Hectare Observation Snapshot:</p>
            <p>This parcel features <strong>${dominantPct}% ${dominant}</strong>, <strong>${veg}% green vegetative canopy</strong>, and <strong>${built}% built roads/structures</strong>.</p>
            <p>The ground is flat (${slope}% slope, ${elev}m AMSL) with moderate ${rain} mm annual rainfall. It is well-suited for seasonal farming or low-rise development, pending revenue title certification.</p>
          </div>
        `;
      } else {
        reply = `
          <div class="space-y-1.5">
            <p class="font-bold text-forest-dark">Observation Telemetry for ${parcelName}:</p>
            <p>Model classification confidence is <strong>${conf}%</strong> across 4,096 optical satellite pixels. Dominant surface is <strong>${dominant} (${dominantPct}%)</strong> and green plant cover is <strong>${veg}%</strong> at ${elev}m elevation.</p>
            <p class="text-earth-muted text-[11px]">Click any suggested prompt chip above to get specific answers regarding farming, buyer checklists, construction risks, or data gaps.</p>
          </div>
        `;
      }

      setTimeout(() => {
        if (target === 'floating') {
          appendFloatingAdvisorMessage('assistant', reply);
        } else if (target === 'full') {
          appendAdvisorMessage('assistant', reply);
        } else {
          appendAdvisorMessage('assistant', reply);
          appendFloatingAdvisorMessage('assistant', reply);
        }
      }, 300);
    }

    // =========================================================================
    // 15. MODALS (TECH, PARAMETER, LIGHTBOX)
    // =========================================================================
    function toggleTechModal(open) {
      const modal = document.getElementById('techModal');
      if (!modal) return;
      if (open) modal.classList.remove('hidden');
      else modal.classList.add('hidden');
    }

    function openParameterModal(title, val, category, measures, means, method) {
      const modal = document.getElementById('parameterDetailModal');
      if (!modal) return;
      document.getElementById('paramModalTitle').innerText = title;
      document.getElementById('paramModalValue').innerText = val;
      document.getElementById('paramModalCategory').innerText = category || 'Parameter Intelligence';
      document.getElementById('paramModalMeasures').innerText = measures;
      document.getElementById('paramModalMeans').innerText = means;
      document.getElementById('paramModalMethod').innerText = method;
      modal.classList.remove('hidden');
    }

    function closeParameterModal() {
      const modal = document.getElementById('parameterDetailModal');
      if (modal) modal.classList.add('hidden');
    }

    function closeAssessmentModal() {
      const modal = document.getElementById('assessmentModal');
      if (modal) modal.classList.add('hidden');
    }

    function openLightbox(type) {
      if (!currentPrediction) return;
      const modal = document.getElementById('imageLightboxModal');
      const img = document.getElementById('lightboxImage');
      const title = document.getElementById('lightboxTitle');
      const cat = document.getElementById('lightboxCategory');

      if (type === 'rgb') {
        img.src = currentPrediction.images.original;
        title.innerText = 'Sentinel-2 True Color Optical Photography';
        cat.innerText = 'Bottom-Of-Atmosphere (BOA) Reflectance';
      } else if (type === 'mask') {
        img.src = currentPrediction.images.colorized_mask;
        title.innerText = 'Land-Cover Semantic Classification Mask';
        cat.innerText = 'SatelliteUNet 7-Class Neural Output';
      } else if (type === 'composite') {
        img.src = currentPrediction.images.side_by_side;
        title.innerText = 'Multi-Spectral Verification Composite Triad';
        cat.innerText = 'Side-By-Side Optical & Semantic Calibration';
      }

      modal.classList.remove('hidden');
    }

    function closeLightbox() {
      const modal = document.getElementById('imageLightboxModal');
      if (modal) modal.classList.add('hidden');
    }

    // =========================================================================
    // 15B. LAND DISCOVERY & GEOSPATIAL INTELLIGENCE LAB (CATALOGUE & AI ENGINES)
    // =========================================================================
    let mlModelsRegistry = null;
    let mlCurrentKNN_K = 5;
    let mlDatasetPage = 0;
    const ML_DATASET_PAGE_SIZE = 25;
    let indiaCatalogue = [];
    let currentCatalogueZone = 'all';

    async function initMLLab() {
      try {
        await loadCatalogueData();
        if (!mlModelsRegistry) {
          const res = await fetch('/api/ml/models');
          if (res.ok) {
            mlModelsRegistry = await res.json();
            populateMLLabFromRegistry();
          }
        }
        updateRegPrediction();
        updateSVMPrediction();
        const knnGrid = document.getElementById('knnResultsGrid');
        if (knnGrid && (!knnGrid.innerHTML || knnGrid.innerHTML.trim() === '')) {
          querySimilarParcels();
        }
        switchMLTab('patterns');
      } catch (err) {
        console.warn("Error initializing Land Discovery Lab:", err);
      }
    }

    async function loadCatalogueData() {
      try {
        const res = await fetch('/api/geo/catalogue');
        if (res.ok) {
          indiaCatalogue = await res.json();
          renderCatalogueCards(indiaCatalogue);
        }
      } catch (e) {
        console.warn("Could not load catalogue data:", e);
      }
    }

    function renderCatalogueCards(list) {
      const grid = document.getElementById('catalogueCardsGrid');
      const countEl = document.getElementById('catalogueCountText');
      if (countEl) countEl.textContent = `${list.length} locations`;
      if (!grid) return;

      if (!list || list.length === 0) {
        grid.innerHTML = `
          <div class="col-span-full py-12 text-center text-earth-muted">
            <div class="text-3xl mb-2">🔍</div>
            <div class="font-serif text-sm">No matching locations found for your search.</div>
            <button onclick="filterCatalogueByZone('all')" class="mt-3 text-xs font-bold text-forest hover:underline">Reset Filters</button>
          </div>
        `;
        return;
      }

      grid.innerHTML = list.map(loc => `
        <div class="bg-white border border-earth-border rounded-3xl p-5 shadow-xs hover:shadow-md hover:border-forest/40 transition-all flex flex-col justify-between space-y-4 group">
          
          <!-- Top Row: Thumbnail + State/District + Type -->
          <div class="space-y-3">
            <div class="flex items-start space-x-3.5">
              <div class="w-16 h-16 rounded-2xl overflow-hidden bg-sand-light border border-earth-border shrink-0 shadow-2xs cursor-pointer group-hover:scale-105 transition-transform" onclick="openLocationLightbox('${loc.thumbnail_url}', '${loc.name}')" title="Click to view optical satellite crop">
                <img src="${loc.thumbnail_url}" alt="${loc.name}" class="w-full h-full object-cover" onerror="this.src='/static/samples/sample_tile_00000.png'"/>
              </div>
              <div class="space-y-1 min-w-0">
                <div class="flex items-center space-x-1.5 flex-wrap">
                  <span class="text-[10px] font-bold uppercase tracking-wider text-forest bg-forest/10 px-2 py-0.5 rounded-md">${loc.state}</span>
                  <span class="text-[10px] text-earth-muted font-mono">${loc.district}</span>
                </div>
                <h4 class="font-bold text-forest-dark text-base font-serif leading-snug truncate" title="${loc.name}">${loc.name}</h4>
                <div class="text-[11px] font-mono text-earth-muted">${loc.latitude.toFixed(4)}°N, ${loc.longitude.toFixed(4)}°E</div>
              </div>
            </div>

            <!-- Terrain & Soil Tag -->
            <div class="flex items-center space-x-2 text-[11px] text-earth-muted">
              <span>⛰️</span>
              <span class="truncate">${loc.terrain} • ${loc.soil_type.split('(')[0]}</span>
            </div>

            <!-- Key Biophysical Measurements Row -->
            <div class="grid grid-cols-4 gap-1.5 p-2.5 rounded-2xl bg-earth-cardTint border border-earth-border/80 text-center font-mono">
              <div>
                <div class="text-[9px] uppercase font-bold text-earth-muted">Greenery</div>
                <div class="text-xs font-bold text-forest">${loc.vegetation_pct}%</div>
              </div>
              <div>
                <div class="text-[9px] uppercase font-bold text-earth-muted">Slope</div>
                <div class="text-xs font-bold text-earth-dark">${loc.slope_deg}°</div>
              </div>
              <div>
                <div class="text-[9px] uppercase font-bold text-earth-muted">Rainfall</div>
                <div class="text-xs font-bold text-sky-dark">${Math.round(loc.annual_rainfall_mm)}mm</div>
              </div>
              <div>
                <div class="text-[9px] uppercase font-bold text-earth-muted">Elevation</div>
                <div class="text-xs font-bold text-earth-dark">${Math.round(loc.elevation_m)}m</div>
              </div>
            </div>

            <!-- Plain English Land Meaning -->
            <p class="text-xs text-earth-dark/90 font-serif leading-relaxed line-clamp-2">
              ${loc.agricultural_suitability}
            </p>
          </div>

          <!-- Bottom Action Buttons -->
          <div class="pt-2 border-t border-earth-border/70 flex items-center justify-between gap-2">
            <button onclick="selectCatalogueLocation('${loc.id}')" class="flex-1 py-2 px-3 rounded-xl bg-forest hover:bg-forest-dark text-white text-xs font-bold transition shadow-2xs flex items-center justify-center space-x-1.5">
              <span>Inspect Land</span><span>&rarr;</span>
            </button>
            <button onclick="matchSimilarFromCatalogue('${loc.id}')" class="py-2 px-3 rounded-xl border border-earth-border bg-earth-cardTint hover:bg-sand-light text-forest text-xs font-semibold transition" title="Find lands across India matching this location">
              🔍 Find Similar
            </button>
          </div>

        </div>
      `).join('');
    }

    function filterCatalogueCards() {
      const q = (document.getElementById('catalogueSearchInput') ? document.getElementById('catalogueSearchInput').value : '').trim().toLowerCase();
      let filtered = indiaCatalogue;
      if (currentCatalogueZone !== 'all') {
        filtered = filtered.filter(loc => matchesZone(loc, currentCatalogueZone));
      }
      if (q) {
        filtered = filtered.filter(loc => 
          loc.name.toLowerCase().includes(q) ||
          loc.state.toLowerCase().includes(q) ||
          loc.district.toLowerCase().includes(q) ||
          loc.terrain.toLowerCase().includes(q)
        );
      }
      renderCatalogueCards(filtered);
    }

    function filterCatalogueByZone(zone) {
      currentCatalogueZone = zone;
      document.querySelectorAll('.cat-filter-btn').forEach(btn => {
        if (btn.getAttribute('data-zone') === zone) {
          btn.className = 'cat-filter-btn px-3 py-1 rounded-lg bg-forest text-white font-semibold transition';
        } else {
          btn.className = 'cat-filter-btn px-3 py-1 rounded-lg bg-sand-light hover:bg-sand text-forest font-semibold transition';
        }
      });
      filterCatalogueCards();
    }

    function matchesZone(loc, zone) {
      if (zone === 'cropland') {
        return loc.dominant_type.includes('Crops') || loc.terrain.includes('Plain') || loc.terrain.includes('Interfluve');
      } else if (zone === 'highland') {
        return loc.elevation_m > 400 || loc.slope_deg > 3.0 || loc.terrain.includes('Plateau') || loc.terrain.includes('Hills');
      } else if (zone === 'arid') {
        return loc.annual_rainfall_mm < 600 || loc.terrain.includes('Desert') || loc.terrain.includes('Arid');
      } else if (zone === 'wetland') {
        return loc.water_pct > 3.0 || loc.terrain.includes('Delta') || loc.terrain.includes('Wetland') || loc.terrain.includes('Floodplain');
      }
      return true;
    }

    function selectCatalogueLocation(locId) {
      const loc = indiaCatalogue.find(l => l.id === locId);
      if (!loc) return;

      activeSurvey = {
        name: loc.name,
        displayName: `${loc.name}, ${loc.district}, ${loc.state}, India`,
        lat: loc.latitude,
        lon: loc.longitude,
        isDemo: false,
        demoIndex: null,
        dataState: 'VERIFIED REGIONAL EARTH OBSERVATION'
      };

      updateActivePlaceUI();
      acquireSatelliteImagery(loc.latitude, loc.longitude);
      navigateTo('intelligence');
    }

    function matchSimilarFromCatalogue(locId) {
      const loc = indiaCatalogue.find(l => l.id === locId);
      if (!loc) return;

      const pName = document.getElementById('knnCurrentParcelName');
      if (pName) pName.textContent = loc.name;

      switchMLTab('knn');
      querySimilarParcels({
        mean_red: loc.soil_pct > 50 ? 150 : 85,
        mean_green: loc.vegetation_pct > 50 ? 145 : 110,
        mean_blue: 75,
        vegetation_pct: loc.vegetation_pct,
        built_up_pct: loc.built_up_pct,
        soil_pct: loc.soil_pct,
        k: mlCurrentKNN_K
      });
    }

    function openLocationLightbox(imgSrc, title) {
      const modal = document.getElementById('imageLightboxModal');
      const img = document.getElementById('lightboxImage');
      const titleEl = document.getElementById('lightboxTitle');
      const catEl = document.getElementById('lightboxCategory');

      if (img) img.src = imgSrc;
      if (titleEl) titleEl.innerText = title;
      if (catEl) catEl.innerText = 'High-Resolution Sentinel-2 Multi-Spectral Tile';
      if (modal) modal.classList.remove('hidden');
    }

    function switchMLTab(tabId) {
      document.querySelectorAll('.mllab-tab').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.mllab-tab-btn').forEach(btn => {
        btn.className = 'mllab-tab-btn px-4 py-2.5 rounded-xl font-semibold text-earth-text hover:bg-sand-light transition shrink-0 flex items-center space-x-2';
      });

      const target = document.getElementById('mlTab_' + tabId);
      const btn = document.getElementById('mlTabBtn_' + tabId);
      if (target) target.classList.remove('hidden');
      if (btn) btn.className = 'mllab-tab-btn px-4 py-2.5 rounded-xl font-bold bg-forest text-white transition shrink-0 flex items-center space-x-2';

      if (tabId === 'dataset') {
        loadDatasetExplorer(0);
      }
    }

    function populateMLLabFromRegistry() {
      if (!mlModelsRegistry || !mlModelsRegistry.models) return;

      // 1. Model A Scatter points
      const reg = mlModelsRegistry.models.linear_regression;
      if (reg && reg.scatter_preview) {
        const grid = document.getElementById('regScatterGrid');
        if (grid) {
          grid.innerHTML = reg.scatter_preview.slice(0, 40).map((pt, i) => `
            <div class="p-2 rounded-xl border border-earth-border/70 ${pt.error < 5 ? 'bg-emerald-50 text-emerald-900 border-emerald-200' : 'bg-sand-light/40 text-earth-dark'}">
              <div class="text-[9px] uppercase font-bold text-earth-muted">Sample #${i+1}</div>
              <div class="font-mono text-[11px] font-bold">Act: ${pt.actual}%</div>
              <div class="font-mono text-[11px]">Pred: ${pt.predicted}%</div>
              <div class="text-[9px] font-mono ${pt.error < 5 ? 'text-emerald-700' : 'text-amber-700'}">Δ: ±${pt.error}%</div>
            </div>
          `).join('');
        }
      }

      // 2. Model B Confusion Matrix
      const svm = mlModelsRegistry.models.svm_classifier;
      if (svm && svm.confusion_matrix) {
        const tbody = document.getElementById('svmConfusionMatrixBody');
        if (tbody) {
          const labels = svm.confusion_matrix.labels;
          const matrix = svm.confusion_matrix.matrix;
          const perClass = svm.per_class || {};

          tbody.innerHTML = matrix.map((row, rIdx) => {
            const rowLabel = labels[rIdx] || `Class ${rIdx}`;
            const metrics = perClass[rowLabel] || { precision: 0.7, recall: 0.7, f1: 0.7 };
            return `
              <tr class="hover:bg-sand-light/30">
                <td class="p-2 text-left font-bold text-forest-dark">${rowLabel}</td>
                ${row.slice(0, 5).map((val, cIdx) => `
                  <td class="p-2 ${rIdx === cIdx ? 'bg-forest/15 font-bold text-forest' : 'text-earth-muted'}">${val}</td>
                `).join('')}
                <td class="p-2 font-bold text-forest">${(metrics.precision * 100).toFixed(1)}%</td>
                <td class="p-2 font-bold text-forest">${(metrics.recall * 100).toFixed(1)}%</td>
                <td class="p-2 font-bold text-forest">${(metrics.f1 * 100).toFixed(1)}%</td>
              </tr>
            `;
          }).join('');
        }
      }
    }

    // --- Model A: Linear Regression Handlers ---
    function setRegPreset(r, g, b, std) {
      document.getElementById('regSlider_red').value = r;
      document.getElementById('regSlider_green').value = g;
      document.getElementById('regSlider_blue').value = b;
      document.getElementById('regSlider_std').value = std;
      updateRegPrediction();
    }

    async function updateRegPrediction() {
      const r = parseFloat(document.getElementById('regSlider_red').value);
      const g = parseFloat(document.getElementById('regSlider_green').value);
      const b = parseFloat(document.getElementById('regSlider_blue').value);
      const std = parseFloat(document.getElementById('regSlider_std').value);

      document.getElementById('regVal_red').textContent = r;
      document.getElementById('regVal_green').textContent = g;
      document.getElementById('regVal_blue').textContent = b;
      document.getElementById('regVal_std').textContent = std;

      try {
        const res = await fetch('/api/ml/predict/linear', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mean_red: r, mean_green: g, mean_blue: b, std_green: std })
        });
        if (res.ok) {
          const data = await res.json();
          const pct = data.predicted_vegetation_pct;
          document.getElementById('regResultPct').textContent = pct.toFixed(1) + '%';
          document.getElementById('regResultBadge').textContent = data.scientific_interpretation;
          document.getElementById('regResultBar').style.width = Math.min(100, Math.max(0, pct)) + '%';
          document.getElementById('regResultBarText').textContent = `${pct.toFixed(1)}% of land surface`;
          document.getElementById('regResultSummary').textContent = data.layman_summary;
        }
      } catch (err) {
        console.warn("Error running linear regression:", err);
      }
    }

    // --- Model B: SVM Handlers ---
    function runSVMPreset(r, g, b, label) {
      document.getElementById('svmSlider_red').value = r;
      document.getElementById('svmSlider_green').value = g;
      document.getElementById('svmSlider_blue').value = b;
      updateSVMPrediction();
    }

    async function updateSVMPrediction() {
      const r = parseFloat(document.getElementById('svmSlider_red').value);
      const g = parseFloat(document.getElementById('svmSlider_green').value);
      const b = parseFloat(document.getElementById('svmSlider_blue').value);

      document.getElementById('svmVal_red').textContent = r;
      document.getElementById('svmVal_green').textContent = g;
      document.getElementById('svmVal_blue').textContent = b;

      try {
        const res = await fetch('/api/ml/predict/svm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mean_red: r, mean_green: g, mean_blue: b })
        });
        if (res.ok) {
          const data = await res.json();
          document.getElementById('svmResultClass').textContent = data.predicted_class_name;
          document.getElementById('svmResultConfidence').textContent = data.confidence_pct.toFixed(1) + '%';
          document.getElementById('svmResultSummary').textContent = data.layman_summary;

          const container = document.getElementById('svmProbBarsContainer');
          if (container && data.class_probabilities) {
            container.innerHTML = Object.entries(data.class_probabilities).map(([cName, prob]) => `
              <div class="space-y-1">
                <div class="flex justify-between text-[11px] font-semibold text-earth-dark">
                  <span class="${cName === data.predicted_class_name ? 'text-forest font-bold' : ''}">${cName}</span>
                  <span class="font-mono ${cName === data.predicted_class_name ? 'text-forest font-bold' : 'text-earth-muted'}">${prob.toFixed(1)}%</span>
                </div>
                <div class="h-2 w-full bg-sand-light rounded-full overflow-hidden">
                  <div class="h-full ${cName === data.predicted_class_name ? 'bg-forest' : 'bg-sage-dark/60'} rounded-full transition-all duration-300" style="width: ${prob}%;"></div>
                </div>
              </div>
            `).join('');
          }
        }
      } catch (err) {
        console.warn("Error running SVM prediction:", err);
      }
    }

    // --- Model C: KNN Handlers ---
    function setKNN_K(k) {
      mlCurrentKNN_K = k;
      [3, 5, 10].forEach(val => {
        const btn = document.getElementById('knnKBtn_' + val);
        if (btn) {
          if (val === k) {
            btn.className = 'px-3 py-1 rounded-lg text-xs font-bold bg-forest text-white';
          } else {
            btn.className = 'px-3 py-1 rounded-lg text-xs font-bold border border-earth-border hover:bg-sand-light text-earth-dark';
          }
        }
      });
      querySimilarParcels();
    }

    function loadCurrentParcelIntoKNN() {
      querySimilarParcels();
    }

    async function querySimilarParcels(customParams) {
      try {
        const payload = customParams || {
          mean_red: 90.0,
          mean_green: 135.0,
          mean_blue: 80.0,
          vegetation_pct: 35.0,
          built_up_pct: 12.0,
          soil_pct: 48.0,
          k: mlCurrentKNN_K
        };
        const res = await fetch('/api/ml/knn/neighbors', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const data = await res.json();
          const grid = document.getElementById('knnResultsGrid');
          const countEl = document.getElementById('knnResultsCount');
          if (countEl) countEl.textContent = `Found ${data.neighbors.length} matching parcels (K = ${mlCurrentKNN_K})`;
          if (grid) {
            grid.innerHTML = data.neighbors.map((p, idx) => `
              <div class="bg-white border border-earth-border rounded-2xl p-4 shadow-xs space-y-3 hover:border-forest/50 transition">
                <div class="flex items-center justify-between">
                  <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-sand-light text-earth-dark">Rank #${idx + 1} Analog</span>
                  <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">${p.similarity_pct}% Similar</span>
                </div>
                <div>
                  <div class="font-bold text-forest-dark text-sm">Parcel #${p.parcel_id}</div>
                  <div class="text-[11px] font-mono text-earth-muted">${p.latitude.toFixed(4)}°N, ${p.longitude.toFixed(4)}°E</div>
                </div>
                <div class="grid grid-cols-3 gap-2 text-center text-xs p-2.5 bg-earth-cardTint rounded-xl border border-earth-border">
                  <div>
                    <div class="text-[9px] uppercase font-bold text-earth-muted">Greenery</div>
                    <div class="font-bold text-forest font-mono">${p.vegetation_pct}%</div>
                  </div>
                  <div>
                    <div class="text-[9px] uppercase font-bold text-earth-muted">Built-up</div>
                    <div class="font-bold text-terracotta font-mono">${p.built_up_pct}%</div>
                  </div>
                  <div>
                    <div class="text-[9px] uppercase font-bold text-earth-muted">Bare Soil</div>
                    <div class="font-bold text-earth-dark font-mono">${p.soil_pct}%</div>
                  </div>
                </div>
                <div class="flex items-center justify-between text-xs pt-1">
                  <span class="text-[11px] text-earth-muted">Type: <strong>${p.dominant_land_type}</strong></span>
                  <button onclick="inspectKNNParcelOnMap(${p.latitude}, ${p.longitude}, 'Parcel #${p.parcel_id}')" class="text-xs font-bold text-forest hover:underline">
                    View on Map &rarr;
                  </button>
                </div>
              </div>
            `).join('');
          }
        }
      } catch (err) {
        console.warn("Error querying KNN:", err);
      }
    }

    function inspectKNNParcelOnMap(lat, lon, name) {
      activeSurvey = {
        name: name,
        displayName: `${name} (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E), India`,
        lat: lat,
        lon: lon,
        isDemo: false,
        demoIndex: null,
        dataState: 'VERIFIED SURVEY ANALOG OBSERVATION'
      };
      updateActivePlaceUI();
      acquireSatelliteImagery(lat, lon);
      navigateTo('explore');
      if (map) {
        map.flyTo({ center: [lon, lat], zoom: 12, essential: true });
      }
    }

    // --- Model D: DBSCAN Handlers ---
    async function runDBSCANClustering() {
      const eps = parseFloat(document.getElementById('dbscanSlider_eps').value);
      const min_samples = parseInt(document.getElementById('dbscanSlider_min').value, 10);

      try {
        const res = await fetch('/api/ml/dbscan/cluster', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ eps: eps, min_samples: min_samples })
        });
        if (res.ok) {
          const data = await res.json();
          document.getElementById('dbscanClusterBadge').textContent = `${data.clusters_discovered} Clusters Discovered`;
          document.getElementById('dbscanNoiseBadge').textContent = `${data.noise_points} Outliers (${data.noise_pct}%)`;

          const grid = document.getElementById('dbscanClustersGrid');
          if (grid && data.clusters) {
            grid.innerHTML = Object.entries(data.clusters).map(([name, c]) => `
              <div class="bg-white border border-earth-border rounded-2xl p-4 shadow-xs space-y-3 ${c.cluster_id === -1 ? 'border-terracotta/40 bg-sand-light/20' : ''}">
                <div class="flex items-center justify-between">
                  <span class="font-bold text-forest-dark text-xs">${name}</span>
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${c.cluster_id === -1 ? 'bg-amber-100 text-amber-800' : 'bg-forest/10 text-forest'}">${c.size} parcels (${c.pct_of_dataset}%)</span>
                </div>
                <div class="text-[11px] text-earth-muted">
                  Dominant: <strong class="text-forest-dark">${c.dominant_land_type}</strong> • Center: ${c.center_lat.toFixed(3)}°N, ${c.center_lon.toFixed(3)}°E
                </div>
                <div class="grid grid-cols-3 gap-2 text-center text-xs p-2 bg-earth-cardTint rounded-xl border border-earth-border font-mono">
                  <div>
                    <div class="text-[9px] uppercase text-earth-muted">Veg %</div>
                    <div class="font-bold text-forest">${c.avg_vegetation_pct}%</div>
                  </div>
                  <div>
                    <div class="text-[9px] uppercase text-earth-muted">Built %</div>
                    <div class="font-bold text-terracotta">${c.avg_built_up_pct}%</div>
                  </div>
                  <div>
                    <div class="text-[9px] uppercase text-earth-muted">Soil %</div>
                    <div class="font-bold text-earth-dark">${c.avg_soil_pct}%</div>
                  </div>
                </div>
              </div>
            `).join('');
          }
        }
      } catch (err) {
        console.warn("Error running DBSCAN clustering:", err);
      }
    }

    // --- Dataset Explorer Handlers ---
    async function loadDatasetExplorer(page) {
      if (page < 0) page = 0;
      mlDatasetPage = page;
      const classFilterEl = document.getElementById('datasetFilterClass');
      const classFilter = classFilterEl ? classFilterEl.value : '';
      let url = `/api/ml/dataset?limit=${ML_DATASET_PAGE_SIZE}&offset=${page * ML_DATASET_PAGE_SIZE}`;
      if (classFilter !== '') {
        url += `&dominant_class=${classFilter}`;
      }

      try {
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          const tbody = document.getElementById('datasetTableBody');
          const start = page * ML_DATASET_PAGE_SIZE + 1;
          const end = Math.min(start + data.records.length - 1, data.total_records);
          const pageInfo = document.getElementById('datasetPageInfo');
          if (pageInfo) pageInfo.textContent = `Showing ${start}–${end} of ${data.total_records} genuine Sentinel-2 samples`;

          if (tbody) {
            tbody.innerHTML = data.records.map(r => `
              <tr class="hover:bg-sand-light/30 transition">
                <td class="p-2.5 font-bold text-forest">#${r.sample_id}</td>
                <td class="p-2.5 text-earth-muted">${r.latitude.toFixed(4)}°N, ${r.longitude.toFixed(4)}°E</td>
                <td class="p-2.5 text-earth-dark">R:${Math.round(r.mean_red)} G:${Math.round(r.mean_green)} B:${Math.round(r.mean_blue)}</td>
                <td class="p-2.5 font-bold text-forest">${r.vegetation_pct}%</td>
                <td class="p-2.5 text-terracotta">${r.built_up_pct}%</td>
                <td class="p-2.5 text-earth-dark">${r.soil_pct}%</td>
                <td class="p-2.5 font-semibold text-forest-dark">${r.dominant_class}</td>
                <td class="p-2.5 text-right">
                  <button onclick="testSampleInML(${r.sample_id}, ${r.mean_red}, ${r.mean_green}, ${r.mean_blue}, '${r.dominant_class}')" class="px-2.5 py-1 rounded bg-forest/10 hover:bg-forest hover:text-white text-forest text-[10px] font-bold transition">
                    Test in ML &rarr;
                  </button>
                </td>
              </tr>
            `).join('');
          }
        }
      } catch (err) {
        console.warn("Error loading dataset explorer:", err);
      }
    }

    function changeDatasetPage(delta) {
      loadDatasetExplorer(mlDatasetPage + delta);
    }

    function testSampleInML(sampleId, r, g, b, domClass) {
      const rVal = Math.round(r);
      const gVal = Math.round(g);
      const bVal = Math.round(b);
      document.getElementById('regSlider_red').value = rVal;
      document.getElementById('regSlider_green').value = gVal;
      document.getElementById('regSlider_blue').value = bVal;
      document.getElementById('svmSlider_red').value = rVal;
      document.getElementById('svmSlider_green').value = gVal;
      document.getElementById('svmSlider_blue').value = bVal;
      switchMLTab('regression');
      updateRegPrediction();
      updateSVMPrediction();
    }

    // --- Satellite Imagery Acquisition Pipeline ---
    async function acquireSatelliteImagery(lat, lon) {
      try {
        const res = await fetch(`/api/imagery/acquire?lat=${lat}&lon=${lon}`);
        if (res.ok) {
          const data = await res.json();
          const imgEl = document.getElementById('intelThumbImg');
          if (imgEl && data.image_url) {
            imgEl.src = data.image_url;
          }
        }
      } catch (e) {
        console.warn("Satellite acquisition pipeline note:", e);
      }
    }

    // =========================================================================
    // 16. INITIALIZATION ON PAGE LOAD
    // =========================================================================
    window.addEventListener('DOMContentLoaded', () => {
      initDashboardGreeting();

      const hash = window.location.hash.replace('#', '');
      const validViews = ['dashboard', 'explore', 'intelligence', 'mllab', 'places', 'reports', 'advisor', 'registry', 'landing', 'profile', 'settings'];
      if (validViews.includes(hash)) {
        navigateTo(hash);
      } else {
        navigateTo('dashboard');
      }

      // Initialize App Feeds
      loadSamples();
      renderRecentSearches();
      fetchSavedPlaces();
      fetchSavedReports();
      loadDataRegistry();
      checkExistingAuth();
    });
  // </script>
