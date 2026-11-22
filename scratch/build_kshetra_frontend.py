"""
KSHETRA — LAND SHIELD AI
Frontend Upgrade Script: Injects Brand Identity, Premium Editorial Hero, Real India Geocoding,
Data State System, My Places Persistence, Data Registry, and Auth/Profile Modals.
"""

import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Title & Fonts in <head>
old_title_snippet = '<title>Land Shield AI — Intelligent Earth Observation & Land Intelligence Platform</title>'
new_title_snippet = '''<title>KSHETRA — LAND SHIELD AI | Verifying Titles. Securing Boundaries.</title>

  <!-- Google Fonts: Cormorant Garamond for KSHETRA display title + Plus Jakarta Sans + JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,600;1,700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">'''

if old_title_snippet in html:
    html = html.replace(old_title_snippet, new_title_snippet, 1)

# Update Tailwind config to include serif Cormorant Garamond
old_font_config = "fontFamily: {\n            sans: ['\"Plus Jakarta Sans\"', 'system-ui', '-apple-system', 'sans-serif'],\n            mono: ['\"JetBrains Mono\"', 'monospace'],\n          },"
new_font_config = "fontFamily: {\n            serif: ['\"Cormorant Garamond\"', 'Georgia', 'serif'],\n            sans: ['\"Plus Jakarta Sans\"', 'system-ui', '-apple-system', 'sans-serif'],\n            mono: ['\"JetBrains Mono\"', 'monospace'],\n          },"
if old_font_config in html:
    html = html.replace(old_font_config, new_font_config, 1)

# 2. Update Header with KSHETRA branding and top navigation links
header_old_pattern = re.compile(r'<header class="bg-white/95 backdrop-blur-md border-b border-earth-border sticky top-0 z-40 shadow-xs">[\s\S]*?</header>')

new_header = '''  <!-- ========================================================================= -->
  <!-- 1. KSHETRA BRANDING & PRIMARY NAVIGATION HEADER                           -->
  <!-- ========================================================================= -->
  <header class="bg-[#FBF9F5]/95 backdrop-blur-md border-b border-earth-border sticky top-0 z-40 shadow-xs">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 h-20 flex items-center justify-between">
      
      <!-- Brand Logo, KSHETRA Title & Commercial Tagline -->
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
      </div>

      <!-- Main Navigation Menu -->
      <nav class="hidden xl:flex items-center space-x-1 text-xs font-semibold text-earth-dark">
        <a href="#heroSection" class="px-3 py-1.5 rounded-lg hover:bg-sand-light transition text-forest font-bold">Dashboard</a>
        <a href="#mapSection" class="px-3 py-1.5 rounded-lg hover:bg-sand-light transition">Explore India</a>
        <a href="#tabPanel_overview" class="px-3 py-1.5 rounded-lg hover:bg-sand-light transition">Land Intelligence</a>
        <button onclick="openSavedPlacesDrawer()" class="px-3 py-1.5 rounded-lg hover:bg-sand-light transition flex items-center space-x-1">
          <span>My Places</span>
          <span id="navSavedPlacesCount" class="w-4 h-4 rounded-full bg-sand text-[10px] font-bold text-forest flex items-center justify-center">0</span>
        </button>
        <button onclick="openRegistryModal()" class="px-3 py-1.5 rounded-lg hover:bg-sand-light transition">Data Registry</button>
        <button onclick="openReportModal()" class="px-3 py-1.5 rounded-lg hover:bg-sand-light transition">Reports</button>
        <button onclick="toggleChatDrawer(true)" class="px-3 py-1.5 rounded-lg hover:bg-sand-light transition text-forest flex items-center space-x-1">
          <span class="w-2 h-2 rounded-full bg-forest animate-pulse"></span>
          <span>AI Advisor</span>
        </button>
      </nav>

      <!-- Action Items & Diagnostic Access -->
      <div class="flex items-center space-x-2.5">
        <!-- My Places Quick Trigger -->
        <button onclick="openSavedPlacesDrawer()" title="View Saved Places" class="p-2 rounded-xl border border-earth-border bg-white hover:bg-sand-light text-forest transition shadow-2xs">
          <svg class="w-4 h-4 text-forest" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
          </svg>
        </button>

        <!-- Technical / System Diagnostics -->
        <button onclick="toggleTechModal(true)" title="System & CUDA Diagnostics" class="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl border border-earth-border bg-white hover:bg-sand-light text-xs font-semibold text-forest transition shadow-2xs">
          <svg class="w-3.5 h-3.5 text-sage-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/>
          </svg>
          <span class="hidden md:inline">Diagnostics</span>
        </button>

        <!-- Profile & Account Settings Button -->
        <button onclick="openAuthModal()" class="inline-flex items-center space-x-2 px-3 py-2 rounded-xl border border-earth-border bg-white hover:bg-sand-light text-xs font-semibold text-earth-dark transition shadow-2xs">
          <div class="w-5 h-5 rounded-full bg-forest text-white text-[10px] font-bold flex items-center justify-center">K</div>
          <span class="hidden sm:inline">Profile</span>
        </button>

        <!-- Official Report Action -->
        <button onclick="openReportModal()" class="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-forest hover:bg-forest-dark text-white text-xs font-bold rounded-xl transition shadow-xs hover:shadow-md">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <span class="hidden sm:inline">Land Dossier</span>
          <span class="sm:hidden">Report</span>
        </button>
      </div>
    </div>
  </header>'''

html = header_old_pattern.sub(new_header, html)

# 3. Insert Editorial Hero Section & India Location Search before LOCATION HERO & MAP SECTION
hero_section_code = '''    <!-- ========================================================================= -->
    <!-- 2. EDITORIAL HERO & INDIA-WIDE SEARCH BAR                                 -->
    <!-- ========================================================================= -->
    <section id="heroSection" class="relative bg-gradient-to-b from-[#FAF8F3] via-white to-[#F6F3E9]/40 border border-earth-border rounded-3xl p-6 sm:p-10 shadow-sm overflow-hidden">
      <!-- Subtle Decorative Map Grid Backdrop -->
      <div class="absolute inset-0 opacity-[0.03] pointer-events-none bg-[radial-gradient(#2B4333_1px,transparent_1px)] [background-size:16px_16px]"></div>
      
      <div class="relative max-w-4xl mx-auto text-center space-y-4">
        <!-- Brand Badges -->
        <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sand-light border border-sand-dark/40 shadow-2xs">
          <span class="w-2 h-2 rounded-full bg-forest animate-pulse"></span>
          <span class="text-[11px] font-bold uppercase tracking-wider text-forest-dark font-mono">Autonomous Geospatial Intelligence</span>
          <span class="text-[10px] text-earth-muted">•</span>
          <span class="text-[11px] font-semibold text-earth-muted">Republic of India</span>
        </div>

        <!-- Display Heading -->
        <div class="space-y-1">
          <h2 class="text-3xl sm:text-5xl font-extrabold tracking-tight text-forest-dark font-serif">
            KSHETRA
          </h2>
          <div class="text-sm sm:text-base font-extrabold tracking-widest text-earth-dark uppercase">
            Land Shield AI
          </div>
          <p class="text-base sm:text-lg font-serif italic text-forest-dark/90 pt-0.5">
            Verifying Titles. Securing Boundaries.
          </p>
          <p class="text-xs sm:text-sm text-earth-muted max-w-xl mx-auto pt-1">
            Understand the land. Make informed decisions. Real-time satellite land-cover segmentation, climate telemetry, and terrain screening across India.
          </p>
        </div>

        <!-- Prominent India Location Search Input -->
        <div class="pt-2 max-w-2xl mx-auto relative text-left">
          <div class="relative flex items-center">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-earth-muted">
              <svg class="w-5 h-5 text-forest" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
            <input 
              id="indiaLocationSearchInput" 
              type="text" 
              placeholder="Search a city, village, district, location or coordinates (e.g. Meerut, Faridabad, Bengaluru, 28.40, 77.35)..." 
              class="w-full pl-11 pr-24 py-3.5 bg-white border-2 border-earth-border focus:border-forest rounded-2xl text-xs sm:text-sm text-earth-dark placeholder-earth-muted/70 shadow-sm focus:outline-none focus:ring-4 focus:ring-forest/10 transition"
              oninput="handleSearchInputChange(this.value)"
              onkeydown="handleSearchInputKey(event)"
              autocomplete="off"
            />
            <button 
              onclick="executeSearch()" 
              class="absolute right-2 px-4 py-2 bg-forest hover:bg-forest-dark text-white rounded-xl text-xs font-bold transition shadow-xs hover:shadow">
              Search
            </button>
          </div>

          <!-- Autocomplete Dropdown Container -->
          <div id="searchSuggestionsBox" class="hidden absolute left-0 right-0 top-full mt-2 bg-white border border-earth-border rounded-2xl shadow-xl z-50 overflow-hidden divide-y divide-earth-border/60">
            <!-- Dynamically populated suggestions -->
          </div>
        </div>

        <!-- Quick Action Shortcuts -->
        <div class="flex flex-wrap items-center justify-center gap-2 pt-2 text-xs">
          <span class="text-earth-muted font-medium">Quick Exploration:</span>
          <button onclick="quickSelectCity('New Delhi')" class="px-2.5 py-1 rounded-lg bg-white border border-earth-border hover:bg-sand-light text-earth-dark font-medium transition shadow-2xs">Delhi NCR</button>
          <button onclick="quickSelectCity('Meerut')" class="px-2.5 py-1 rounded-lg bg-white border border-earth-border hover:bg-sand-light text-earth-dark font-medium transition shadow-2xs">Meerut</button>
          <button onclick="quickSelectCity('Bengaluru')" class="px-2.5 py-1 rounded-lg bg-white border border-earth-border hover:bg-sand-light text-earth-dark font-medium transition shadow-2xs">Bengaluru</button>
          <button onclick="quickSelectCity('Mumbai')" class="px-2.5 py-1 rounded-lg bg-white border border-earth-border hover:bg-sand-light text-earth-dark font-medium transition shadow-2xs">Mumbai</button>
          <button onclick="quickSelectCity('Jaipur')" class="px-2.5 py-1 rounded-lg bg-white border border-earth-border hover:bg-sand-light text-earth-dark font-medium transition shadow-2xs">Jaipur</button>
          <button onclick="openRegistryModal()" class="px-2.5 py-1 rounded-lg bg-sand-light border border-sand-dark/40 text-forest-dark font-bold hover:bg-sand transition shadow-2xs flex items-center space-x-1">
            <span>Data Registry</span>
            <span class="text-[10px]">&rarr;</span>
          </button>
        </div>

        <!-- Data State System Transparency Banner -->
        <div class="pt-3 border-t border-earth-border/60 flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-[11px] text-earth-muted">
          <span class="font-bold text-earth-dark uppercase tracking-wider">Data State System:</span>
          <span class="inline-flex items-center space-x-1 text-forest"><span class="w-2 h-2 rounded-full bg-forest"></span><span>Verified (Retrieved)</span></span>
          <span class="inline-flex items-center space-x-1 text-sky-dark"><span class="w-2 h-2 rounded-full bg-sky"></span><span>Derived (Mathematical)</span></span>
          <span class="inline-flex items-center space-x-1 text-[#936639]"><span class="w-2 h-2 rounded-full bg-sand-dark"></span><span>Estimated (SatelliteUNet / SRTM)</span></span>
          <span class="inline-flex items-center space-x-1 text-purple-700"><span class="w-2 h-2 rounded-full bg-purple-500"></span><span>Demo (Reference Tile)</span></span>
          <span class="inline-flex items-center space-x-1 text-terracotta"><span class="w-2 h-2 rounded-full bg-terracotta"></span><span>Unavailable (Data Gap Noted)</span></span>
        </div>
      </div>
    </section>

    <!-- Recently Explored Locations Strip -->
    <section id="recentLocationsSection" class="bg-white border border-earth-border rounded-2xl p-4 shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center space-x-2">
          <svg class="w-4 h-4 text-forest" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span class="text-xs font-bold uppercase tracking-wider text-earth-dark">Recently Explored Locations</span>
        </div>
        <button onclick="clearRecentLocations()" id="btnClearRecent" class="hidden text-[11px] text-earth-muted hover:text-terracotta transition">Clear History</button>
      </div>
      <div id="recentLocationsList" class="flex items-center overflow-x-auto space-x-2 py-1 scrollbar-none text-xs">
        <span class="text-earth-muted/80 italic text-xs py-1">No recent searches in this session. Search any Indian city or click on the map to begin exploring.</span>
      </div>
    </section>
'''

old_map_header = '    <!-- LOCATION HERO & MAP SECTION -->\n    <section class="bg-white border border-earth-border rounded-2xl overflow-hidden shadow-sm">'
new_map_header = hero_section_code + '\n    <!-- LOCATION HERO & MAP SECTION -->\n    <section id="mapSection" class="bg-white border border-earth-border rounded-2xl overflow-hidden shadow-sm">'

if old_map_header in html:
    html = html.replace(old_map_header, new_map_header, 1)

# 4. Enhance Active Survey Location Header with 'Save Location' button & Data State Badge
old_survey_bar = '''          <h2 id="heroLocationTitle" class="text-lg font-bold text-earth-dark mt-0.5">
            Loading demonstration location...
          </h2>
          <p id="heroLocationSubtitle" class="text-xs text-earth-muted">
            Coordinates: -- • Regional Earth Observation (Delhi NCR Study Area)
          </p>'''

new_survey_bar = '''          <div class="flex items-center space-x-2 mt-0.5 flex-wrap gap-y-1">
            <h2 id="heroLocationTitle" class="text-lg sm:text-xl font-bold text-earth-dark font-serif">
              Loading survey location...
            </h2>
            <span id="activeDataStateBadge" class="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-200">
              DEMO DATA — NOT A VERIFIED REAL-WORLD OBSERVATION
            </span>
          </div>
          <p id="heroLocationSubtitle" class="text-xs text-earth-muted mt-0.5">
            Coordinates: -- • Regional Earth Observation Footprint
          </p>'''

if old_survey_bar in html:
    html = html.replace(old_survey_bar, new_survey_bar, 1)

# Add "Save to My Places" button beside basemap controls
old_map_buttons = '''          <button onclick="resetMapView()" class="px-3 py-1.5 bg-earth-cardTint hover:bg-sand-light text-forest text-xs font-semibold rounded-xl border border-earth-border transition">
            Fit Extent
          </button>'''

new_map_buttons = '''          <button onclick="resetMapView()" class="px-3 py-1.5 bg-earth-cardTint hover:bg-sand-light text-forest text-xs font-semibold rounded-xl border border-earth-border transition">
            Fit Extent
          </button>
          <button onclick="promptSaveCurrentLocation()" id="btnSaveCurrentPlace" class="px-3 py-1.5 bg-white hover:bg-sand-light text-forest text-xs font-bold rounded-xl border border-earth-border transition shadow-2xs flex items-center space-x-1.5">
            <svg class="w-3.5 h-3.5 text-sage-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
            </svg>
            <span>Save Location</span>
          </button>'''

if old_map_buttons in html:
    html = html.replace(old_map_buttons, new_map_buttons, 1)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Checkpoint A layout and branding successfully applied!")
