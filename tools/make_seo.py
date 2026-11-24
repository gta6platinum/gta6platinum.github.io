#!/usr/bin/env python3
"""Build static, crawlable guide pages (one per collectible type) + sitemap.xml + robots.txt.

Reads the data arrays straight out of tools/master.html so the pages never drift from the app.
Run from the repo root:  python3 tools/make_seo.py
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://gta6platinum.github.io"
M = open(os.path.join(ROOT, "tools/master.html"), encoding="utf-8").read()


def grab(name):
    i = M.index("var " + name + "=") + len(name) + 5
    return json.JSONDecoder().raw_decode(M[i:])[0]


FULL, TROPHIES, CARDS, MIS, WAINK, CHAPI, GARAGES, IMGS, IMGSUB, SETS = [
    grab(k) for k in ["FULL", "TROPHIES", "CARDS", "MIS", "WAINK", "CHAPI", "GARAGES", "IMGS", "IMGSUB", "SETS"]]
TODAY = datetime.date.today().isoformat()
e = lambda s: html.escape(str(s), quote=True)

CSS = """*{box-sizing:border-box}body{margin:0;background:#121820;color:#e8edf2;font:16px/1.6 Overpass,system-ui,-apple-system,Segoe UI,sans-serif}
a{color:#f2a93b}header{background:#0f6b46;padding:18px 20px}header a{color:#fff;text-decoration:none;font-weight:700}
main{max-width:860px;margin:0 auto;padding:22px 18px 60px}h1{font-size:30px;line-height:1.2;margin:8px 0 10px}
h2{font-size:21px;margin:30px 0 8px;border-bottom:2px solid #f2a93b;padding-bottom:4px}.lead{color:#b8c4cf;font-size:17px}
.cta{display:inline-block;background:#f2a93b;color:#121820;font-weight:800;padding:12px 18px;border-radius:8px;text-decoration:none;margin:10px 0 4px}
ol,ul{padding-left:22px}li{margin:10px 0;padding-bottom:8px;border-bottom:1px solid #2b3846}li b{color:#fff}
.d{color:#b8c4cf;display:block}.pin{font-size:14px;margin-right:10px}.tag{font-size:13px;color:#121820;background:#b8c4cf;border-radius:4px;padding:1px 6px;margin-left:6px}
.th{display:block;margin:6px 0}.th img{width:200px;max-width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:6px;border:1px solid #2b3846;background:#0c1117}
.th span{display:block;font-size:12px;color:#8b98a5}nav.more{margin-top:40px;font-size:15px}nav.more a{display:inline-block;margin:4px 10px 4px 0}
footer{color:#8b98a5;font-size:13px;text-align:center;padding:20px}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #2b3846;padding:8px;text-align:left;vertical-align:top}"""

THUMB_JS = """<script>(function(){var C={};function ch(id){var m=/^(.*)-(\\d+)$/.exec(id);return m[1]+'_'+Math.floor(+m[2]/40)}
var io=new IntersectionObserver(function(es){es.forEach(function(x){if(!x.isIntersecting)return;io.unobserve(x.target);var im=x.target,id=im.getAttribute('data-tid'),c=ch(id);
(C[c]=C[c]||fetch('/thumbs/'+c+'.json').then(function(r){return r.json()})).then(function(d){if(d[id])im.src='data:image/webp;base64,'+d[id];else im.parentNode.style.display='none'}).catch(function(){im.parentNode.style.display='none'})})},{rootMargin:'400px'});
document.querySelectorAll('img[data-tid]').forEach(function(i){io.observe(i)})})()</script>"""

PAGES = []  # (slug, title, h1, desc, body_html)


def pin(id_):
    return '<a class="pin" href="https://www.gtabase.com/gta-6/map/#%s" target="_blank" rel="noopener">📍 Map pin</a>' % e(id_)


def thumb(id_):
    if id_ not in IMGS:
        return ""
    who = IMGSUB[IMGS[id_]] or "GTABase"
    credit = "Photo: " + who + ("" if who == "GTABase" else " / GTABase")
    return '<span class="th"><img data-tid="%s" alt="%s" loading="lazy"><span>%s</span></span>' % (e(id_), e(id_), e(credit))


def item_list(items, ordered=True):
    tag = "ol" if ordered else "ul"
    out = ["<%s>" % tag]
    for it in items:
        id_, name = it[0], it[1]
        desc = it[2] if len(it) > 2 and it[2] else ""
        out.append("<li><b>%s</b>%s%s%s</li>" % (
            e(name), ('<span class="d">%s</span>' % e(desc)) if desc else "", thumb(id_),
            pin(id_) if not str(id_).startswith("?") else ""))
    out.append("</%s>" % tag)
    return "".join(out)


def add(slug, keyword, h1, desc, body, lead):
    PAGES.append((slug, keyword, h1, desc, lead + body))


def sub(group, name):
    for g in FULL:
        if g[0].endswith(group) or g[0] == group:
            for s in g[1]:
                if s[0] == name:
                    return s[1]
    raise KeyError(group + "/" + name)


INTRO = ('<p class="lead">%s</p><a class="cta" href="/">✅ Track these in the free checklist →</a>'
         '<p class="lead" style="font-size:15px">The checklist saves your progress on your phone, works in English, Arabic and Spanish, and has every other collectible too.</p>')

# --- simple FULL-based pages -------------------------------------------------
SIMPLE = [
    ("meteorites", "Luxury watches, treasure & hidden items", "Meteorites", "Meteorite Locations",
     "Every meteorite in GTA 6 with its exact map pin. Meteorites don't count toward 100% completion, but they sell for good money early on."),
    ("luxury-watches", "Luxury watches, treasure & hidden items", "Luxury Watches", "Luxury Watch Locations",
     "All luxury watches in GTA 6 and where to find them — several are inside safes or are key valuables in robberies like Hit Kingpin Bowling."),
    ("hidden-packages", "Luxury watches, treasure & hidden items", "Hidden Package", "Hidden Package Locations",
     "Every hidden package in GTA 6, each with a map pin so you can grab them in order."),
    ("cocaine-flamingos", "Luxury watches, treasure & hidden items", "Cocaine Flamingos", "Cocaine Flamingo Locations",
     "Every mapped cocaine flamingo in GTA 6. Shoot the ones with a black-and-white beak to get the cocaine inside — 100 of the 125 count for 100% completion, and 50 unlock the Inflatable Flamingo cheat."),
    ("scoop-containers", "Luxury watches, treasure & hidden items", "SCOOP Containers", "SCOOP Container Locations",
     "All SCOOP containers in GTA 6 with exact map pins."),
    ("unique-weapons", "Unique weapons", "Unique Weapons", "Unique Weapon Locations",
     "Every unique (collectible) weapon in GTA 6. Weapons count toward 100% completion, so this list is worth clearing."),
    ("standout-vehicles", "Standout vehicles", "Standout Vehicles", "Standout Vehicle Locations",
     "Every standout vehicle in GTA 6 with where it spawns. Discovering vehicles also unlocks the Whip It Good trophy."),
    ("magazines-and-books", "Magazines, books & comics", "Magazines & Books", "Magazine & Book Locations",
     "All magazines and books in GTA 6 with map pins, including the ones that become missable when a chapter ends."),
    ("stunt-jumps", "Stunts", "Stunt Jumps", "Stunt Jump Locations",
     "Every stunt jump in GTA 6 with its map pin."),
    ("under-the-bridge", "Stunts", "Under the Bridge", "Under the Bridge Locations",
     "Every Under the Bridge challenge in GTA 6 with exact map pins."),
    ("knife-flights", "Stunts", "Knife Flights", "Knife Flight Locations",
     "All knife flights in GTA 6 with map pins."),
    ("base-jumps", "Stunts", "BASE Jumps", "BASE Jump Locations",
     "Every BASE jump in GTA 6 with map pins."),
    ("races", "Races & ranges", "Races", "Race Locations",
     "Every race in GTA 6 with its start point."),
    ("drone-races", "Races & ranges", "Drone Races", "Drone Race Locations",
     "All drone races in GTA 6 with map pins."),
    ("banks", "Robberies", "Banks", "Bank Robbery Locations",
     "Every bank you can rob in GTA 6."),
    ("illegal-operations", "Robberies", "Illegal Operations", "Illegal Operation (Gang Hit) Locations",
     "All illegal operations and gang hits in GTA 6, including the Kolt & Associates jobs from Chapter 2."),
]
for slug, grp, name, kw, lead in SIMPLE:
    items = sub(grp, name)
    n = len(items)
    h1 = "All %d GTA 6 %s" % (n, kw)
    add(slug, kw, h1, "%s — all %d with map pins and photos. Free GTA 6 checklist that saves your progress." % (h1.replace("All %d " % n, ""), n),
        item_list(items), INTRO % e(lead))

# basketball hoops (single sub with long name)
hoops = [g for g in FULL if "Basketball" in g[0]][0][1][0][1]
add("basketball-hoops", "Basketball Hoop Locations", "All %d GTA 6 Basketball Hoop Locations" % len(hoops),
    "All %d GTA 6 basketball hoops with map pins — you need 90 of 100 for 100%% completion." % len(hoops),
    item_list(hoops), INTRO % "Every basketball hoop in GTA 6. You need 90 of the 100 for 100% completion.")

# magazines+comics+book swaps already partly; comics small → fold into one page
mc = sub("Magazines, books & comics", "Comics") + sub("Magazines, books & comics", "Book Swaps")
add("comics-and-book-swaps", "Comics & Book Swap Locations", "GTA 6 Comics & Book Swap Locations",
    "Every comic and book swap in GTA 6 with map pins.", item_list(mc), INTRO % "All comics and book swaps in GTA 6.")

# --- WAiNK ---------------------------------------------------------------------
REG = {"VC": "Vice City", "VB": "Vice Beach", "VD": "Vice-Dale County", "MA": "Mariana County", "LE": "Leonard County", "KE": "Kelly County", "LU": "Lummox County", "UN": ""}
wb = []
total = 0
for sect, rows in WAINK.items():
    wb.append("<h2>%s</h2><ol>" % e(sect))
    for r in rows:
        total += 1
        wb.append("<li><b>%s</b><span class=\"d\">%s</span></li>" % (e(r[0]), e(", ".join(x for x in [r[1] if len(r) > 1 else "", REG.get(r[2], r[2]) if len(r) > 2 else ""] if x))))
    wb.append("</ol>")
add("waink", "WAiNK Photo Locations", "All GTA 6 WAiNK Photo Locations (Landmarks, Curiosities, Sculptures)",
    "Every WAiNK landmark, curiosity, sculpture and No Flusher tag in GTA 6 — the full photo-collectible list.",
    "".join(wb), INTRO % "The WAiNK photo collectibles in GTA 6: landmarks, curiosities, sculptures and No Flusher tags.")

# --- Cards -------------------------------------------------------------------
cb = []
by = {}
for c in CARDS:
    by.setdefault(c[0], []).append(c)
for si, s in enumerate(SETS):
    rows = by.get(si, [])
    if not rows:
        continue
    cb.append("<h2>%s <span class=\"tag\">%d cards</span></h2>" % (e(s[0]), s[1]))
    if len(s) > 2:
        cb.append('<p class="d">%s</p>' % e(s[2]))
    cb.append("<ol>")
    for c in rows:
        cb.append("<li><b>%s</b>%s<span class=\"d\">%s%s</span></li>" % (
            e(c[1]), (' <span class="tag">%s</span>' % e(c[2])) if c[2] else "", e(c[4]),
            (" — " + e(REG.get(c[3], c[3]))) if c[3] else ""))
    cb.append("</ol>")
ncards = sum(s[1] for s in SETS)
nlisted = len(CARDS)
add("collectible-cards", "Collectible Card Locations", "GTA 6 Collectible Card Locations — All %d Sets (%d of %d Cards Mapped)" % (len(SETS), nlisted, ncards),
    "Every GTA 6 collectible card by set — %d cards across %d sets, including the missable Starlet Motel cards." % (ncards, len(SETS)),
    "".join(cb), INTRO % ("GTA 6 has %d collectible cards across %d sets. %d are mapped so far — the list grows as players find the rest. Some cards are missable: the Starlet Motel ones lock after Chapter 2." % (ncards, len(SETS), nlisted)))

# --- Trophies ----------------------------------------------------------------
GR = {"P": "Platinum", "G": "Gold", "S": "Silver", "B": "Bronze"}
tb = ["<table><tr><th>Trophy</th><th>Grade</th><th>How to unlock</th></tr>"]
for t in TROPHIES:
    tb.append("<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>" % (e(t[0]), GR.get(t[1], t[1]), e(t[3] if len(t) > 3 else "")))
tb.append("</table>")
add("trophies", "Trophy List", "GTA 6 Trophy List — All %d Trophies & How to Unlock Them" % len(TROPHIES),
    "The full GTA 6 trophy list: all %d trophies with how to unlock each one, including the hidden and missable ones." % len(TROPHIES),
    "".join(tb), INTRO % "Every GTA 6 trophy and how to get it. Use the checklist to tick them off as you go.")

# --- Missables per chapter ---------------------------------------------------
mb = []
for ch in sorted(CHAPI, key=int):
    mb.append("<h2>Chapter %s</h2><ol>" % ch)
    for r in CHAPI[ch]:
        mb.append("<li><b>%s</b><span class=\"d\">%s</span>%s</li>" % (e(r[0]), e(r[1]), pin(r[2]) if len(r) > 2 and r[2] and not r[2].startswith("?") else ""))
    mb.append("</ol>")
add("missables", "Missables by Chapter", "GTA 6 Missables — Everything You Can Miss, Chapter by Chapter",
    "Every missable in GTA 6 by chapter: cards, meditations, garages and trophies that lock forever once a chapter ends.",
    "".join(mb), INTRO % "GTA 6 has no mission replay, so some things are gone for good once you move on. Here is everything to clear before each chapter ends.")

# --- Story missions ----------------------------------------------------------
sb = []
for ch in MIS:
    sb.append("<h2>%s</h2><ol>" % e(ch[0]))
    sb.extend("<li><b>%s</b></li>" % e(x) for x in ch[1])
    sb.append("</ol>")
nm = sum(len(c[1]) for c in MIS)
add("story-missions", "Story Mission List", "GTA 6 Story Missions — Full List of All %d Main Missions in Order" % nm,
    "The full list of GTA 6 story missions in order, chapter by chapter (%d missions)." % nm,
    "".join(sb), INTRO % "Every main story mission in GTA 6, in order, split by chapter.")

# --- Garages -----------------------------------------------------------------
gb = ["<table><tr><th>Garage</th><th>Location</th><th>Price</th><th>How to get it</th></tr>"]
for g in GARAGES:
    gb.append("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>" % (e(g[0]), e(g[1]), e(g[2]), e(" — ".join(x for x in g[3:] if x))))
gb.append("</table>")
add("garages", "Garage Locations", "All GTA 6 Garages — Locations, Prices & How to Unlock",
    "Every garage in GTA 6 with location, price and how to unlock it. Each garage you buy adds parking space.",
    "".join(gb), INTRO % "Every garage in GTA 6, what it costs and how to unlock it.")


# --- render ------------------------------------------------------------------
def nav(cur):
    return '<nav class="more"><b>More GTA 6 guides:</b><br>' + "".join(
        '<a href="/%s/">%s</a>' % (s, e(k)) for s, k, *_ in PAGES if s != cur) + "</nav>"


def page(slug, kw, h1, desc, body):
    url = "%s/%s/" % (SITE, slug)
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc,
          "dateModified": TODAY, "mainEntityOfPage": url, "publisher": {"@type": "Organization", "name": "GTA Guide to Platinum", "url": SITE + "/"}}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "GTA Guide to Platinum", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": kw, "item": url}]}
    return """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s | GTA Guide to Platinum</title><meta name="description" content="%s"><link rel="canonical" href="%s">
<meta property="og:type" content="article"><meta property="og:url" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s">
<meta property="og:image" content="%s/og.png"><meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">%s</script><script type="application/ld+json">%s</script><style>%s</style></head><body>
<header><a href="/">🌴 GTA Guide to Platinum</a></header><main><p style="font-size:14px;margin:0"><a href="/">Home</a> › %s</p><h1>%s</h1>%s%s
<a class="cta" href="/">✅ Open the full checklist →</a></main>
<footer>Updated %s · Locations and photos credited to their GTABase contributors · Free, no ads · <a href="/">gta6platinum.github.io</a></footer>%s</body></html>""" % (
        e(h1), e(desc), url, url, e(h1), e(desc), SITE, json.dumps(ld), json.dumps(crumbs), CSS, e(kw), e(h1), body, nav(slug), TODAY, THUMB_JS)


for slug, kw, h1, desc, body in PAGES:
    d = os.path.join(ROOT, slug)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(slug, kw, h1, desc, body))

# hub page
hub = "<ul>" + "".join('<li><a href="/%s/"><b>%s</b></a><span class="d">%s</span></li>' % (s, e(h), e(d)) for s, k, h, d, b in PAGES) + "</ul>"
os.makedirs(os.path.join(ROOT, "guides"), exist_ok=True)
PAGES_ALL = PAGES[:]
open(os.path.join(ROOT, "guides/index.html"), "w", encoding="utf-8").write(
    page("guides", "All guides", "Every GTA 6 Collectible & Trophy Guide", "All GTA 6 collectible location guides in one place — meteorites, cards, watches, weapons, WAiNK, trophies and missables.",
         INTRO % "Pick a guide below, or open the interactive checklist to track everything at once." + hub))

urls = [SITE + "/", SITE + "/guides/"] + ["%s/%s/" % (SITE, s) for s, *_ in PAGES]
open(os.path.join(ROOT, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (u, TODAY) for u in urls) + "</urlset>\n")
open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE)
print("pages:", len(PAGES) + 1)
for s, k, h, *_ in PAGES:
    print(" ", s, "—", h)
