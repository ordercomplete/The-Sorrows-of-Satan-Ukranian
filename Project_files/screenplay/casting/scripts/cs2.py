"""Search Commons with filetype filter; print candidates. Usage: python cs2.py '<query>' [limit]"""
import sys, json, re
sys.path.insert(0, r"D:\GEN\The-Sorrows-of-Satan-Ukranian\Project_files\screenplay\casting\scripts")
from commons import api

q = sys.argv[1] + ' filetype:bitmap'
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 12
d = api({"action":"query","generator":"search","gsrsearch": q,
         "gsrnamespace":"6","gsrlimit":str(limit),"prop":"imageinfo",
         "iiprop":"url|extmetadata|size|mime","iiurlwidth":"1200","format":"json"})
BAD = ["painting","lithograph","engraving","illustration","drawing","caricature","statue","sculpture","bust ","plaque"]
for p in (d.get("query") or {}).get("pages",{}).values():
    ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
    def g(k): return re.sub("<[^>]+>","",(em.get(k) or {}).get("value",""))
    text=" ".join([p.get("title",""),g("ImageTitle"),g("ImageDescription"),g("Categories")]).lower()
    bad = [b for b in BAD if b in text]
    yr = g("DateTimeOriginal") or g("DateTime")
    print(("BAD:"+",".join(bad)[:30]) if bad else "ok  ", "|", (p.get("title") or "")[:80],
          "|", yr[:14], "|", g("LicenseShortName")[:16], "|", ii.get("width"), "x", ii.get("height"))
