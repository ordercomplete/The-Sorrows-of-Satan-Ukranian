"""Wikimedia Commons helper for casting-photo research. Rate-limited (~1 req / 6s)."""
import json, time, urllib.parse, urllib.request, pathlib

UA = {"User-Agent": "Hermes-casting-research/1.0 (casting refs project; contact: local)"}
API = "https://commons.wikimedia.org/w/api.php"
LAST = [0.0]

def _throttle():
    d = time.time() - LAST[0]
    if d < 10.0:
        time.sleep(10.0 - d)
    LAST[0] = time.time()

def api(params: dict):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(5):
        _throttle()
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                time.sleep(15 * (attempt + 1))
                continue
            raise

def search(query, limit=20):
    """File-namespace search; returns list of pageinfo dicts w/ extmetadata."""
    d = api({
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime", "iiurlwidth": "1200", "format": "json",
    })
    pages = (d.get("query") or {}).get("pages") or {}
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata") or {}
        def g(k): return (em.get(k) or {}).get("value", "")
        out.append({
            "title": p.get("title"),
            "descriptionurl": p.get("descriptionurl") or ii.get("descriptionurl", ""),
            "thumburl": ii.get("thumburl", ""), "url": ii.get("url", ""),
            "width": ii.get("width"), "height": ii.get("height"), "mime": ii.get("mime"),
            "image_title": g("ImageTitle"), "image_desc": g("ImageDescription"),
            "artist": g("Artist"), "license": g("LicenseShortName"),
            "datetime": g("DateTimeOriginal") or g("DateTime"),
            "categories": g("Categories"), "file_size": ii.get("size"),
        })
    return out

BAD = ["painting", "lithograph", "engraving", "illustration", "drawing",
       "cartoon", "sketch of", "poster,", "map", "sculpture", "statue",
       "stained glass", "caricature"]
GOOD = ["photograph", "photo", "carte de visite", "cabinet card", "albumen",
        "portrait study", "photogravure", "gelatin silver", "carte-de-visite",
        "portraits", "portrait of", "studio portrait", "phototype"]

def score(rec):
    text = " ".join(str(rec.get(k, "")) for k in ("title", "image_title", "image_desc", "categories")).lower()
    if any(b in text for b in BAD):
        return -99
    s = 0
    for gword in GOOD:
        if gword in text:
            s += 2
    import re
    yrs = re.findall(r"\b(189[0-9]|190[0-5])\b", text)
    if yrs:
        s += 3
    if "portrait" in text:
        s += 1
    return s

def download(url, dest):
    _throttle()
    req = urllib.request.Request(url, headers=UA)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        while True:
            b = r.read(1 << 16)
            if not b:
                break
            f.write(b)
    return dest.stat().st_size
