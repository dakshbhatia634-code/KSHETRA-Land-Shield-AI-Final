"""
KSHETRA — LAND SHIELD AI
Assembly Script for Full Multi-View SaaS Application.
"""

from pathlib import Path

def assemble_saas():
    base_dir = Path(__file__).resolve().parent
    frontend_dir = base_dir.parent / "frontend"
    output_file = frontend_dir / "index.html"

    # HTML Head & Styles
    head = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KSHETRA — LAND SHIELD AI | Verifying Titles. Securing Boundaries.</title>

  <!-- MapLibre GL JS -->
  <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" />
  <script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>

  <!-- Tailwind CSS & Google Fonts -->
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,600;1,700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
            sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          colors: {
            ivory: '#FBF9F5',
            cream: '#FAF8F3',
            forest: {
              DEFAULT: '#45634D',
              dark: '#2B4333',
              light: '#5A7D63',
            },
            sage: {
              DEFAULT: '#8DAA91',
              light: '#B6CBB9',
              dark: '#6E8E74',
            },
            sand: {
              DEFAULT: '#EADCC8',
              light: '#F5EFE6',
              dark: '#D8C5AB',
            },
            sky: {
              DEFAULT: '#7BA7BC',
              light: '#E8F1F5',
              dark: '#5B8C9F',
            },
            terracotta: {
              DEFAULT: '#C88A75',
              light: '#F8EDE9',
              dark: '#A86D5A',
            },
            earth: {
              dark: '#223026',
              text: '#2C3E33',
              muted: '#637367',
              border: '#E2DDD1',
              card: '#FFFFFF',
              cardTint: '#FCFBF7',
            }
          }
        }
      }
    }
  </script>

  <style>
    html {
      scroll-behavior: smooth;
    }
    body {
      background-color: #F6F3E9;
      color: #223026;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.3s ease, color 0.3s ease;
    }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #D8C5AB; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: #8DAA91; }

    .app-view {
      animation: fadeIn 0.22s ease-out forwards;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes kenBurns {
      0% { transform: scale(1); }
      100% { transform: scale(1.08); }
    }
    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-8px); }
    }
    .ken-burns {
      animation: kenBurns 28s ease-in-out infinite alternate;
    }
    .animate-float {
      animation: float 6s ease-in-out infinite;
    }

    @media print {
      body { background: white !important; color: black !important; }
      #appSidebar, header, #floatingAdvisorLauncher, #floatingAdvisorPanel, button, .nav-item, #techModal, #parameterDetailModal, #authModal, #savePlaceModal, #comparePlacesModal, #editPlaceNotesModal, .print\\:hidden { display: none !important; }
      #appContentShell { padding-left: 0 !important; }
      main { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
      .app-view { display: none !important; }
      #view_reports { display: block !important; }
      #reportContainer { border: 1px solid #ddd !important; box-shadow: none !important; padding: 24px !important; max-width: 100% !important; }
    }
  </style>
</head>
<body class="min-h-screen flex flex-col font-sans">
"""

    sections = [
        "section_sidebar_topbar.html",
        "section_dashboard_view.html",
        "section_explore_view.html",
        "section_intelligence_view.html",
        "section_places_view.html",
        "section_registry_view.html",
        "section_reports_view.html",
        "section_advisor_view.html",
        "section_profile_settings_landing.html",
        "section_modals.html",
        "section_script.js"
    ]

    parts = [head]

    # Split sidebar and topbar so header and main are wrapped in a 64-padding container
    sidebar_topbar = (base_dir / "section_sidebar_topbar.html").read_text(encoding="utf-8")
    split_marker = "<!-- 2. TOP APPLICATION BAR"
    if split_marker in sidebar_topbar:
        sidebar_html, topbar_html = sidebar_topbar.split(split_marker, 1)
        parts.append(sidebar_html)
        parts.append('\n  <!-- Application Content Shell -->\n')
        parts.append('  <div id="appContentShell" class="flex-1 flex flex-col min-w-0 min-h-screen transition-all duration-300 ease-in-out">\n')
        parts.append("    " + split_marker + topbar_html)
        parts.append('\n    <main id="appMain" class="flex-1 flex flex-col p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-6 pb-24">\n')
    else:
        parts.append(sidebar_topbar)
        parts.append('\n  <div id="appContentShell" class="md:pl-64 flex-1 flex flex-col min-w-0 min-h-screen transition-all duration-300 ease-in-out">\n')
        parts.append('\n    <main id="appMain" class="flex-1 flex flex-col p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-6 pb-24">\n')

    # Main views
    view_files = [
        "section_dashboard_view.html",
        "section_explore_view.html",
        "section_intelligence_view.html",
        "section_mllab_view.html",
        "section_places_view.html",
        "section_registry_view.html",
        "section_reports_view.html",
        "section_advisor_view.html",
        "section_profile_settings_landing.html"
    ]
    for vf in view_files:
        content = (base_dir / vf).read_text(encoding="utf-8")
        parts.append(content)
        parts.append("\n")

    # Close main container wrapper and outer shell
    parts.append("    </main>\n")
    parts.append("  </div><!-- End Content Shell -->\n")

    # Modals and scripts
    parts.append((base_dir / "section_modals.html").read_text(encoding="utf-8"))
    parts.append("\n")
    parts.append((base_dir / "section_script.js").read_text(encoding="utf-8"))
    parts.append("\n</body>\n</html>\n")

    full_html = "".join(parts)
    output_file.write_text(full_html, encoding="utf-8")
    print(f"Successfully assembled {output_file} ({len(full_html):,} bytes).")

if __name__ == "__main__":
    assemble_saas()
