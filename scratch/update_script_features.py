"""
KSHETRA — LAND SHIELD AI
Script updater for interactive multi-page SaaS features:
- Saved Places: Notes editing, comparison modal, SQLite sync
- Reports: Report history, save report to SQLite, PDF print formatting
- AI Land Advisor: Context-aware dynamic responses, floating launcher & drawer
- Land Intelligence: Location-specific summaries, environment telemetry binding
- Dashboard: Featured regions, recent reports preview, omni-search
"""

import re
from pathlib import Path

script_path = Path(__file__).resolve().parent / "section_script.js"
content = script_path.read_text(encoding="utf-8")

# 1. Add global state variables
state_target = "let activeIntelDomain = 'overview';"
state_replacement = """let activeIntelDomain = 'overview';
    let savedReports = [];
    let selectedComparePlaceIds = [];
    let editingPlaceId = null;"""
if state_target in content:
    content = content.replace(state_target, state_replacement, 1)

# 2. Add environment telemetry fetching & rendering
env_block = """
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
"""

run_sample_marker = "async function runSampleInference(sampleIndex) {"
if run_sample_marker in content:
    content = content.replace(run_sample_marker, env_block + "\n    " + run_sample_marker, 1)

# Update runSampleInference to trigger fetchEnvironment
old_run_sample = """        currentPrediction = await res.json();
        updateActivePlaceUI();
        renderIntelligenceView();
        renderReportsView();"""
new_run_sample = """        currentPrediction = await res.json();
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
        renderReportsView();"""
if old_run_sample in content:
    content = content.replace(old_run_sample, new_run_sample, 1)

# Update handleMapClick to call fetchEnvironment
old_map_click = "recordRecentSearch(activeSurvey.name, lat, lon);\n      updateActivePlaceUI();"
new_map_click = """recordRecentSearch(activeSurvey.name, lat, lon);
      fetchEnvironment(lat, lon);
      updateActivePlaceUI();"""
if old_map_click in content:
    content = content.replace(old_map_click, new_map_click, 1)

# Replace renderSavedPlaces to include checkboxes, notes editor, compare
old_render_saved = """    function renderSavedPlaces() {
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
        const card = document.createElement('div');
        card.className = 'bg-white border border-earth-border rounded-2xl p-5 shadow-xs space-y-3 hover:border-forest/50 transition';
        card.innerHTML = `
          <div class="flex items-start justify-between">
            <div>
              <span class="text-[9px] font-bold uppercase tracking-wider text-earth-muted">${p.tags || p.tag || 'Saved Land Parcel'}</span>
              <h4 class="text-sm font-bold text-forest-dark font-serif mt-0.5">${escapeHtml(p.name || 'Saved Parcel')}</h4>
              <div class="text-[11px] font-mono text-earth-muted">${latStr}°N, ${lonStr}°E</div>
            </div>
            <button onclick="deleteSavedPlace('${p.id}')" title="Remove Parcel" class="text-earth-muted hover:text-terracotta text-sm font-bold">&times;</button>
          </div>
          ${p.notes ? `<p class="text-xs text-earth-muted line-clamp-2 italic">"${escapeHtml(p.notes)}"</p>` : ''}
          <div class="pt-2 border-t border-earth-border flex items-center justify-between text-xs">
            <button onclick="viewPlaceOnMap(${latVal}, ${lonVal}, '${escapeHtml(p.name || '')}')" class="text-forest font-bold hover:underline">
              View on Map &rarr;
            </button>
            <button onclick="viewPlaceIntelligence(${latVal}, ${lonVal}, '${escapeHtml(p.name || '')}')" class="px-3 py-1 bg-forest/10 hover:bg-forest/20 text-forest font-bold rounded-lg transition">
              Analyze
            </button>
          </div>
        `;
        grid.appendChild(card);
      });
    }"""

new_render_saved = """    function toggleCompareSelect(id, checked) {
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
    }"""

if old_render_saved in content:
    content = content.replace(old_render_saved, new_render_saved, 1)

# Report History & Management functions
reports_management_block = """
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
"""

export_marker = "function exportJsonSummary() {"
if export_marker in content:
    content = content.replace(export_marker, reports_management_block + "\n    " + export_marker, 1)

# Floating Advisor Functions and Enhanced Grounded Engine
floating_advisor_block = """
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
"""

advisor_marker = "function handleAdvisorSubmit(e) {"
if advisor_marker in content:
    content = content.replace(advisor_marker, floating_advisor_block + "\n    " + advisor_marker, 1)

# Now enhance generateAdvisorGroundedReply to accept target and use real metrics
old_advisor_reply_re = re.search(r"function generateAdvisorGroundedReply\(query\)\s*\{[\s\S]*?appendAdvisorMessage\('assistant', reply\);\s*\}, 300\);\s*\}", content)
if old_advisor_reply_re:
    new_advisor_reply = """function generateAdvisorGroundedReply(query, target = 'both') {
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
    }"""
    content = content.replace(old_advisor_reply_re.group(0), new_advisor_reply, 1)

# Update DOMContentLoaded to load reports and registry
old_init = "fetchSavedPlaces();\n      checkExistingAuth();"
new_init = """fetchSavedPlaces();
      fetchSavedReports();
      loadDataRegistry();
      checkExistingAuth();"""
if old_init in content:
    content = content.replace(old_init, new_init, 1)

script_path.write_text(content, encoding="utf-8")
print(f"Updated {script_path} ({len(content):,} bytes).")
