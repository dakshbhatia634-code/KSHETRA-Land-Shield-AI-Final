"""
Refine scratch/section_dashboard_view.html for above-the-fold 800px viewport fit
and use cleaned rock graphic without background text.
"""

from pathlib import Path

def refine_dashboard():
    dashboard_path = Path("scratch/section_dashboard_view.html")
    content = dashboard_path.read_text(encoding="utf-8")

    # Replace /assets/earth_hero.jpg with /assets/earth_rock_clean.jpg
    content = content.replace('/assets/earth_hero.jpg', '/assets/earth_rock_clean.jpg')

    # Update header padding and typography sizing for 800px fold fit
    old_header = '<header class="relative min-h-[95vh] lg:min-h-screen flex flex-col justify-between overflow-hidden px-6 sm:px-12 lg:px-20 pt-12 sm:pt-20 pb-12">'
    new_header = '<header class="relative min-h-[90vh] flex flex-col justify-between overflow-hidden px-6 sm:px-10 lg:px-16 pt-6 sm:pt-8 pb-8">'
    if old_header in content:
        content = content.replace(old_header, new_header)

    old_h1 = '<h1 class="font-serif text-6xl sm:text-7xl lg:text-[7.8rem] text-white font-medium tracking-tight leading-[0.9]">'
    new_h1 = '<h1 class="font-serif text-5xl sm:text-6xl lg:text-7xl text-white font-medium tracking-tight leading-[0.9]">'
    if old_h1 in content:
        content = content.replace(old_h1, new_h1)

    old_sub = '<div class="font-serif italic text-2xl sm:text-4xl lg:text-5xl font-light text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-emerald-400 to-teal-200">'
    new_sub = '<div class="font-serif italic text-xl sm:text-3xl lg:text-4xl font-light text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-emerald-400 to-teal-200">'
    if old_sub in content:
        content = content.replace(old_sub, new_sub)

    # Adjust rock container size
    content = content.replace('w-72 sm:w-88 md:w-96 aspect-square', 'w-64 sm:w-76 md:w-84 aspect-square')

    dashboard_path.write_text(content, encoding="utf-8")
    print("Successfully refined section_dashboard_view.html")

if __name__ == "__main__":
    refine_dashboard()
