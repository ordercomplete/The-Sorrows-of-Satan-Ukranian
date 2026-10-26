"""Commons search + pick candidates. Usage: python cs.py '<query>' [limit]"""
import sys, json
sys.path.insert(0, r"D:\GEN\The-Sorrows-of-Satan-Ukranian\Project_files\screenplay\casting\scripts")
from commons import search, score

q = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 15
recs = search(q, limit=limit)
recs.sort(key=score, reverse=True)
for r in recs[:limit]:
    print(score(r), "|", (r["title"] or "")[:90], "|", (r["datetime"] or "?")[:12], "|",
          (r["license"] or "?")[:20], "|", (r["image_title"] or "")[:70])
