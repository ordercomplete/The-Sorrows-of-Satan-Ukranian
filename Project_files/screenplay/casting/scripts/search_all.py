"""Search LOC PPOC + Wellcome for photo candidates per character. Saves JSON."""
import json, time, urllib.parse, urllib.request, pathlib, sys

UA = {"User-Agent": "Hermes-casting-research/1.0 (local film reference research)"}
OUT = pathlib.Path(r"D:\GEN\The-Sorrows-of-Satan-Ukranian\Project_files\screenplay\casting\scripts\candidates")
OUT.mkdir(exist_ok=True)

QUERIES = {
 "geoffrey_tempest": [
   "portrait young man 1890s photographer",
   "Arthur Conan Doyle portrait",
   "writer portrait 1895 studio",
   "George du Maurier photograph",
   "Robert Louis Stevenson portrait 1893",
   "John Galsworthy portrait",
 ],
 "lady_sibyl_elton": [
   "princess dress ball 1895 photograph",
   "duchess portrait 1890s photograph",
   "aristocratic woman white dress 1895 photo",
   "Princess Victoria Alexandrine of Hesse portrait",
   "Daisy Cornwallis-West",
   "Lady Randolph Churchill photograph",
 ],
 "charlotte_fitzroy": ["pince-nez woman photograph 1890s", "middle aged lady portrait photograph 1895"],
 "mavis_clare": ["woman writer author portrait photograph 1895", "Marie Corelli portrait photograph", "poet woman portrait 1890s photograph"],
 "viscount_lynton": ["young nobleman portrait photograph 1893", "duke young man photograph 1895 polo", "Lord Albert Victor photograph"],
 "earl_of_elton": ["old gentleman whiskers portrait photograph 1895", "peer lord portrait photograph 1900 side-whiskers"],
 "lucio_rimanez": ["Italian prince portrait photograph 1895", "Count of Turin photograph", "Prince Thomas of Savoa"],
}

def get(url, params=None):
    if params:
        url = url + "&" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def loc(q, n=12):
    d = get("https://www.loc.gov/pictures/search/", {"q": q, "fo": "json", "results": str(n), "nd": "1"})
    out = []
    for it in (d.get("results") or [])[:n]:
        out.append({"src": "loc", "title": it.get("title",""), "date": it.get("date",""),
                    "created_published": it.get("created_published",""),
                    "medium": it.get("medium",""), "creator": it.get("creator_names",""),
                    "id": it.get("id",""), "link": it.get("link",""),
                    "reproduction": (it.get("reproductions") or [{}])[0].get("url","") if it.get("reproductions") else "",
                    "rights": it.get("rights_advisory",""), "notes": (it.get("notes") or [])[:2]})
    return out

def wellcome(q, n=12):
    d = get("https://api.wellcomecollection.org/v1/images", {"query": q, "size": str(n)})
    out = []
    for it in (d.get("results") or [])[:n]:
        ci = it.get("canonicalImageLinks") or {}
        out.append({"src": "wellcome", "title": it.get("title",""), "date": it.get("createdDate",{}).get("label",""),
                    "id": it.get("id",""), "license": (it.get("license") or {}).get("label",""),
                    "thumb": ci.get("thumbnail720",""), "sq": ci.get("square1024",""),
                    "workType": [t.get("label") for t in it.get("workType",[]) if isinstance(t,dict)]})
    return out

char = sys.argv[1] if len(sys.argv) > 1 else None
res = {}
for c, qs in QUERIES.items():
    if char and c != char: continue
    items = []
    for q in qs:
        try:
            items += loc(q)
        except Exception as e:
            print("LOC fail", c, q, e, file=sys.stderr)
        time.sleep(1.2)
        try:
            items += wellcome(q)
        except Exception as e:
            print("WLC fail", c, q, e, file=sys.stderr)
        time.sleep(1.2)
    res[c] = items
    (OUT / (c + ".json")).write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(c, len(items))
