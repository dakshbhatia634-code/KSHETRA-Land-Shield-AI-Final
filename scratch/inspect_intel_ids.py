import re

with open("scratch/section_intelligence_view.html", "r", encoding="utf-8") as f:
    text = f.read()

ids = re.findall(r'id="([^"]+)"', text)
print("Total IDs:", len(ids))
print("First 40 IDs:", ids[:40])
