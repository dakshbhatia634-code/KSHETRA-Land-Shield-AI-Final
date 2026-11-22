"""
Build script for KSHETRA Cinematic Homepage Replacement.
Generates scratch/section_dashboard_view.html.
"""

from pathlib import Path

def generate_dashboard_view():
    base_dir = Path(__file__).resolve().parent
    out_file = base_dir / "section_dashboard_view.html"

    html = """<!-- ========================================================================= -->
<!-- VIEW 1: KSHETRA CINEMATIC HOMEPAGE & LANDING EXPERIENCE                   -->
<!-- ========================================================================= -->
<section id="view_dashboard" class="app-view w-full bg-[#050806] text-white selection:bg-emerald-500 selection:text-black min-h-screen">

  <!-- 1. FLOATING MINIMAL DARK NAVIGATION -->
  <nav class="sticky top-0 z-50 backdrop-blur-xl bg-[#050806]/85 border-b border-emerald-950/60 px-6 sm:px-10 lg:px-16 py-4 flex items-center justify-between transition-all duration-300">
    <!-- Brand -->
    <div class="flex items-center space-x-3 cursor-pointer" onclick="navigateTo('dashboard')">
      <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-900 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20 ring-1 ring-emerald-400/30 shrink-0">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-3 1.5-4 4.5-4 7m4-7c3 1.5 4 4.5 4 7m-4-7v7" stroke-width="1.8" />
        </svg>
      </div>
      <div class="leading-tight">
        <div class="flex items-center space-x-2">
          <span class="text-xl font-bold font-serif tracking-wider text-white">KSHETRA</span>
          <span class="px-1.5 py-0.5 text-[9px] font-mono uppercase tracking-widest bg-emerald-950/80 text-emerald-400 border border-emerald-800/40 rounded">LAND SHIELD AI</span>
        </div>
        <div class="text-[10px] tracking-[0.2em] uppercase text-zinc-400 font-sans">Earth Intelligence</div>
      </div>
    </div>

    <!-- Center Navigation Links -->
    <div class="hidden lg:flex items-center space-x-8 text-xs font-semibold uppercase tracking-widest text-zinc-300">
      <button onclick="navigateTo('explore')" class="hover:text-emerald-400 transition-colors flex items-center space-x-1.5">
        <span>Explore India</span>
      </button>
      <button onclick="navigateTo('intelligence')" class="hover:text-emerald-400 transition-colors flex items-center space-x-1.5">
        <span>Land Intelligence</span>
      </button>
      <button onclick="navigateTo('mllab')" class="hover:text-emerald-400 transition-colors flex items-center space-x-1.5">
        <span>32 Verified Sites</span>
      </button>
      <button onclick="navigateTo('reports')" class="hover:text-emerald-400 transition-colors flex items-center space-x-1.5">
        <span>Due Diligence</span>
      </button>
      <button onclick="navigateTo('advisor')" class="hover:text-emerald-400 transition-colors flex items-center space-x-1.5">
        <span>AI Advisor</span>
      </button>
    </div>

    <!-- Right Actions -->
    <div class="flex items-center space-x-3">
      <button onclick="navigateTo('explore')" class="relative group px-5 py-2.5 rounded-full text-xs font-bold uppercase tracking-wider text-black bg-gradient-to-r from-emerald-400 to-teal-300 hover:from-emerald-300 hover:to-teal-200 transition-all shadow-[0_0_20px_rgba(16,185,129,0.35)] hover:shadow-[0_0_30px_rgba(16,185,129,0.55)] flex items-center space-x-2">
        <span>Launch Console</span>
        <svg class="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
      </button>
      <button onclick="openAuthModal()" class="hidden sm:flex items-center space-x-2 px-3.5 py-2 rounded-full text-xs font-medium text-zinc-300 hover:text-white border border-emerald-900/60 hover:bg-emerald-950/30 transition">
        <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
        <span id="navAuthLabelHome">Sign In</span>
      </button>
      <button onclick="toggleSidebarDirectly()" title="Open Workspace Sidebar" class="p-2.5 rounded-xl text-zinc-400 hover:text-white border border-emerald-950 hover:bg-emerald-950/50 transition">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/></svg>
      </button>
    </div>
  </nav>

  <!-- ======================================================================= -->
  <!-- 2. FULL VIEWPORT IMMERSIVE HERO (ABOVE THE FOLD)                        -->
  <!-- ======================================================================= -->
  <header class="relative min-h-[92vh] lg:min-h-screen flex flex-col justify-between overflow-hidden px-6 sm:px-12 lg:px-20 pt-8 sm:pt-14 pb-10">

    <!-- Topographic Contour Lines SVG Background -->
    <div class="absolute inset-0 pointer-events-none opacity-20">
      <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" viewBox="0 0 1440 900">
        <path d="M0,200 C300,120 600,280 900,160 C1200,40 1350,180 1440,140" fill="none" stroke="#34D399" stroke-width="1.2" stroke-dasharray="6,4" />
        <path d="M0,320 C250,220 550,380 850,260 C1150,140 1320,270 1440,220" fill="none" stroke="#10B981" stroke-width="1.5" />
        <path d="M0,450 C350,380 650,520 950,410 C1250,300 1380,420 1440,360" fill="none" stroke="#059669" stroke-width="1.2" />
        <path d="M0,580 C280,500 580,660 880,540 C1180,420 1340,560 1440,510" fill="none" stroke="#34D399" stroke-width="0.8" stroke-dasharray="4,6" />
        <path d="M0,720 C320,640 620,800 920,680 C1220,560 1360,700 1440,650" fill="none" stroke="#10B981" stroke-width="1.2" />
      </svg>
    </div>

    <!-- Aurora & Emerald Atmospheric Glow Gradients -->
    <div class="absolute -top-40 right-[-10%] w-[850px] h-[850px] rounded-full bg-emerald-600/15 blur-[160px] pointer-events-none animate-pulse" style="animation-duration: 8s;"></div>
    <div class="absolute top-1/3 left-[-15%] w-[600px] h-[600px] rounded-full bg-teal-800/10 blur-[140px] pointer-events-none"></div>

    <!-- Main Hero Content: Two-Column Composition -->
    <div class="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center my-auto">
      
      <!-- Left Column: Typography & Dramatic Statement -->
      <div class="lg:col-span-7 space-y-6">
        
        <!-- Tagline Pill -->
        <div class="inline-flex items-center space-x-2.5 px-4 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-700/40 text-emerald-300 text-xs tracking-[0.25em] uppercase font-mono shadow-inner shadow-emerald-500/10">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span class="font-semibold">Verifying Titles · Securing Boundaries</span>
        </div>

        <!-- Massive Cinematic Serif Headline -->
        <h1 class="font-serif text-5xl sm:text-7xl lg:text-[7.2rem] text-white font-medium tracking-tight leading-[0.92]">
          Understand<br>
          <span class="italic font-light text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-emerald-400 to-teal-200">what lies</span> beneath.
        </h1>

        <!-- Concise Discover Sentence -->
        <p class="text-zinc-300 text-base sm:text-lg lg:text-xl max-w-xl font-normal leading-relaxed">
          Autonomous multi-spectral Earth observation and AI land intelligence decoding topography, vegetation vitality, and ground truth across India.
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-wrap items-center gap-4 pt-2">
          <button onclick="navigateTo('explore')" class="px-8 py-4 rounded-full bg-emerald-400 hover:bg-emerald-300 text-black font-bold text-sm tracking-wide transition-all shadow-[0_0_35px_rgba(16,185,129,0.35)] hover:shadow-[0_0_50px_rgba(16,185,129,0.55)] flex items-center space-x-3 group">
            <span>Explore India</span>
            <svg class="w-4 h-4 group-hover:translate-x-1.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </button>
          <button onclick="navigateTo('mllab')" class="px-6 py-4 rounded-full bg-emerald-950/40 hover:bg-emerald-900/40 text-emerald-200 border border-emerald-800/40 hover:border-emerald-600/50 font-semibold text-sm tracking-wide transition-all flex items-center space-x-2">
            <span>Inspect 32 Verified Sites</span>
            <span class="px-2 py-0.5 text-[10px] bg-emerald-900/80 text-emerald-300 rounded-full font-mono">18 States</span>
          </button>
        </div>

        <!-- Fast Location Finder Pill -->
        <div class="pt-4 max-w-lg">
          <div class="flex items-center bg-[#09120C]/90 border border-emerald-900/60 rounded-2xl p-1.5 focus-within:border-emerald-500/80 transition-colors shadow-2xl">
            <svg class="w-5 h-5 text-emerald-400 ml-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            <input type="text" id="heroLocationSearch" placeholder="Search any location in India (e.g. Wayanad, Nashik, Varanasi)..." class="bg-transparent text-sm text-white placeholder-zinc-500 px-3 py-2 w-full focus:outline-none" onkeydown="if(event.key==='Enter') executeHeroSearch()">
            <button onclick="executeHeroSearch()" class="px-4 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 rounded-xl text-xs font-semibold transition shrink-0">Search</button>
          </div>
        </div>

      </div>

      <!-- Right Column: 3D Moss Earth & Holographic Data Centerpiece (Alethia Style) -->
      <div class="lg:col-span-5 relative flex items-center justify-center">
        
        <!-- Glowing Ambient Backdrop Ring -->
        <div class="absolute w-80 sm:w-96 h-80 sm:h-96 rounded-full bg-emerald-500/20 blur-3xl pointer-events-none"></div>

        <!-- Center 3D Floating Earth Container -->
        <div class="relative w-72 sm:w-88 md:w-96 aspect-square rounded-3xl overflow-visible flex items-center justify-center">
          
          <!-- Floating Terrain Visual with Neon Glow -->
          <div class="relative w-full h-full rounded-3xl overflow-hidden border border-emerald-800/40 shadow-[0_20px_60px_rgba(0,0,0,0.8)] group">
            <img src="/assets/earth_hero.jpg" alt="KSHETRA Earth Intelligence" class="w-full h-full object-cover transform scale-105 group-hover:scale-110 transition-transform duration-1000">
            <!-- Neon Green Vein Gradient Overlay -->
            <div class="absolute inset-0 bg-gradient-to-t from-[#050806] via-transparent to-transparent opacity-80"></div>
            <div class="absolute inset-0 bg-radial from-transparent via-emerald-950/20 to-[#050806]/90"></div>
          </div>

          <!-- Holographic Telemetry Tag 1: Top Left -->
          <div class="absolute -top-6 -left-6 sm:-left-10 bg-[#07130B]/90 backdrop-blur-md border border-emerald-700/50 rounded-xl px-3.5 py-2 shadow-xl shadow-black/60 pointer-events-none transform -rotate-1 hover:rotate-0 transition-transform">
            <div class="flex items-center space-x-2">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span class="text-[11px] font-mono font-bold text-white uppercase tracking-wider">1.92 ha · Verified</span>
            </div>
            <div class="text-[10px] text-emerald-400/90 font-mono mt-0.5">Canopy: 82% · NDVI 0.74</div>
          </div>

          <!-- Holographic Telemetry Tag 2: Top Right -->
          <div class="absolute top-10 -right-6 sm:-right-10 bg-[#07130B]/90 backdrop-blur-md border border-emerald-700/50 rounded-xl px-3.5 py-2 shadow-xl shadow-black/60 pointer-events-none transform rotate-2 hover:rotate-0 transition-transform">
            <div class="flex items-center space-x-2">
              <span class="text-[11px] font-mono font-bold text-white uppercase tracking-wider">▲ Elev 482m</span>
            </div>
            <div class="text-[10px] text-emerald-400/90 font-mono mt-0.5">Slope 3.2° · High Stability</div>
          </div>

          <!-- Holographic Telemetry Tag 3: Bottom Left -->
          <div class="absolute -bottom-6 -left-4 sm:-left-8 bg-[#07130B]/90 backdrop-blur-md border border-emerald-700/50 rounded-xl px-3.5 py-2 shadow-xl shadow-black/60 pointer-events-none transform rotate-1 hover:rotate-0 transition-transform">
            <div class="flex items-center space-x-2">
              <span class="w-1.5 h-1.5 rounded-full bg-teal-400"></span>
              <span class="text-[11px] font-mono font-bold text-white uppercase tracking-wider">Sentinel-2 10m</span>
            </div>
            <div class="text-[10px] text-teal-300 font-mono mt-0.5">12 Multi-Spectral Bands</div>
          </div>

          <!-- Holographic Telemetry Tag 4: Bottom Right -->
          <div class="absolute -bottom-4 -right-4 sm:-right-8 bg-[#07130B]/90 backdrop-blur-md border border-emerald-700/50 rounded-xl px-3.5 py-2 shadow-xl shadow-black/60 pointer-events-none transform -rotate-2 hover:rotate-0 transition-transform">
            <div class="flex items-center space-x-2">
              <span class="text-[11px] font-mono font-bold text-emerald-300 uppercase tracking-wider">🛡️ Zero Encroachment</span>
            </div>
            <div class="text-[10px] text-zinc-400 font-mono mt-0.5">Cadastral Lock Verified</div>
          </div>

        </div>

      </div>

    </div>

    <!-- Bottom Bar of Hero: Statement & Scroll Indicator -->
    <div class="relative z-10 pt-12 sm:pt-16 border-t border-emerald-950/60 flex flex-col sm:flex-row items-center justify-between gap-6 text-xs text-zinc-400">
      
      <!-- Left Statement -->
      <div class="max-w-md text-center sm:text-left">
        <p class="font-medium text-zinc-300">Know your land precisely.</p>
        <p class="text-zinc-500 text-[11px]">End-to-end environmental intelligence powered by verified scientific pipelines.</p>
      </div>

      <!-- Center Understated Scroll Indicator -->
      <div class="flex flex-col items-center space-y-1.5 cursor-pointer group" onclick="document.getElementById('storySection').scrollIntoView({behavior: 'smooth'})">
        <span class="text-[10px] font-mono uppercase tracking-[0.25em] text-emerald-400/80 group-hover:text-emerald-300 transition-colors">Scroll to Discover</span>
        <div class="w-5 h-8 rounded-full border border-emerald-800/60 flex items-start justify-center p-1">
          <div class="w-1 h-2 rounded-full bg-emerald-400 animate-bounce"></div>
        </div>
      </div>

      <!-- Right Telemetry Ticker -->
      <div class="flex items-center space-x-3 font-mono text-[11px] text-zinc-500">
        <span class="flex items-center space-x-1.5 text-emerald-400">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>100% Deterministic ML</span>
        </span>
        <span>·</span>
        <span>32 India Sites</span>
        <span>·</span>
        <span>10m GSD</span>
      </div>

    </div>

  </header>

  <!-- ======================================================================= -->
  <!-- 3. IMMERSIVE SCROLL STORYTELLING: EVERY PIECE OF LAND HOLDS A STORY    -->
  <!-- ======================================================================= -->
  <section id="storySection" class="relative py-24 sm:py-32 px-6 sm:px-12 lg:px-20 border-t border-emerald-950/40 bg-gradient-to-b from-[#050806] via-[#070D09] to-[#050806]">
    
    <!-- Section Header -->
    <div class="max-w-4xl mx-auto text-center space-y-4 mb-20 sm:mb-28">
      <div class="text-xs uppercase tracking-[0.35em] text-emerald-400 font-mono font-semibold">The Science of Terrain Decoding</div>
      <h2 class="font-serif text-4xl sm:text-6xl lg:text-7xl text-white tracking-tight leading-[1.05]">
        Every piece of land holds a different story.
      </h2>
      <p class="text-zinc-400 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
        Beneath every parcel lies a complex web of photosynthetic vigor, hydrological drainage, foundation slope stability, and title boundaries. KSHETRA decodes all of it in seconds.
      </p>
    </div>

    <!-- 6 Full-Width Alternating Capability Featurettes -->
    <div class="space-y-24 sm:space-y-36 max-w-6xl mx-auto">

      <!-- Featurette 1: Earth Observation & Multi-Spectral Bands -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
        <!-- Visual -->
        <div class="lg:col-span-6 relative order-2 lg:order-1">
          <div class="relative rounded-3xl overflow-hidden border border-emerald-800/40 bg-[#09140C] p-6 shadow-2xl">
            <div class="flex items-center justify-between pb-4 border-b border-emerald-900/40 text-xs font-mono text-emerald-300">
              <span>SENTINEL-2 MSI RADIOMETRIC STACK</span>
              <span>10M RESOLUTION</span>
            </div>
            <!-- Spectral Grid -->
            <div class="grid grid-cols-2 gap-3 pt-4">
              <div class="bg-[#050B07] p-3 rounded-2xl border border-emerald-900/30">
                <div class="text-[10px] font-mono text-zinc-400">BAND 2 · BLUE</div>
                <div class="text-base font-bold text-white font-mono mt-1">490 nm</div>
                <div class="text-[11px] text-zinc-400 mt-1">Soil / vegetation discrimination</div>
              </div>
              <div class="bg-[#050B07] p-3 rounded-2xl border border-emerald-900/30">
                <div class="text-[10px] font-mono text-zinc-400">BAND 3 · GREEN</div>
                <div class="text-base font-bold text-emerald-400 font-mono mt-1">560 nm</div>
                <div class="text-[11px] text-zinc-400 mt-1">Chlorophyll peak reflectance</div>
              </div>
              <div class="bg-[#050B07] p-3 rounded-2xl border border-emerald-900/30">
                <div class="text-[10px] font-mono text-zinc-400">BAND 4 · RED</div>
                <div class="text-base font-bold text-rose-400 font-mono mt-1">665 nm</div>
                <div class="text-[11px] text-zinc-400 mt-1">Chlorophyll maximum absorption</div>
              </div>
              <div class="bg-[#050B07] p-3 rounded-2xl border border-emerald-900/30">
                <div class="text-[10px] font-mono text-zinc-400">BAND 8 · NIR</div>
                <div class="text-base font-bold text-teal-300 font-mono mt-1">842 nm</div>
                <div class="text-[11px] text-zinc-400 mt-1">Leaf mesophyll cell scattering</div>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-emerald-900/40 flex items-center justify-between text-[11px] font-mono text-zinc-400">
              <span>Revisit: 5-Day Constellation</span>
              <span class="text-emerald-400">Atmospheric BOA Corrected</span>
            </div>
          </div>
        </div>
        <!-- Story -->
        <div class="lg:col-span-6 space-y-4 order-1 lg:order-2">
          <div class="text-xs font-mono uppercase tracking-[0.2em] text-emerald-400 font-semibold">01 · Spaceborne Earth Observation</div>
          <h3 class="font-serif text-3xl sm:text-4xl lg:text-5xl text-white font-medium tracking-tight">
            Spectral signatures beyond human vision.
          </h3>
          <p class="text-zinc-300 text-sm sm:text-base leading-relaxed">
            Conventional inspection relies on visible RGB photographs. KSHETRA ingests European Space Agency Copernicus Sentinel-2 multi-spectral bands at 10-meter ground resolution, capturing invisible near-infrared wavelengths where photosynthetic health, water absorption, and mineral boundaries announce themselves unequivocally.
          </p>
          <div class="pt-2 flex items-center space-x-4">
            <button onclick="navigateTo('explore')" class="text-xs font-bold uppercase tracking-wider text-emerald-400 hover:text-emerald-300 flex items-center space-x-1.5 transition">
              <span>View Sentinel-2 Layers</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Featurette 2: Vegetation Canopy & Chlorophyll -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
        <!-- Story -->
        <div class="lg:col-span-6 space-y-4">
          <div class="text-xs font-mono uppercase tracking-[0.2em] text-emerald-400 font-semibold">02 · Photosynthetic Canopy Vigor</div>
          <h3 class="font-serif text-3xl sm:text-4xl lg:text-5xl text-white font-medium tracking-tight">
            Continuous chlorophyll health and canopy density.
          </h3>
          <p class="text-zinc-300 text-sm sm:text-base leading-relaxed">
            Healthy plants absorb red light for carbon fixation while scattering 85% of near-infrared photons. Our continuous radiometric indices (NDVI, SAVI, Chlorophyll Index) differentiate fertile agricultural parcels from seasonal drought stress, overgrazed scrublands, and structural concrete canopy across all Indian agro-climatic zones.
          </p>
          <div class="pt-2">
            <button onclick="navigateTo('intelligence')" class="text-xs font-bold uppercase tracking-wider text-emerald-400 hover:text-emerald-300 flex items-center space-x-1.5 transition">
              <span>Inspect Canopy Analytics</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
            </button>
          </div>
        </div>
        <!-- Visual -->
        <div class="lg:col-span-6 relative">
          <div class="relative rounded-3xl overflow-hidden border border-emerald-800/40 bg-[#09140C] p-6 shadow-2xl">
            <div class="flex items-center justify-between pb-4 border-b border-emerald-900/40 text-xs font-mono text-emerald-300">
              <span>VEGETATION DENSITY SPECTRUM</span>
              <span>NDVI RANGE [-1.0 to +1.0]</span>
            </div>
            <div class="space-y-4 pt-4">
              <div>
                <div class="flex justify-between text-xs font-mono mb-1">
                  <span class="text-zinc-400">Dense Agroforest / Plantation</span>
                  <span class="text-emerald-400 font-bold">0.72 – 0.88</span>
                </div>
                <div class="h-2 rounded-full bg-zinc-800 overflow-hidden">
                  <div class="h-full bg-emerald-400 rounded-full" style="width: 85%"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-xs font-mono mb-1">
                  <span class="text-zinc-400">Active Double-Cropping Farmland</span>
                  <span class="text-teal-300 font-bold">0.52 – 0.71</span>
                </div>
                <div class="h-2 rounded-full bg-zinc-800 overflow-hidden">
                  <div class="h-full bg-teal-400 rounded-full" style="width: 65%"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-xs font-mono mb-1">
                  <span class="text-zinc-400">Semi-Arid Scrub & Grassland</span>
                  <span class="text-amber-300 font-bold">0.24 – 0.45</span>
                </div>
                <div class="h-2 rounded-full bg-zinc-800 overflow-hidden">
                  <div class="h-full bg-amber-400 rounded-full" style="width: 38%"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-xs font-mono mb-1">
                  <span class="text-zinc-400">Barren Topsoil / Concrete Build</span>
                  <span class="text-rose-400 font-bold">0.05 – 0.18</span>
                </div>
                <div class="h-2 rounded-full bg-zinc-800 overflow-hidden">
                  <div class="h-full bg-rose-400 rounded-full" style="width: 15%"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Featurette 3: Soil Mechanics & NASA SRTM Topography -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
        <!-- Visual -->
        <div class="lg:col-span-6 relative order-2 lg:order-1">
          <div class="relative rounded-3xl overflow-hidden border border-emerald-800/40 bg-[#09140C] p-6 shadow-2xl">
            <div class="flex items-center justify-between pb-4 border-b border-emerald-900/40 text-xs font-mono text-emerald-300">
              <span>NASA SRTM 30M DIGITAL ELEVATION MODEL</span>
              <span>TERRAIN MECHANICS</span>
            </div>
            <div class="grid grid-cols-3 gap-3 pt-4 text-center">
              <div class="bg-[#050B07] p-4 rounded-2xl border border-emerald-900/30">
                <div class="text-[10px] font-mono text-zinc-400 uppercase">Elevation</div>
                <div class="text-2xl font-bold text-white font-mono mt-1">482 m</div>
                <div class="text-[10px] text-emerald-400 mt-1">Plateau Terrain</div>
              </div>
              <div class="bg-[#050B07] p-4 rounded-2xl border border-emerald-900/30">
                <div class="text-[10px] font-mono text-zinc-400 uppercase">Slope Gradient</div>
                <div class="text-2xl font-bold text-emerald-400 font-mono mt-1">3.2°</div>
                <div class="text-[10px] text-emerald-300 mt-1">Gentle (0-5°)</div>
              </div>
              <div class="bg-[#050B07] p-4 rounded-2xl border border-emerald-900/30">
                <div class="text-[10px] font-mono text-zinc-400 uppercase">Foundation</div>
                <div class="text-2xl font-bold text-teal-300 font-mono mt-1">High</div>
                <div class="text-[10px] text-zinc-400 mt-1">Low Shear Risk</div>
              </div>
            </div>
            <div class="mt-4 p-3 bg-emerald-950/40 rounded-xl border border-emerald-800/30 text-xs font-mono text-emerald-200 flex items-center space-x-2">
              <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>Optimal construction feasibility: minimal grading required.</span>
            </div>
          </div>
        </div>
        <!-- Story -->
        <div class="lg:col-span-6 space-y-4 order-1 lg:order-2">
          <div class="text-xs font-mono uppercase tracking-[0.2em] text-emerald-400 font-semibold">03 · Topographic Mechanics & Slope</div>
          <h3 class="font-serif text-3xl sm:text-4xl lg:text-5xl text-white font-medium tracking-tight">
            NASA SRTM elevation and civil engineering stability.
          </h3>
          <p class="text-zinc-300 text-sm sm:text-base leading-relaxed">
            Land gradient dictates stormwater drainage, soil shear risks, retaining wall expenses, and foundation bearing capacity. By integrating NASA Shuttle Radar Topography Mission (SRTM) 30-meter elevation models, KSHETRA calculates precise slope vectors, aspect angles, and structural bearing safety across any Indian coordinate.
          </p>
          <div class="pt-2">
            <button onclick="navigateTo('intelligence')" class="text-xs font-bold uppercase tracking-wider text-emerald-400 hover:text-emerald-300 flex items-center space-x-1.5 transition">
              <span>Examine Terrain Gradients</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Featurette 4: Hydrology & Flood Vulnerability -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
        <!-- Story -->
        <div class="lg:col-span-6 space-y-4">
          <div class="text-xs font-mono uppercase tracking-[0.2em] text-emerald-400 font-semibold">04 · Hydrology & Inundation Risk</div>
          <h3 class="font-serif text-3xl sm:text-4xl lg:text-5xl text-white font-medium tracking-tight">
            Catchment pathways, NDWI, and flood plains.
          </h3>
          <p class="text-zinc-300 text-sm sm:text-base leading-relaxed">
            A parcel dry in March can become an uninsurable flood sink during July monsoons. KSHETRA evaluates Normalized Difference Water Index (NDWI) proxies, historical inundation frequency, and riparian proximity buffers to reveal seasonal waterlogging vulnerabilities before land transactions take place.
          </p>
          <div class="pt-2">
            <button onclick="navigateTo('intelligence')" class="text-xs font-bold uppercase tracking-wider text-emerald-400 hover:text-emerald-300 flex items-center space-x-1.5 transition">
              <span>View Hydrology Proxies</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
            </button>
          </div>
        </div>
        <!-- Visual -->
        <div class="lg:col-span-6 relative">
          <div class="relative rounded-3xl overflow-hidden border border-emerald-800/40 bg-[#09140C] p-6 shadow-2xl">
            <div class="flex items-center justify-between pb-4 border-b border-emerald-900/40 text-xs font-mono text-emerald-300">
              <span>HYDROLOGICAL BUFFER ENGINE</span>
              <span>FLOOD ZONE ASSESSMENT</span>
            </div>
            <div class="space-y-3 pt-4">
              <div class="p-3 bg-[#050B07] rounded-2xl border border-emerald-900/30 flex items-center justify-between">
                <div>
                  <div class="text-xs font-bold text-white">Riparian Buffer Margin</div>
                  <div class="text-[11px] text-zinc-400">Distance to permanent water body</div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-bold font-mono text-emerald-400">1.4 km</div>
                  <div class="text-[10px] text-emerald-300 font-mono">SAFE (> 500m)</div>
                </div>
              </div>
              <div class="p-3 bg-[#050B07] rounded-2xl border border-emerald-900/30 flex items-center justify-between">
                <div>
                  <div class="text-xs font-bold text-white">Waterlogging Vulnerability</div>
                  <div class="text-[11px] text-zinc-400">Micro-depression accumulation</div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-bold font-mono text-teal-300">Low</div>
                  <div class="text-[10px] text-zinc-400 font-mono">Slope-drained</div>
                </div>
              </div>
              <div class="p-3 bg-[#050B07] rounded-2xl border border-emerald-900/30 flex items-center justify-between">
                <div>
                  <div class="text-xs font-bold text-white">Surface Moisture Index</div>
                  <div class="text-[11px] text-zinc-400">NDWI spectral proxy</div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-bold font-mono text-zinc-300">-0.24</div>
                  <div class="text-[10px] text-zinc-400 font-mono">Non-saturated</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Featurette 5: IMD Climatic Normals & Weather -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
        <!-- Visual -->
        <div class="lg:col-span-6 relative order-2 lg:order-1">
          <div class="relative rounded-3xl overflow-hidden border border-emerald-800/40 bg-[#09140C] p-6 shadow-2xl">
            <div class="flex items-center justify-between pb-4 border-b border-emerald-900/40 text-xs font-mono text-emerald-300">
              <span>IMD 30-YEAR GRIDDED CLIMATE NORMALS</span>
              <span>PRECIPITATION CYCLES</span>
            </div>
            <div class="grid grid-cols-2 gap-3 pt-4">
              <div class="bg-[#050B07] p-4 rounded-2xl border border-emerald-900/30">
                <div class="text-[10px] font-mono text-zinc-400 uppercase">Annual Normal Rain</div>
                <div class="text-2xl font-bold text-sky-400 font-mono mt-1">880 mm</div>
                <div class="text-[10px] text-zinc-400 mt-1">Moderate Monsoon Zone</div>
              </div>
              <div class="bg-[#050B07] p-4 rounded-2xl border border-emerald-900/30">
                <div class="text-[10px] font-mono text-zinc-400 uppercase">Monsoon Peak</div>
                <div class="text-2xl font-bold text-white font-mono mt-1">Jul – Aug</div>
                <div class="text-[10px] text-emerald-400 mt-1">72% Annual Inflow</div>
              </div>
            </div>
            <div class="mt-4 p-3 bg-sky-950/30 rounded-xl border border-sky-800/30 text-xs font-mono text-sky-200">
              Verified with India Meteorological Department 1991–2020 climatological normals.
            </div>
          </div>
        </div>
        <!-- Story -->
        <div class="lg:col-span-6 space-y-4 order-1 lg:order-2">
          <div class="text-xs font-mono uppercase tracking-[0.2em] text-emerald-400 font-semibold">05 · Meteorological Climatology</div>
          <h3 class="font-serif text-3xl sm:text-4xl lg:text-5xl text-white font-medium tracking-tight">
            IMD 30-year gridded climate and monsoon patterns.
          </h3>
          <p class="text-zinc-300 text-sm sm:text-base leading-relaxed">
            Real estate and agro-forestry feasibility cannot rely on single-day weather forecasts. KSHETRA anchors each analysis to 30-year gridded rainfall normals from the India Meteorological Department (IMD Pune), predicting rainfall reliability, aridity indices, and heat wave stress across every district in the country.
          </p>
          <div class="pt-2">
            <button onclick="navigateTo('intelligence')" class="text-xs font-bold uppercase tracking-wider text-emerald-400 hover:text-emerald-300 flex items-center space-x-1.5 transition">
              <span>View Climate Normals</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Featurette 6: Agriculture Viability & Title Boundary Defense -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
        <!-- Story -->
        <div class="lg:col-span-6 space-y-4">
          <div class="text-xs font-mono uppercase tracking-[0.2em] text-emerald-400 font-semibold">06 · Agro-Civil Viability & Title Defense</div>
          <h3 class="font-serif text-3xl sm:text-4xl lg:text-5xl text-white font-medium tracking-tight">
            Cadastral title boundaries and multi-use zoning.
          </h3>
          <p class="text-zinc-300 text-sm sm:text-base leading-relaxed">
            Is the land suited for double-cropping, horticultural plantations, or structural civil foundations? Does the physical perimeter on satellite imagery correspond to the registered cadastral deed? KSHETRA delivers deterministic due diligence scoring, reconciling recorded deeds against satellite-verified physical fences.
          </p>
          <div class="pt-2">
            <button onclick="navigateTo('reports')" class="text-xs font-bold uppercase tracking-wider text-emerald-400 hover:text-emerald-300 flex items-center space-x-1.5 transition">
              <span>Generate Due Diligence Report</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
            </button>
          </div>
        </div>
        <!-- Visual -->
        <div class="lg:col-span-6 relative">
          <div class="relative rounded-3xl overflow-hidden border border-emerald-800/40 bg-[#09140C] p-6 shadow-2xl">
            <div class="flex items-center justify-between pb-4 border-b border-emerald-900/40 text-xs font-mono text-emerald-300">
              <span>CADASTRAL BOUNDARY VERIFICATION</span>
              <span>100% RECONCILED</span>
            </div>
            <div class="space-y-3 pt-4">
              <div class="flex items-center justify-between p-3 bg-[#050B07] rounded-xl border border-emerald-900/30">
                <span class="text-xs text-zinc-300">Title Deed Cadastral Area</span>
                <span class="font-mono text-xs font-bold text-white">1.92 Hectares (4.74 Acres)</span>
              </div>
              <div class="flex items-center justify-between p-3 bg-[#050B07] rounded-xl border border-emerald-900/30">
                <span class="text-xs text-zinc-300">Satellite Optical Perimeter</span>
                <span class="font-mono text-xs font-bold text-emerald-400">1.91 Hectares (99.5% Match)</span>
              </div>
              <div class="flex items-center justify-between p-3 bg-[#050B07] rounded-xl border border-emerald-900/30">
                <span class="text-xs text-zinc-300">Encroachment Buffer</span>
                <span class="font-mono text-xs font-bold text-emerald-300">0.00 m (Zero Encroachment)</span>
              </div>
              <div class="p-3 bg-emerald-950/40 rounded-xl border border-emerald-800/30 text-xs font-mono text-emerald-300 flex items-center space-x-2">
                <svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                <span>Clear title boundary verified against physical satellite fences.</span>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

  </section>

  <!-- ======================================================================= -->
  <!-- 4. INTERACTIVE INDIA GEOSPATIAL MAP COMMAND                             -->
  <!-- ======================================================================= -->
  <section class="relative py-24 px-6 sm:px-12 lg:px-20 border-t border-emerald-950/40 bg-[#040805]">
    
    <div class="max-w-6xl mx-auto space-y-8">
      
      <!-- Section Header -->
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div class="text-xs uppercase tracking-[0.3em] text-emerald-400 font-mono font-semibold mb-2">Interactive Geospatial Command</div>
          <h2 class="font-serif text-3xl sm:text-5xl text-white font-medium tracking-tight">
            Explore India's Diverse Terrains in Real Time.
          </h2>
          <p class="text-zinc-400 text-sm sm:text-base mt-2 max-w-xl">
            Live multi-spectral and high-resolution satellite cartography across all Indian states and union territories. Click anywhere to survey ground truth.
          </p>
        </div>
        <button onclick="navigateTo('explore')" class="px-6 py-3 rounded-full bg-emerald-400 hover:bg-emerald-300 text-black font-bold text-xs uppercase tracking-wider transition-all shadow-[0_0_25px_rgba(16,185,129,0.3)] flex items-center space-x-2 shrink-0 self-start md:self-auto">
          <span>Launch Full-Screen Studio</span>
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
        </button>
      </div>

      <!-- Map Container Box -->
      <div class="relative rounded-3xl overflow-hidden border border-emerald-800/40 bg-[#08120B] shadow-2xl">
        
        <!-- Map Controls Bar -->
        <div class="p-4 bg-[#060D08]/90 border-b border-emerald-900/40 flex flex-wrap items-center justify-between gap-4">
          
          <!-- Region Quick Jumps -->
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-mono text-zinc-400 uppercase tracking-wider mr-1">Region:</span>
            <button onclick="dashMapPanTo([78.9629, 20.5937], 4.5)" class="px-3 py-1 rounded-lg text-xs font-mono bg-emerald-950/60 text-emerald-300 hover:bg-emerald-900/60 border border-emerald-800/40 transition">All India</button>
            <button onclick="dashMapPanTo([77.3501, 28.4007], 8.5)" class="px-3 py-1 rounded-lg text-xs font-mono bg-emerald-950/60 text-emerald-300 hover:bg-emerald-900/60 border border-emerald-800/40 transition">North (Indo-Gangetic)</button>
            <button onclick="dashMapPanTo([76.1320, 11.6854], 8.5)" class="px-3 py-1 rounded-lg text-xs font-mono bg-emerald-950/60 text-emerald-300 hover:bg-emerald-900/60 border border-emerald-800/40 transition">South (Western Ghats)</button>
            <button onclick="dashMapPanTo([73.7898, 19.9975], 8.5)" class="px-3 py-1 rounded-lg text-xs font-mono bg-emerald-950/60 text-emerald-300 hover:bg-emerald-900/60 border border-emerald-800/40 transition">West (Deccan)</button>
            <button onclick="dashMapPanTo([94.2037, 26.7509], 8.5)" class="px-3 py-1 rounded-lg text-xs font-mono bg-emerald-950/60 text-emerald-300 hover:bg-emerald-900/60 border border-emerald-800/40 transition">East (Brahmaputra)</button>
          </div>

          <!-- Basemap Selector -->
          <div class="flex items-center space-x-2">
            <span class="text-xs font-mono text-zinc-400 uppercase tracking-wider mr-1">Layer:</span>
            <button id="dashLayerDark" onclick="setDashMapLayer('dark')" class="px-3 py-1 rounded-lg text-xs font-mono bg-emerald-500 text-black font-bold transition">Dark Canvas</button>
            <button id="dashLayerSat" onclick="setDashMapLayer('satellite')" class="px-3 py-1 rounded-lg text-xs font-mono bg-[#09150D] text-zinc-300 hover:text-white border border-emerald-900/50 transition">Satellite</button>
            <button id="dashLayerOSM" onclick="setDashMapLayer('osm')" class="px-3 py-1 rounded-lg text-xs font-mono bg-[#09150D] text-zinc-300 hover:text-white border border-emerald-900/50 transition">Topographic</button>
          </div>

        </div>

        <!-- Working MapLibre GL Canvas -->
        <div id="dashMap" class="w-full h-[520px] bg-[#050806]"></div>

        <!-- Floating HUD Coordinates Box -->
        <div class="absolute bottom-4 left-4 bg-[#060D08]/90 backdrop-blur-md border border-emerald-800/40 rounded-xl p-3 shadow-xl pointer-events-none text-xs font-mono text-zinc-300 space-y-1">
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-emerald-400 font-bold">LIVE TELEMETRY HUD</span>
          </div>
          <div>Target: <span id="dashHudPlace" class="text-white">Faridabad Agro-Urban Fringe</span></div>
          <div>Coords: <span id="dashHudCoords" class="text-emerald-300">28.4007°N, 77.3501°E</span></div>
        </div>

      </div>

    </div>

  </section>

  <!-- ======================================================================= -->
  <!-- 5. GALLERY OF REAL LAND SAMPLES (32 VERIFIED INDIA LOCATIONS)            -->
  <!-- ======================================================================= -->
  <section class="relative py-24 sm:py-32 px-6 sm:px-12 lg:px-20 border-t border-emerald-950/40 bg-gradient-to-b from-[#040805] via-[#070E09] to-[#040805]">
    
    <div class="max-w-6xl mx-auto space-y-12">
      
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div class="text-xs uppercase tracking-[0.3em] text-emerald-400 font-mono font-semibold mb-2">Verified Ground Truth</div>
          <h2 class="font-serif text-3xl sm:text-5xl text-white font-medium tracking-tight">
            Inspected Locations Across 18 States.
          </h2>
          <p class="text-zinc-400 text-sm sm:text-base mt-2 max-w-xl">
            Each parcel contains verified multi-spectral imagery, SRTM elevation, IMD climate normals, and automated machine learning inference. Click any location to survey its land intelligence.
          </p>
        </div>
        <button onclick="navigateTo('mllab')" class="px-6 py-3 rounded-full bg-emerald-950/60 hover:bg-emerald-900/60 text-emerald-300 border border-emerald-800/50 font-bold text-xs uppercase tracking-wider transition flex items-center space-x-2 shrink-0 self-start md:self-auto">
          <span>View All 32 in Catalogue</span>
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
        </button>
      </div>

      <!-- Real Locations Grid (Top 8 Diverse Showcases) -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        <!-- Card 1: Bangalore Rural (Karnataka) -->
        <div class="group bg-[#08120B] border border-emerald-900/40 hover:border-emerald-500/50 rounded-2xl p-4 transition-all duration-300 flex flex-col justify-between shadow-lg hover:shadow-emerald-950/40">
          <div>
            <div class="relative aspect-video rounded-xl overflow-hidden mb-3 bg-zinc-900">
              <img src="/static/imagery/sat_12.5218_76.8951.png" alt="Bangalore Rural" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" onerror="this.src='/static/samples/sample_tile_00000.png'">
              <span class="absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-800/40">Karnataka</span>
            </div>
            <div class="text-sm font-bold text-white">Bangalore Rural</div>
            <div class="text-xs text-zinc-400">Plateau Agriculture</div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono border-t border-emerald-900/40 pt-2 text-zinc-400">
              <div>NDVI: <span class="text-emerald-400 font-bold">0.68</span></div>
              <div>Elev: <span class="text-white">914m</span></div>
              <div>Rain: <span class="text-sky-300">880mm</span></div>
              <div>Slope: <span class="text-zinc-200">2.1°</span></div>
            </div>
          </div>
          <button onclick="selectCatalogueLocation('loc_005')" class="mt-4 w-full py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/30 text-emerald-300 text-xs font-semibold font-mono tracking-wider transition flex items-center justify-center space-x-1.5">
            <span>Inspect Parcel</span>
            <span>&rarr;</span>
          </button>
        </div>

        <!-- Card 2: Wayanad (Kerala) -->
        <div class="group bg-[#08120B] border border-emerald-900/40 hover:border-emerald-500/50 rounded-2xl p-4 transition-all duration-300 flex flex-col justify-between shadow-lg hover:shadow-emerald-950/40">
          <div>
            <div class="relative aspect-video rounded-xl overflow-hidden mb-3 bg-zinc-900">
              <img src="/static/imagery/sat_11.6854_76.1320.png" alt="Wayanad" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" onerror="this.src='/static/samples/sample_tile_00000.png'">
              <span class="absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-800/40">Kerala</span>
            </div>
            <div class="text-sm font-bold text-white">Wayanad Agroforestry</div>
            <div class="text-xs text-zinc-400">Western Ghats Canopy</div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono border-t border-emerald-900/40 pt-2 text-zinc-400">
              <div>NDVI: <span class="text-emerald-400 font-bold">0.81</span></div>
              <div>Elev: <span class="text-white">1,150m</span></div>
              <div>Rain: <span class="text-sky-300">2,320mm</span></div>
              <div>Slope: <span class="text-zinc-200">14.8°</span></div>
            </div>
          </div>
          <button onclick="selectCatalogueLocation('loc_004')" class="mt-4 w-full py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/30 text-emerald-300 text-xs font-semibold font-mono tracking-wider transition flex items-center justify-center space-x-1.5">
            <span>Inspect Parcel</span>
            <span>&rarr;</span>
          </button>
        </div>

        <!-- Card 3: Nashik (Maharashtra) -->
        <div class="group bg-[#08120B] border border-emerald-900/40 hover:border-emerald-500/50 rounded-2xl p-4 transition-all duration-300 flex flex-col justify-between shadow-lg hover:shadow-emerald-950/40">
          <div>
            <div class="relative aspect-video rounded-xl overflow-hidden mb-3 bg-zinc-900">
              <img src="/static/imagery/sat_19.9975_73.7898.png" alt="Nashik" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" onerror="this.src='/static/samples/sample_tile_00000.png'">
              <span class="absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-800/40">Maharashtra</span>
            </div>
            <div class="text-sm font-bold text-white">Nashik Vineyard Basin</div>
            <div class="text-xs text-zinc-400">Deccan Semi-Arid</div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono border-t border-emerald-900/40 pt-2 text-zinc-400">
              <div>NDVI: <span class="text-emerald-400 font-bold">0.54</span></div>
              <div>Elev: <span class="text-white">602m</span></div>
              <div>Rain: <span class="text-sky-300">710mm</span></div>
              <div>Slope: <span class="text-zinc-200">3.8°</span></div>
            </div>
          </div>
          <button onclick="selectCatalogueLocation('loc_011')" class="mt-4 w-full py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/30 text-emerald-300 text-xs font-semibold font-mono tracking-wider transition flex items-center justify-center space-x-1.5">
            <span>Inspect Parcel</span>
            <span>&rarr;</span>
          </button>
        </div>

        <!-- Card 4: Varanasi (Uttar Pradesh) -->
        <div class="group bg-[#08120B] border border-emerald-900/40 hover:border-emerald-500/50 rounded-2xl p-4 transition-all duration-300 flex flex-col justify-between shadow-lg hover:shadow-emerald-950/40">
          <div>
            <div class="relative aspect-video rounded-xl overflow-hidden mb-3 bg-zinc-900">
              <img src="/static/imagery/sat_25.3176_82.9739.png" alt="Varanasi" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" onerror="this.src='/static/samples/sample_tile_00000.png'">
              <span class="absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-800/40">Uttar Pradesh</span>
            </div>
            <div class="text-sm font-bold text-white">Varanasi Alluvial Plains</div>
            <div class="text-xs text-zinc-400">Indo-Gangetic Basin</div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono border-t border-emerald-900/40 pt-2 text-zinc-400">
              <div>NDVI: <span class="text-emerald-400 font-bold">0.72</span></div>
              <div>Elev: <span class="text-white">81m</span></div>
              <div>Rain: <span class="text-sky-300">1,025mm</span></div>
              <div>Slope: <span class="text-zinc-200">0.9°</span></div>
            </div>
          </div>
          <button onclick="selectCatalogueLocation('loc_018')" class="mt-4 w-full py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/30 text-emerald-300 text-xs font-semibold font-mono tracking-wider transition flex items-center justify-center space-x-1.5">
            <span>Inspect Parcel</span>
            <span>&rarr;</span>
          </button>
        </div>

        <!-- Card 5: Barmer (Rajasthan) -->
        <div class="group bg-[#08120B] border border-emerald-900/40 hover:border-emerald-500/50 rounded-2xl p-4 transition-all duration-300 flex flex-col justify-between shadow-lg hover:shadow-emerald-950/40">
          <div>
            <div class="relative aspect-video rounded-xl overflow-hidden mb-3 bg-zinc-900">
              <img src="/static/imagery/sat_25.7532_71.4181.png" alt="Barmer" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" onerror="this.src='/static/samples/sample_tile_00000.png'">
              <span class="absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-800/40">Rajasthan</span>
            </div>
            <div class="text-sm font-bold text-white">Barmer Thar Scrub</div>
            <div class="text-xs text-zinc-400">Arid Solar Zone</div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono border-t border-emerald-900/40 pt-2 text-zinc-400">
              <div>NDVI: <span class="text-amber-400 font-bold">0.16</span></div>
              <div>Elev: <span class="text-white">185m</span></div>
              <div>Rain: <span class="text-sky-300">280mm</span></div>
              <div>Slope: <span class="text-zinc-200">1.2°</span></div>
            </div>
          </div>
          <button onclick="selectCatalogueLocation('loc_020')" class="mt-4 w-full py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/30 text-emerald-300 text-xs font-semibold font-mono tracking-wider transition flex items-center justify-center space-x-1.5">
            <span>Inspect Parcel</span>
            <span>&rarr;</span>
          </button>
        </div>

        <!-- Card 6: Sundarbans (West Bengal) -->
        <div class="group bg-[#08120B] border border-emerald-900/40 hover:border-emerald-500/50 rounded-2xl p-4 transition-all duration-300 flex flex-col justify-between shadow-lg hover:shadow-emerald-950/40">
          <div>
            <div class="relative aspect-video rounded-xl overflow-hidden mb-3 bg-zinc-900">
              <img src="/static/imagery/sat_22.1667_88.7500.png" alt="Sundarbans" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" onerror="this.src='/static/samples/sample_tile_00000.png'">
              <span class="absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-800/40">West Bengal</span>
            </div>
            <div class="text-sm font-bold text-white">Sundarbans Wetland</div>
            <div class="text-xs text-zinc-400">Coastal Mangrove Delta</div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono border-t border-emerald-900/40 pt-2 text-zinc-400">
              <div>NDVI: <span class="text-emerald-400 font-bold">0.64</span></div>
              <div>Elev: <span class="text-white">4m</span></div>
              <div>Rain: <span class="text-sky-300">1,890mm</span></div>
              <div>Slope: <span class="text-zinc-200">0.4°</span></div>
            </div>
          </div>
          <button onclick="selectCatalogueLocation('loc_014')" class="mt-4 w-full py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/30 text-emerald-300 text-xs font-semibold font-mono tracking-wider transition flex items-center justify-center space-x-1.5">
            <span>Inspect Parcel</span>
            <span>&rarr;</span>
          </button>
        </div>

        <!-- Card 7: Jorhat (Assam) -->
        <div class="group bg-[#08120B] border border-emerald-900/40 hover:border-emerald-500/50 rounded-2xl p-4 transition-all duration-300 flex flex-col justify-between shadow-lg hover:shadow-emerald-950/40">
          <div>
            <div class="relative aspect-video rounded-xl overflow-hidden mb-3 bg-zinc-900">
              <img src="/static/imagery/sat_26.7509_94.2037.png" alt="Jorhat" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" onerror="this.src='/static/samples/sample_tile_00000.png'">
              <span class="absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-800/40">Assam</span>
            </div>
            <div class="text-sm font-bold text-white">Jorhat Tea Terraces</div>
            <div class="text-xs text-zinc-400">Brahmaputra Valley</div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono border-t border-emerald-900/40 pt-2 text-zinc-400">
              <div>NDVI: <span class="text-emerald-400 font-bold">0.79</span></div>
              <div>Elev: <span class="text-white">116m</span></div>
              <div>Rain: <span class="text-sky-300">2,150mm</span></div>
              <div>Slope: <span class="text-zinc-200">2.6°</span></div>
            </div>
          </div>
          <button onclick="selectCatalogueLocation('loc_022')" class="mt-4 w-full py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/30 text-emerald-300 text-xs font-semibold font-mono tracking-wider transition flex items-center justify-center space-x-1.5">
            <span>Inspect Parcel</span>
            <span>&rarr;</span>
          </button>
        </div>

        <!-- Card 8: Kutch (Gujarat) -->
        <div class="group bg-[#08120B] border border-emerald-900/40 hover:border-emerald-500/50 rounded-2xl p-4 transition-all duration-300 flex flex-col justify-between shadow-lg hover:shadow-emerald-950/40">
          <div>
            <div class="relative aspect-video rounded-xl overflow-hidden mb-3 bg-zinc-900">
              <img src="/static/imagery/sat_23.7337_69.8597.png" alt="Kutch" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" onerror="this.src='/static/samples/sample_tile_00000.png'">
              <span class="absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-800/40">Gujarat</span>
            </div>
            <div class="text-sm font-bold text-white">Kutch Coastal Marsh</div>
            <div class="text-xs text-zinc-400">Saline Intertidal</div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono border-t border-emerald-900/40 pt-2 text-zinc-400">
              <div>NDVI: <span class="text-amber-400 font-bold">0.14</span></div>
              <div>Elev: <span class="text-white">15m</span></div>
              <div>Rain: <span class="text-sky-300">360mm</span></div>
              <div>Slope: <span class="text-zinc-200">0.6°</span></div>
            </div>
          </div>
          <button onclick="selectCatalogueLocation('loc_016')" class="mt-4 w-full py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/30 text-emerald-300 text-xs font-semibold font-mono tracking-wider transition flex items-center justify-center space-x-1.5">
            <span>Inspect Parcel</span>
            <span>&rarr;</span>
          </button>
        </div>

      </div>

    </div>

  </section>

  <!-- ======================================================================= -->
  <!-- 6. AI INTELLIGENCE & DETERMINISTIC PIPELINES                            -->
  <!-- ======================================================================= -->
  <section class="relative py-24 sm:py-32 px-6 sm:px-12 lg:px-20 border-t border-emerald-950/40 bg-[#050806]">
    
    <div class="max-w-6xl mx-auto space-y-16">
      
      <!-- Section Header -->
      <div class="max-w-3xl space-y-4">
        <div class="text-xs uppercase tracking-[0.3em] text-emerald-400 font-mono font-semibold">Engineered For Truth</div>
        <h2 class="font-serif text-3xl sm:text-5xl text-white font-medium tracking-tight">
          How KSHETRA Decodes What Lies Beneath.
        </h2>
        <p class="text-zinc-400 text-sm sm:text-base leading-relaxed">
          We combine continuous multi-spectral satellite sensing, rigorous geodetic boundary reconciliation, and deterministic statistical models trained on 1,500 calibrated Sentinel-2 tiles across India.
        </p>
      </div>

      <!-- 3 Pillars Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <div class="p-8 rounded-3xl bg-[#08120B] border border-emerald-900/40 space-y-4">
          <div class="w-12 h-12 rounded-2xl bg-emerald-500/15 border border-emerald-700/40 flex items-center justify-center text-emerald-300">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
          </div>
          <h3 class="text-xl font-bold font-serif text-white">Autonomous Multi-Spectral Vision</h3>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Neural computer vision processes 10-meter Sentinel-2 bands to segment photosynthetic canopy, identify soil waterlogging, and classify ground cover without human bias.
          </p>
          <div class="pt-2 text-[11px] font-mono text-emerald-400">10m Spatial Resolution · 5-Day Revisit</div>
        </div>

        <div class="p-8 rounded-3xl bg-[#08120B] border border-emerald-900/40 space-y-4">
          <div class="w-12 h-12 rounded-2xl bg-teal-500/15 border border-teal-700/40 flex items-center justify-center text-teal-300">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg>
          </div>
          <h3 class="text-xl font-bold font-serif text-white">Cadastral Title Boundary Lock</h3>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Geometric perimeter algorithms reconcile physical field fences seen on optical satellite imagery against recorded title deeds to identify boundary drift and encroachment.
          </p>
          <div class="pt-2 text-[11px] font-mono text-teal-300">Deterministic Boundary Reconciliation</div>
        </div>

        <div class="p-8 rounded-3xl bg-[#08120B] border border-emerald-900/40 space-y-4">
          <div class="w-12 h-12 rounded-2xl bg-sky-500/15 border border-sky-700/40 flex items-center justify-center text-sky-300">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          </div>
          <h3 class="text-xl font-bold font-serif text-white">Predictive Environmental Due Diligence</h3>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Multi-factor scoring synthesizes NASA SRTM slope, IMD 30-year precipitation normals, and hydrological drainage to compute foundation feasibility and agricultural viability.
          </p>
          <div class="pt-2 text-[11px] font-mono text-sky-300">Comprehensive Due Diligence Scoring</div>
        </div>

      </div>

      <!-- Action Banner -->
      <div class="p-8 sm:p-12 rounded-3xl bg-gradient-to-r from-emerald-950/70 via-[#0A1810] to-[#08130B] border border-emerald-700/40 flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl">
        <div class="space-y-2 text-center md:text-left">
          <h3 class="font-serif text-2xl sm:text-3xl text-white font-medium">Ready to inspect any land across India?</h3>
          <p class="text-xs sm:text-sm text-zinc-400 max-w-xl">
            Acquire multi-spectral satellite imagery, download certified due diligence reports, or ask the AI Land Advisor in natural conversational language.
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-3 shrink-0">
          <button onclick="navigateTo('reports')" class="px-6 py-3 rounded-full bg-emerald-400 hover:bg-emerald-300 text-black font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-emerald-500/20">
            Generate Report
          </button>
          <button onclick="openFloatingAdvisor()" class="px-6 py-3 rounded-full bg-emerald-950/60 hover:bg-emerald-900/60 text-emerald-300 border border-emerald-800/50 font-semibold text-xs tracking-wider transition">
            Consult AI Advisor
          </button>
        </div>
      </div>

    </div>

  </section>

  <!-- ======================================================================= -->
  <!-- 7. CINEMATIC DARK FOOTER                                                -->
  <!-- ======================================================================= -->
  <footer class="border-t border-emerald-950/60 bg-[#030604] py-14 px-6 sm:px-12 lg:px-20 text-xs text-zinc-400">
    <div class="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
      
      <!-- Brand & Tagline -->
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-700/40 flex items-center justify-center text-emerald-300">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
        </div>
        <div>
          <div class="text-sm font-bold font-serif text-white tracking-wider">KSHETRA · LAND SHIELD AI</div>
          <div class="text-[10px] uppercase font-mono tracking-widest text-emerald-400/90">Verifying Titles · Securing Boundaries</div>
        </div>
      </div>

      <!-- Data Source Attribution -->
      <div class="text-center md:text-left text-[11px] text-zinc-400 space-y-0.5">
        <div>Verified telemetry sourced from European Space Agency Copernicus Sentinel-2, NASA SRTM, and IMD Pune.</div>
        <div class="text-zinc-400">Zero synthetic fabrication. 100% deterministic geospatial and environmental telemetry.</div>
      </div>

      <!-- Fast Links -->
      <div class="flex items-center space-x-6 text-zinc-400 font-mono text-[11px]">
        <button onclick="navigateTo('explore')" class="hover:text-emerald-400 transition">Explore</button>
        <button onclick="navigateTo('intelligence')" class="hover:text-emerald-400 transition">Intelligence</button>
        <button onclick="navigateTo('mllab')" class="hover:text-emerald-400 transition">32 Sites</button>
        <button onclick="navigateTo('reports')" class="hover:text-emerald-400 transition">Reports</button>
        <button onclick="navigateTo('registry')" class="hover:text-emerald-400 transition">Sources</button>
      </div>

    </div>

    <div class="max-w-6xl mx-auto mt-8 pt-6 border-t border-emerald-950/40 flex flex-col sm:flex-row items-center justify-between text-[11px] text-zinc-400 gap-4">
      <div>&copy; 2026 KSHETRA · LAND SHIELD AI. All rights reserved across Indian territories.</div>
      <div class="flex items-center space-x-2 text-emerald-500 font-mono">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
        <span>Telemetry Pipeline Active · 100% Deterministic</span>
      </div>
    </div>
  </footer>

</section>
"""

    out_file.write_text(html, encoding="utf-8")
    print(f"Successfully generated {out_file} ({len(html):,} bytes).")

if __name__ == "__main__":
    generate_dashboard_view()
