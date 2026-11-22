import re
from pathlib import Path

t = Path(r"C:\Users\DAKSH\Desktop\land shield ai\frontend\index.html").read_text(encoding="utf-8")
# last script block is the app engine
parts = t.split("<script>")
script = parts[-1]
ids = sorted(set(re.findall(r"getElementById\('([^']+)'\)", script)))
print("COUNT", len(ids))
for i in ids:
    print(i)
