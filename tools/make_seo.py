#!/usr/bin/env python3
"""Build static, crawlable guide pages (one per collectible type) in English and Arabic,
plus sitemap.xml + robots.txt.

Reads the data arrays straight out of tools/master.html so the pages never drift from the app.
English pages live at /<slug>/, Arabic at /ar/<slug>/ (hreflang-linked).
Run from the repo root:  python3 tools/make_seo.py
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://gta6platinum.github.io"
M = open(os.path.join(ROOT, "tools/master.html"), encoding="utf-8").read()


def grab(name):
    i = M.index("var " + name + "=") + len(name) + 5
    return json.JSONDecoder().raw_decode(M[i:])[0]


FULL, TROPHIES, CARDS, MIS, WAINK, CHAPI, GARAGES, IMGS, IMGSUB, SETS, DT = [
    grab(k) for k in ["FULL", "TROPHIES", "CARDS", "MIS", "WAINK", "CHAPI", "GARAGES", "IMGS", "IMGSUB", "SETS", "DT"]]
AR = DT["ar"]
TODAY = datetime.date.today().isoformat()
e = lambda s: html.escape(str(s), quote=True)

CSS = """*{box-sizing:border-box}body{margin:0;background:#121820;color:#e8edf2;font:16px/1.6 Overpass,"IBM Plex Sans Arabic",system-ui,-apple-system,Segoe UI,Tahoma,sans-serif}
a{color:#f2a93b}header{background:#0f6b46;padding:18px 20px;display:flex;justify-content:space-between;gap:12px}header a{color:#fff;text-decoration:none;font-weight:700}
main{max-width:860px;margin:0 auto;padding:22px 18px 60px}h1{font-size:30px;line-height:1.25;margin:8px 0 10px}
h2{font-size:21px;margin:30px 0 8px;border-bottom:2px solid #f2a93b;padding-bottom:4px}.lead{color:#b8c4cf;font-size:17px}
.cta{display:inline-block;background:#f2a93b;color:#121820;font-weight:800;padding:12px 18px;border-radius:8px;text-decoration:none;margin:10px 0 4px}
ol,ul{padding-inline-start:22px}li{margin:10px 0;padding-bottom:8px;border-bottom:1px solid #2b3846}li b{color:#fff}
.d{color:#b8c4cf;display:block}.pin{font-size:14px;margin-inline-end:10px}.tag{font-size:13px;color:#121820;background:#b8c4cf;border-radius:4px;padding:1px 6px;margin-inline-start:6px}
.th{display:block;margin:6px 0}.th img{width:200px;max-width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:6px;border:1px solid #2b3846;background:#0c1117}
.th span{display:block;font-size:12px;color:#8b98a5}nav.more{margin-top:40px;font-size:15px}nav.more a{display:inline-block;margin:4px 10px 4px 0}
footer{color:#8b98a5;font-size:13px;text-align:center;padding:20px}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #2b3846;padding:8px;text-align:start;vertical-align:top}"""

THUMB_JS = """<script>(function(){var C={};function ch(id){var m=/^(.*)-(\\d+)$/.exec(id);return m[1]+'_'+Math.floor(+m[2]/40)}
var io=new IntersectionObserver(function(es){es.forEach(function(x){if(!x.isIntersecting)return;io.unobserve(x.target);var im=x.target,id=im.getAttribute('data-tid'),c=ch(id);
(C[c]=C[c]||fetch('/thumbs/'+c+'.json').then(function(r){return r.json()})).then(function(d){if(d[id])im.src='data:image/webp;base64,'+d[id];else im.parentNode.style.display='none'}).catch(function(){im.parentNode.style.display='none'})})},{rootMargin:'400px'});
document.querySelectorAll('img[data-tid]').forEach(function(i){io.observe(i)})})()</script>"""

UI = {
    "en": dict(pin="📍 Map pin", photo="Photo: ", track="✅ Track these in the free checklist →",
               saves="The checklist saves your progress on your phone, works in English, Arabic and Spanish, and has every other collectible too.",
               open="✅ Open the full checklist →", more="More GTA 6 guides:", home="Home", updated="Updated",
               credit="Locations and photos credited to their GTABase contributors · Free, no ads", other="العربية", cards="cards",
               chapter="Chapter %s", trophy="Trophy", grade="Grade", how="How to unlock", garage="Garage", loc="Location", price="Price",
               get="How to get it", all_guides="All guides"),
    "ar": dict(pin="📍 مكانه على الخريطة", photo="تصوير: ", track="✅ تابعها في القائمة المجانية ←",
               saves="القائمة تحفظ تقدّمك على جوالك، وتشتغل بالعربي والإنجليزي والإسباني، وفيها كل المقتنيات الثانية.",
               open="✅ افتح القائمة الكاملة ←", more="أدلة GTA 6 ثانية:", home="الرئيسية", updated="آخر تحديث",
               credit="الأماكن والصور بأسماء أصحابها في GTABase · مجاني وبدون إعلانات", other="English", cards="بطاقة",
               chapter="الفصل %s", trophy="التروفي", grade="الدرجة", how="طريقة الحصول عليه", garage="الكراج", loc="المكان", price="السعر",
               get="كيف تاخذه", all_guides="كل الأدلة"),
}
GR = {"en": {"P": "Platinum", "G": "Gold", "S": "Silver", "B": "Bronze"},
      "ar": {"P": "بلاتيني", "G": "ذهبي", "S": "فضي", "B": "برونزي"}}
REG = {"en": {"VC": "Vice City", "VB": "Vice Beach", "VD": "Vice-Dale County", "MA": "Mariana County", "LE": "Leonard County", "KE": "Kelly County", "LU": "Lummox County", "UN": ""},
       "ar": {"VC": "Vice City", "VB": "Vice Beach", "VD": "مقاطعة Vice-Dale", "MA": "مقاطعة Mariana", "LE": "مقاطعة Leonard", "KE": "مقاطعة Kelly", "LU": "مقاطعة Lummox", "UN": ""}}


def sub(group, name):
    for g in FULL:
        if g[0].endswith(group) or g[0] == group:
            for s in g[1]:
                if s[0] == name:
                    return s[1]
    raise KeyError(group + "/" + name)


# slug, group, sub, en keyword, en lead, ar keyword, ar lead
SIMPLE = [
    ("meteorites", "Luxury watches, treasure & hidden items", "Meteorites", "Meteorite Locations",
     "Every meteorite in GTA 6 with its exact map pin. Meteorites don't count toward 100% completion, but they sell for good money early on.",
     "أماكن النيازك", "كل نيزك في GTA 6 ومكانه بالضبط على الخريطة. النيازك ما تنحسب في الـ 100%، بس تنباع بفلوس حلوة من بدري."),
    ("luxury-watches", "Luxury watches, treasure & hidden items", "Luxury Watches", "Luxury Watch Locations",
     "All luxury watches in GTA 6 and where to find them — several are inside safes or are key valuables in robberies like Hit Kingpin Bowling.",
     "أماكن الساعات الفاخرة", "كل الساعات الفاخرة في GTA 6 ووين تلقاها. بعضها داخل خزنات، وبعضها من الغنائم الأساسية في سرقات مثل Hit Kingpin Bowling."),
    ("hidden-packages", "Luxury watches, treasure & hidden items", "Hidden Package", "Hidden Package Locations",
     "Every hidden package in GTA 6, each with a map pin so you can grab them in order.",
     "أماكن المخابئ (Hidden Packages)", "كل المخابئ في GTA 6، ولكل واحد دبوسه على الخريطة عشان تجمعها بالترتيب."),
    ("cocaine-flamingos", "Luxury watches, treasure & hidden items", "Cocaine Flamingos", "Cocaine Flamingo Locations",
     "Every mapped cocaine flamingo in GTA 6. Shoot the ones with a black-and-white beak to get the cocaine inside — 100 of the 125 count for 100% completion, and 50 unlock the Inflatable Flamingo cheat.",
     "أماكن فلامنقو الكوكايين", "كل فلامنقو كوكايين مثبّت في GTA 6. اضرب اللي منقاره أبيض وأسود ويطلع لك الكوكايين. تحتاج 100 من 125 للـ 100%، و50 تفتح لك غش Inflatable Flamingo."),
    ("scoop-containers", "Luxury watches, treasure & hidden items", "SCOOP Containers", "SCOOP Container Locations",
     "All SCOOP containers in GTA 6 with exact map pins.",
     "أماكن حاويات SCOOP", "كل حاويات SCOOP في GTA 6 مع أماكنها بالضبط."),
    ("unique-weapons", "Unique weapons", "Unique Weapons", "Unique Weapon Locations",
     "Every unique (collectible) weapon in GTA 6. Weapons count toward 100% completion, so this list is worth clearing.",
     "أماكن الأسلحة الفريدة", "كل الأسلحة الفريدة (المقتنيات) في GTA 6. الأسلحة تنحسب في الـ 100%، فتستاهل تخلصها."),
    ("standout-vehicles", "Standout vehicles", "Standout Vehicles", "Standout Vehicle Locations",
     "Every standout vehicle in GTA 6 with where it spawns. Discovering vehicles also unlocks the Whip It Good trophy.",
     "أماكن السيارات المميزة", "كل سيارة مميزة في GTA 6 ووين تطلع. اكتشاف السيارات يفتح لك تروفي Whip It Good."),
    ("magazines-and-books", "Magazines, books & comics", "Magazines & Books", "Magazine & Book Locations",
     "All magazines and books in GTA 6 with map pins, including the ones that become missable when a chapter ends.",
     "أماكن المجلات والكتب", "كل المجلات والكتب في GTA 6 مع أماكنها، ومنها اللي تفوتك إذا خلص الفصل."),
    ("stunt-jumps", "Stunts", "Stunt Jumps", "Stunt Jump Locations",
     "Every stunt jump in GTA 6 with its map pin.", "أماكن القفزات الاستعراضية", "كل قفزة استعراضية في GTA 6 مع مكانها."),
    ("under-the-bridge", "Stunts", "Under the Bridge", "Under the Bridge Locations",
     "Every Under the Bridge challenge in GTA 6 with exact map pins.", "أماكن تحديات تحت الجسر", "كل تحديات Under the Bridge في GTA 6 مع أماكنها."),
    ("knife-flights", "Stunts", "Knife Flights", "Knife Flight Locations",
     "All knife flights in GTA 6 with map pins.", "أماكن الطيران بين المباني (Knife Flights)", "كل تحديات Knife Flight في GTA 6 مع أماكنها."),
    ("base-jumps", "Stunts", "BASE Jumps", "BASE Jump Locations",
     "Every BASE jump in GTA 6 with map pins.", "أماكن قفزات BASE", "كل قفزات BASE في GTA 6 مع أماكنها."),
    ("races", "Races & ranges", "Races", "Race Locations",
     "Every race in GTA 6 with its start point.", "أماكن السباقات", "كل سباق في GTA 6 ومكان بدايته."),
    ("drone-races", "Races & ranges", "Drone Races", "Drone Race Locations",
     "All drone races in GTA 6 with map pins.", "أماكن سباقات الدرون", "كل سباقات الدرون في GTA 6 مع أماكنها."),
    ("banks", "Robberies", "Banks", "Bank Robbery Locations",
     "Every bank you can rob in GTA 6.", "أماكن البنوك اللي تنسرق", "كل بنك تقدر تسرقه في GTA 6."),
    ("illegal-operations", "Robberies", "Illegal Operations", "Illegal Operation (Gang Hit) Locations",
     "All illegal operations and gang hits in GTA 6, including the Kolt & Associates jobs from Chapter 2.",
     "أماكن العمليات غير القانونية", "كل العمليات غير القانونية وهجمات العصابات في GTA 6، ومنها عمليات Kolt & Associates في الفصل 2."),
]


def build(L):
    u = UI[L]
    tr = (lambda s: AR.get(s, s)) if L == "ar" else (lambda s: s)
    P = []

    def pin(id_):
        return '<a class="pin" href="https://www.gtabase.com/gta-6/map/#%s" target="_blank" rel="noopener">%s</a>' % (e(id_), u["pin"])

    def thumb(id_):
        if id_ not in IMGS:
            return ""
        who = IMGSUB[IMGS[id_]] or "GTABase"
        return '<span class="th"><img data-tid="%s" alt="%s" loading="lazy"><span>%s</span></span>' % (
            e(id_), e(id_), e(u["photo"] + who + ("" if who == "GTABase" else " / GTABase")))

    def items(lst):
        out = ["<ol>"]
        for it in lst:
            d = it[2] if len(it) > 2 and it[2] else ""
            out.append("<li><b>%s</b>%s%s%s</li>" % (e(it[1]), ('<span class="d">%s</span>' % e(tr(d))) if d else "", thumb(it[0]),
                                                     pin(it[0]) if not str(it[0]).startswith("?") else ""))
        out.append("</ol>")
        return "".join(out)

    def intro(lead):
        return '<p class="lead">%s</p><a class="cta" href="/">%s</a><p class="lead" style="font-size:15px">%s</p>' % (
            e(lead), u["track"], u["saves"])

    def add(slug, kw, h1, desc, body, lead):
        P.append((slug, kw, h1, desc, intro(lead) + body))

    for slug, grp, name, kw, lead, kwa, leada in SIMPLE:
        lst = sub(grp, name)
        n = len(lst)
        if L == "en":
            add(slug, kw, "All %d GTA 6 %s" % (n, kw),
                "GTA 6 %s — all %d with map pins and photos. Free GTA 6 checklist that saves your progress." % (kw, n), items(lst), lead)
        else:
            add(slug, kwa, "%s في GTA 6 — كل الـ %d" % (kwa, n),
                "%s في GTA 6: كل الـ %d مع مكانها على الخريطة وصورها. قائمة مجانية بالعربي تحفظ تقدّمك." % (kwa, n), items(lst), leada)

    hoops = [g for g in FULL if "Basketball" in g[0]][0][1][0][1]
    if L == "en":
        add("basketball-hoops", "Basketball Hoop Locations", "All %d GTA 6 Basketball Hoop Locations" % len(hoops),
            "All %d GTA 6 basketball hoops with map pins — you need 90 of 100 for 100%% completion." % len(hoops),
            items(hoops), "Every basketball hoop in GTA 6. You need 90 of the 100 for 100% completion.")
    else:
        add("basketball-hoops", "أماكن سلال كرة السلة", "أماكن سلال كرة السلة في GTA 6 — كل الـ %d" % len(hoops),
            "كل سلال كرة السلة في GTA 6 (%d) مع أماكنها. تحتاج 90 من 100 للـ 100%%." % len(hoops),
            items(hoops), "كل سلة كرة سلة في GTA 6. تحتاج 90 من الـ 100 للـ 100%.")

    mc = sub("Magazines, books & comics", "Comics") + sub("Magazines, books & comics", "Book Swaps")
    if L == "en":
        add("comics-and-book-swaps", "Comics & Book Swap Locations", "GTA 6 Comics & Book Swap Locations",
            "Every comic and book swap in GTA 6 with map pins.", items(mc), "All comics and book swaps in GTA 6.")
    else:
        add("comics-and-book-swaps", "أماكن القصص المصورة وتبادل الكتب", "أماكن القصص المصورة وتبادل الكتب في GTA 6",
            "كل القصص المصورة ونقاط تبادل الكتب في GTA 6 مع أماكنها.", items(mc), "كل القصص المصورة ونقاط تبادل الكتب في GTA 6.")

    # WAiNK
    sep = "، " if L == "ar" else ", "
    wb = []
    for sect, rows in WAINK.items():
        wb.append("<h2>%s</h2><ol>" % e(tr(sect)))
        for r in rows:
            parts = [tr(r[1]) if len(r) > 1 else "", REG[L].get(r[2], r[2]) if len(r) > 2 else ""]
            wb.append("<li><b>%s</b><span class=\"d\">%s</span></li>" % (e(r[0]), e(sep.join(x for x in parts if x))))
        wb.append("</ol>")
    if L == "en":
        add("waink", "WAiNK Photo Locations", "All GTA 6 WAiNK Photo Locations (Landmarks, Curiosities, Sculptures)",
            "Every WAiNK landmark, curiosity, sculpture and No Flusher tag in GTA 6 — the full photo-collectible list.",
            "".join(wb), "The WAiNK photo collectibles in GTA 6: landmarks, curiosities, sculptures and No Flusher tags.")
    else:
        add("waink", "أماكن صور WAiNK", "كل أماكن صور WAiNK في GTA 6 (المعالم والغرائب والمنحوتات)",
            "كل معالم WAiNK وغرائبها ومنحوتاتها وعلامات No Flusher في GTA 6 — قائمة صور المقتنيات كاملة.",
            "".join(wb), "مقتنيات WAiNK في GTA 6: المعالم والغرائب والمنحوتات وعلامات No Flusher.")

    # Cards
    cb, by = [], {}
    for c in CARDS:
        by.setdefault(c[0], []).append(c)
    for si, s in enumerate(SETS):
        rows = by.get(si, [])
        if not rows:
            continue
        cb.append("<h2>%s <span class=\"tag\">%d %s</span></h2>" % (e(s[0]), s[1], u["cards"]))
        if len(s) > 2:
            cb.append('<p class="d">%s</p>' % e(tr(s[2])))
        cb.append("<ol>")
        for c in rows:
            rg = REG[L].get(c[3], c[3]) if c[3] else ""
            cb.append("<li><b>%s</b>%s<span class=\"d\">%s%s</span></li>" % (
                e(c[1]), (' <span class="tag">%s</span>' % e(tr(c[2]))) if c[2] else "", e(tr(c[4])), (" — " + e(rg)) if rg else ""))
        cb.append("</ol>")
    nc, nl = sum(s[1] for s in SETS), len(CARDS)
    if L == "en":
        add("collectible-cards", "Collectible Card Locations", "GTA 6 Collectible Card Locations — All %d Sets (%d of %d Cards Mapped)" % (len(SETS), nl, nc),
            "Every GTA 6 collectible card by set — %d cards across %d sets, including the missable Starlet Motel cards." % (nc, len(SETS)),
            "".join(cb), "GTA 6 has %d collectible cards across %d sets. %d are mapped so far — the list grows as players find the rest. Some cards are missable: the Starlet Motel ones lock after Chapter 2." % (nc, len(SETS), nl))
    else:
        add("collectible-cards", "أماكن البطاقات", "أماكن بطاقات GTA 6 — كل الـ %d مجموعة (%d من %d بطاقة معروفة)" % (len(SETS), nl, nc),
            "كل بطاقات GTA 6 حسب المجموعة — %d بطاقة في %d مجموعة، ومنها بطاقات Starlet Motel اللي تفوتك." % (nc, len(SETS)),
            "".join(cb), "في GTA 6 فيه %d بطاقة في %d مجموعة. المعروف مكانه للحين %d، والقائمة تكبر كل ما لقى اللاعبين الباقي. بعض البطاقات تفوتك: بطاقات Starlet Motel تنقفل بعد الفصل 2." % (nc, len(SETS), nl))

    # Trophies
    tb = ["<table><tr><th>%s</th><th>%s</th><th>%s</th></tr>" % (u["trophy"], u["grade"], u["how"])]
    for t in TROPHIES:
        tb.append("<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>" % (e(t[0]), GR[L].get(t[1], t[1]), e(tr(t[3])) if len(t) > 3 else ""))
    tb.append("</table>")
    if L == "en":
        add("trophies", "Trophy List", "GTA 6 Trophy List — All %d Trophies & How to Unlock Them" % len(TROPHIES),
            "The full GTA 6 trophy list: all %d trophies with how to unlock each one, including the hidden and missable ones." % len(TROPHIES),
            "".join(tb), "Every GTA 6 trophy and how to get it. Use the checklist to tick them off as you go.")
    else:
        add("trophies", "قائمة التروفيات", "قائمة تروفيات GTA 6 — كل الـ %d تروفي وطريقة الحصول عليها" % len(TROPHIES),
            "قائمة تروفيات GTA 6 كاملة بالعربي: كل الـ %d تروفي وطريقة كل واحد، ومنها المخفية واللي تفوتك." % len(TROPHIES),
            "".join(tb), "كل تروفي في GTA 6 وطريقة الحصول عليه. علّم عليها في القائمة وأنت تلعب.")

    # Missables
    mb = []
    for ch in sorted(CHAPI, key=int):
        mb.append("<h2>%s</h2><ol>" % (u["chapter"] % ch))
        for r in CHAPI[ch]:
            mb.append("<li><b>%s</b><span class=\"d\">%s</span>%s</li>" % (
                e(tr(r[0])), e(tr(r[1])), pin(r[2]) if len(r) > 2 and r[2] and not r[2].startswith("?") else ""))
        mb.append("</ol>")
    if L == "en":
        add("missables", "Missables by Chapter", "GTA 6 Missables — Everything You Can Miss, Chapter by Chapter",
            "Every missable in GTA 6 by chapter: cards, meditations, garages and trophies that lock forever once a chapter ends.",
            "".join(mb), "GTA 6 has no mission replay, so some things are gone for good once you move on. Here is everything to clear before each chapter ends.")
    else:
        add("missables", "الأشياء اللي تفوتك", "الأشياء اللي تفوتك في GTA 6 — فصل بفصل",
            "كل شي يفوتك في GTA 6 حسب الفصل: بطاقات وتأملات وكراجات وتروفيات تنقفل للأبد إذا خلص الفصل.",
            "".join(mb), "GTA 6 ما فيه إعادة مهمات، فبعض الأشياء تروح عليك للأبد إذا كملت. هذا كل شي لازم تخلصه قبل نهاية كل فصل.")

    # Story missions
    sb = []
    for ch in MIS:
        sb.append("<h2>%s</h2><ol>" % e(tr(ch[0])))
        sb.extend("<li><b>%s</b></li>" % e(x) for x in ch[1])
        sb.append("</ol>")
    nm = sum(len(c[1]) for c in MIS)
    if L == "en":
        add("story-missions", "Story Mission List", "GTA 6 Story Missions — Full List of All %d Main Missions in Order" % nm,
            "The full list of GTA 6 story missions in order, chapter by chapter (%d missions)." % nm,
            "".join(sb), "Every main story mission in GTA 6, in order, split by chapter.")
    else:
        add("story-missions", "قائمة مهمات القصة", "مهمات قصة GTA 6 — القائمة الكاملة لكل الـ %d مهمة بالترتيب" % nm,
            "قائمة مهمات قصة GTA 6 كاملة بالترتيب، فصل بفصل (%d مهمة)." % nm,
            "".join(sb), "كل مهمات القصة الرئيسية في GTA 6 بالترتيب، مقسّمة حسب الفصل.")

    # Garages
    gb = ["<table><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>" % (u["garage"], u["loc"], u["price"], u["get"])]
    for g in GARAGES:
        gb.append("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            e(tr(g[0])), e(tr(g[1])), e(tr(g[2])), e(" — ".join(tr(x) for x in g[3:] if x))))
    gb.append("</table>")
    if L == "en":
        add("garages", "Garage Locations", "All GTA 6 Garages — Locations, Prices & How to Unlock",
            "Every garage in GTA 6 with location, price and how to unlock it. Each garage you buy adds parking space.",
            "".join(gb), "Every garage in GTA 6, what it costs and how to unlock it.")
    else:
        add("garages", "أماكن الكراجات", "كل كراجات GTA 6 — أماكنها وأسعارها وطريقة فتحها",
            "كل كراج في GTA 6 مع مكانه وسعره وطريقة فتحه. كل كراج تشتريه يزيد لك مكان سيارة.",
            "".join(gb), "كل كراج في GTA 6، كم سعره، وكيف تفتحه.")
    return P


def url(L, slug):
    return "%s/%s%s/" % (SITE, "ar/" if L == "ar" else "", slug)


def render(L, P, slug, kw, h1, desc, body):
    u = UI[L]
    me, other = url(L, slug), url("ar" if L == "en" else "en", slug)
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc, "inLanguage": L,
          "dateModified": TODAY, "mainEntityOfPage": me, "publisher": {"@type": "Organization", "name": "GTA Guide to Platinum", "url": SITE + "/"}}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "GTA Guide to Platinum", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": kw, "item": me}]}
    nav = '<nav class="more"><b>%s</b><br>%s</nav>' % (u["more"], "".join(
        '<a href="%s">%s</a>' % (url(L, s), e(k)) for s, k, *_ in P if s != slug))
    alt = '<link rel="alternate" hreflang="en" href="%s"><link rel="alternate" hreflang="ar" href="%s"><link rel="alternate" hreflang="x-default" href="%s">' % (
        url("en", slug), url("ar", slug), url("en", slug))
    return """<!DOCTYPE html><html lang="%s" dir="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s | GTA Guide to Platinum</title><meta name="description" content="%s"><link rel="canonical" href="%s">%s
<meta property="og:type" content="article"><meta property="og:url" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s">
<meta property="og:image" content="%s/og.png"><meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">%s</script><script type="application/ld+json">%s</script><style>%s</style></head><body>
<header><a href="/">🌴 GTA Guide to Platinum</a><a href="%s" hreflang="%s">%s</a></header><main><p style="font-size:14px;margin:0"><a href="/">%s</a> › %s</p><h1>%s</h1>%s%s
<a class="cta" href="/">%s</a></main>
<footer>%s %s · %s · <a href="/">gta6platinum.github.io</a></footer>%s</body></html>""" % (
        L, "rtl" if L == "ar" else "ltr", e(h1), e(desc), me, alt, me, e(h1), e(desc), SITE,
        json.dumps(ld, ensure_ascii=False), json.dumps(crumbs, ensure_ascii=False), CSS,
        other, "ar" if L == "en" else "en", u["other"], u["home"], e(kw), e(h1), body, nav, u["open"], u["updated"], TODAY, u["credit"], THUMB_JS)


urls = [SITE + "/"]
count = 0
for L in ("en", "ar"):
    P = build(L)
    base = os.path.join(ROOT, "ar") if L == "ar" else ROOT
    u = UI[L]
    hub = "<ul>" + "".join('<li><a href="%s"><b>%s</b></a><span class="d">%s</span></li>' % (url(L, s), e(h), e(dd)) for s, k, h, dd, b in P) + "</ul>"
    hub_intro = '<p class="lead">%s</p><a class="cta" href="/">%s</a>' % (
        e("Pick a guide below, or open the interactive checklist to track everything at once." if L == "en"
          else "اختر الدليل اللي تبيه، أو افتح القائمة التفاعلية وتابع كل شي مرة وحدة."), u["track"])
    title = "Every GTA 6 Collectible & Trophy Guide" if L == "en" else "كل أدلة GTA 6 بالعربي: المقتنيات والتروفيات"
    desc = ("All GTA 6 collectible location guides in one place — meteorites, cards, watches, weapons, WAiNK, trophies and missables." if L == "en"
            else "كل أدلة أماكن المقتنيات في GTA 6 بمكان واحد — النيازك والبطاقات والساعات والأسلحة وWAiNK والتروفيات والأشياء اللي تفوتك.")
    P.append(("guides", u["all_guides"], title, desc, hub_intro + hub))
    for slug, kw, h1, dsc, body in P:
        d = os.path.join(base, slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(render(L, P, slug, kw, h1, dsc, body))
        urls.append(url(L, slug))
        count += 1

open(os.path.join(ROOT, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (x, TODAY) for x in urls) + "</urlset>\n")
open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE)
print("pages:", count)
