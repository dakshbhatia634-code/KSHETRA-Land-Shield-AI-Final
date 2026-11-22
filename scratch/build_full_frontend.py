"""
KSHETRA — LAND SHIELD AI
Full Multi-View SaaS Application Generator.
"""

def get_html_head():
    return '''<!DOCTYPE html>
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
    body {
      background-color: #F6F3E9;
      color: #223026;
      -webkit-font-smoothing: antialiased;
    }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #D8C5AB; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: #8DAA91; }

    .app-view {
      animation: fadeIn 0.2s ease-out forwards;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body class="min-h-screen flex flex-col font-sans">
'''

with open('scratch/builder_head.py', 'w', encoding='utf-8') as f:
    f.write(get_html_head())

print("Head generator complete.")
