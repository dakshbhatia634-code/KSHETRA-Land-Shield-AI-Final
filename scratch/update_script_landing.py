"""
Update scratch/section_script.js with all cinematic landing and dynamic location helpers.
"""

from pathlib import Path

def update_script():
    script_path = Path("scratch/section_script.js")
    content = script_path.read_text(encoding="utf-8")

    # 1. Update navigateTo layout logic
    old_nav_start = """    function navigateTo(viewName) {
      if (!viewName) viewName = 'dashboard';
      currentView = viewName;

      // 1. Hide all views"""

    new_nav_start = """    function navigateTo(viewName) {
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

      // 1. Hide all views"""

    if old_nav_start in content:
        content = content.replace(old_nav_start, new_nav_start)
        print("Updated navigateTo layout logic.")

    # 2. Add Helper Functions before initDashMap
    marker_anchor = "function initDashMap() {"
    helper_code = """
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
      const coordsStr = prompt("Enter Indian Coordinates (Latitude, Longitude):\\nExample: 28.6139, 77.2090");
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

    function initDashMap() {"""

    if marker_anchor in content and "function setDashMapLayer" not in content:
        content = content.replace(marker_anchor, helper_code)
        print("Added helper functions.")

    # 3. Update initDashMap default to dark layer
    old_dash_layers = """layers: [
            { id: 'dash-satellite-layer', type: 'raster', source: 'dash-satellite', minzoom: 0, maxzoom: 19 },
            { id: 'dash-dark-layer', type: 'raster', source: 'dash-dark', minzoom: 0, maxzoom: 19, layout: { visibility: 'none' } },
            { id: 'dash-osm-layer', type: 'raster', source: 'dash-osm', minzoom: 0, maxzoom: 19, layout: { visibility: 'none' } }
          ]"""

    new_dash_layers = """layers: [
            { id: 'dash-satellite-layer', type: 'raster', source: 'dash-satellite', minzoom: 0, maxzoom: 19, layout: { visibility: 'none' } },
            { id: 'dash-dark-layer', type: 'raster', source: 'dash-dark', minzoom: 0, maxzoom: 19, layout: { visibility: 'visible' } },
            { id: 'dash-osm-layer', type: 'raster', source: 'dash-osm', minzoom: 0, maxzoom: 19, layout: { visibility: 'none' } }
          ]"""

    if old_dash_layers in content:
        content = content.replace(old_dash_layers, new_dash_layers)
        print("Set dashMap default layer to dark.")

    # 4. In dashMap click handler, update HUD coordinates
    old_dash_click = """dashMap.on('click', (e) => {
        handleMapClick(e.lngLat.lat, e.lngLat.lng);
      });"""

    new_dash_click = """dashMap.on('click', (e) => {
        const lat = e.lngLat.lat;
        const lon = e.lngLat.lng;
        const hudCoords = document.getElementById('dashHudCoords');
        const hudPlace = document.getElementById('dashHudPlace');
        if (hudCoords) hudCoords.innerText = `${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E`;
        if (hudPlace) hudPlace.innerText = `Survey Point (${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E)`;
        handleMapClick(lat, lon);
      });"""

    if old_dash_click in content:
        content = content.replace(old_dash_click, new_dash_click)
        print("Updated dashMap click handler.")

    script_path.write_text(content, encoding="utf-8")
    print("Successfully updated section_script.js")

if __name__ == "__main__":
    update_script()
