import re
s=open('tools/master.html').read()
s=re.sub(r'<script type="application/json" id="state">.*?</script>','<script type="application/json" id="state">{"t":0,"s":{}}</script>',s,count=1,flags=re.S)
def rep(o,n):
    global s; assert s.count(o)>=1,o[:60]; s=s.replace(o,n)
rep('<title>GTA 6 — Platinum Workspace</title>','<title>GTA Guide to Platinum</title>')
rep('GTA 6 — Platinum Workspace 🌴','GTA Guide to Platinum 🌴')
rep('var SKEY="gta6plat_v1"','var SKEY="gta6guide_public_v1"')
rep('syncMsg="Saved on this device"','syncMsg="Your progress is saved in this browser on this device"')
rep('if(window.claude&&window.claude.use){window.claude.use("artifact")','if(false&&window.claude&&window.claude.use){window.claude.use("artifact")')
rep('var DEFCHAP="2";','var DEFCHAP="";')
rep('try{CHAP=localStorage.getItem("gta6chap")','try{CHAP=localStorage.getItem("gta6chap_pub")')
rep('try{localStorage.setItem("gta6chap",CHAP)','try{localStorage.setItem("gta6chap_pub",CHAP)')
rep("🗺️ opens the exact pin on GTABase.</footer>","🗺️ opens the exact pin on GTABase.<br>Map pins & the full checklist link to <a target=\"_blank\" rel=\"noopener\" href=\"https://www.gtabase.com/gta-6/map/\">GTABase.com</a> — go show them some love.<br>© 2026 Moe — GTA Guide to Platinum (our code, text & design). Map data © GTABase.com; videos © their creators. Official site & donation addresses: <a href=\"https://gta6platinum.github.io/\">gta6platinum.github.io</a>. Fan-made, not affiliated with Rockstar Games or GTABase.</footer>")
d=open('tools/donate.html').read()
i=s.rindex('</body>')
s=s[:i]+d+s[i:]
open('index.html','w').write(s)
# --- footer translations (public-only strings) ---
import json
s=open('index.html').read()
FT={"Map pins & the full checklist link to ":("دبابيس الخريطة والقائمة الكاملة مربوطة بموقع ","Los pines del mapa y la lista completa enlazan a "),
" — go show them some love.":(" — ادعموهم بزيارة."," — pásate a darles apoyo."),
"© 2026 Moe — GTA Guide to Platinum (our code, text & design). Map data © GTABase.com; videos © their creators. Official site & donation addresses: ":("© 2026 Moe — GTA Guide to Platinum (الكود والنصوص والتصميم لنا). بيانات الخريطة © GTABase.com؛ الفيديوهات © لأصحابها. الموقع الرسمي وعناوين التبرع: ","© 2026 Moe — GTA Guide to Platinum (nuestro código, textos y diseño). Datos del mapa © GTABase.com; videos © sus creadores. Sitio oficial y direcciones de donación: "),
". Fan-made, not affiliated with Rockstar Games or GTABase.":(". دليل من صنع معجب، غير تابع لـ Rockstar Games ولا GTABase.",". Hecho por fans, sin relación con Rockstar Games ni GTABase.")}
i=s.index('var DT=')+7;j=s.index(';\nfunction T(',i);DT=json.loads(s[i:j])
for k,(a,e) in FT.items():
    for kk in (k,k.strip()): DT['ar'][kk]=a if kk==k else a.strip(); DT['es'][kk]=e if kk==k else e.strip()
s=s[:i]+json.dumps(DT,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+s[j:]
open('index.html','w').write(s)

# --- share preview / SEO (public only) ---
s=open('index.html').read()
meta=('<meta name="description" content="Free GTA 6 platinum guide: every trophy, collectible, card, WAiNK spot, code and car, with a checklist that saves your progress. English, Arabic and Spanish.">'
 '<link rel="canonical" href="https://gta6platinum.github.io/">'
 '<meta property="og:type" content="website"><meta property="og:url" content="https://gta6platinum.github.io/">'
 '<meta property="og:title" content="GTA Guide to Platinum"><meta property="og:description" content="Every GTA 6 trophy, collectible, code and car in one free checklist — English · العربية · Español">'
 '<meta property="og:image" content="https://gta6platinum.github.io/og.png"><meta name="twitter:card" content="summary_large_image">'
 '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ctext y=%22.9em%22 font-size=%2290%22%3E%F0%9F%8F%86%3C/text%3E%3C/svg%3E">')
if 'og:image' not in s:
    s=s.replace('<title>GTA Guide to Platinum</title>','<title>GTA Guide to Platinum</title>'+meta,1)
open('index.html','w').write(s)
