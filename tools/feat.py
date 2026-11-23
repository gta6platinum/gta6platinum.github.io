# One-time patch: global search + progress backup
import json,re
p='tools/master.html';s=open(p).read()
assert 'id="srchBtn"' not in s
s=s.replace('<div class="sub sync" id="sync"></div>','<div class="sub sync" id="sync"></div><div class="lang tools"><button id="srchBtn">🔍 Search</button><button id="bkBtn">💾 Backup</button></div>',1)
s=s.replace('<nav class="nav" id="nav"></nav>','<nav class="nav" id="nav"></nav><div class="modal" id="mSearch" hidden><div class="mc"><div class="mh"><input id="sq" type="search" placeholder="Search everything — card, car, code, trophy…" autocomplete="off"><button class="mx" data-close="mSearch">✕</button></div><div id="sres" class="sres"></div></div></div><div class="modal" id="mBackup" hidden><div class="mc"><div class="mh"><b>💾 Backup your progress</b><button class="mx" data-close="mBackup">✕</button></div><p class="d">Your ticks live in this browser only. Save a backup to move them to another phone or browser, or to keep them safe.</p><div class="links"><a href="#" id="bkDl">⬇️ Download backup file</a><a href="#" id="bkCopy">📋 Copy backup code</a></div><p class="d" style="margin-top:12px">Restore: pick a backup file or paste a code.</p><input type="file" id="bkFile" accept=".json,application/json"><textarea id="bkCode" rows="3" placeholder="Paste backup code here"></textarea><div class="links"><a href="#" id="bkRestore">♻️ Restore</a></div><p class="d" id="bkMsg"></p></div></div>',1)
css='''
.tools button{font-size:14px!important;padding:7px 14px!important}
.modal{position:fixed;inset:0;z-index:70;background:#000b;display:flex;align-items:flex-start;justify-content:center;padding:6vh 12px}
.modal[hidden]{display:none}
.mc{background:var(--card);border:1px solid var(--line);border-radius:18px;width:100%;max-width:640px;max-height:84vh;overflow:auto;padding:16px}
.mh{display:flex;gap:8px;align-items:center;justify-content:space-between;margin-bottom:10px}
.mh input{flex:1;background:var(--card2);border:1px solid var(--line);color:var(--txt);border-radius:12px;padding:12px 14px;font:inherit;font-size:16px}
.mx{background:none;border:0;color:var(--txt);font-size:20px;cursor:pointer;padding:6px 10px}
.sres .hit{display:block;width:100%;text-align:start;background:var(--card2);border:1px solid var(--line);color:var(--txt);border-radius:12px;padding:10px 12px;margin-bottom:8px;font:inherit;cursor:pointer}
.sres .hit small{display:block;color:var(--teal);font-size:12px;margin-bottom:2px}
.sres .hit.done{opacity:.55}
.mc textarea{width:100%;margin-top:8px;background:var(--card2);border:1px solid var(--line);color:var(--txt);border-radius:12px;padding:10px;font:inherit;font-size:13px}
.mc input[type=file]{margin-top:6px;color:var(--mute);font-size:13px}
.row.flash{animation:fl 2s ease}
@keyframes fl{0%,40%{background:#22e1d633}100%{background:transparent}}
'''
s=s.replace('</style>',css+'</style>',1)
js=r'''
var SIDX=null;
function buildIndex(){var V={ch2:vCh2,cards:vCards,wink:vWink,med:vMed,trophy:vTrophy,weap:vWeap,cars:vCars,garage:vGarage,more:vMore,full:vFull,codes:vCodes},idx=[],seen={},keep=filt;
TABS.forEach(function(t){if(!V[t[0]])return;var d=document.createElement("div");try{filt={};d.innerHTML=V[t[0]]();TUI(d)}catch(e){return}
d.querySelectorAll(".row[data-k]").forEach(function(r){var k=r.getAttribute("data-k");if(seen[k])return;seen[k]=1;var tx=r.cloneNode(true);tx.querySelectorAll(".links,input,button").forEach(function(x){x.remove()});var txt=tx.textContent.replace(/\s+/g," ").trim();idx.push({k:k,tab:t[0],lab:T(t[1]),txt:txt,low:txt.toLowerCase()})})});
filt=keep;return idx}
function runSearch(q){var box=document.getElementById("sres");q=q.trim().toLowerCase();if(q.length<2){box.innerHTML='<p class="d">'+esc(T("Type at least 2 letters."))+'</p>';return}
if(!SIDX)SIDX=buildIndex();var words=q.split(/\s+/),hits=SIDX.filter(function(x){return words.every(function(w){return x.low.indexOf(w)>=0})}).slice(0,40);
box.innerHTML=hits.length?hits.map(function(h){return '<button class="hit'+(isOn(h.k)?' done':'')+'" data-hit="'+h.k+'" data-tab="'+h.tab+'"><small>'+esc(h.lab)+(isOn(h.k)?' · ✅':'')+'</small>'+esc(h.txt.slice(0,160))+'</button>'}).join(""):'<p class="d">'+esc(T("Nothing found."))+'</p>'}
function jumpTo(k){setTimeout(function(){var r=document.querySelector('.row[data-k="'+k+'"]');if(!r)return;var p=r.parentNode;while(p&&p!==document.body){if(p.tagName==="DETAILS")p.open=true;p=p.parentNode}r.scrollIntoView({block:"center"});r.classList.add("flash")},60)}
function bkCode(){return btoa(unescape(encodeURIComponent(JSON.stringify({v:1,t:st.t,s:st.s}))))}
function bkApply(obj){if(!obj||typeof obj.s!=="object")throw 0;var n=0;Object.keys(obj.s).forEach(function(k){if(!st.s[k]){st.s[k]=1;n++}});st.t=Date.now();try{localStorage.setItem(SKEY,JSON.stringify(st))}catch(e){}schedulePub();render();return n}
function bkMsg(m){document.getElementById("bkMsg").textContent=T(m)}
document.addEventListener("click",function(e){
 var c=e.target.closest("[data-close]");if(c){document.getElementById(c.getAttribute("data-close")).hidden=true;return}
 if(e.target.classList&&e.target.classList.contains("modal")){e.target.hidden=true;return}
 if(e.target.closest("#srchBtn")){SIDX=null;var m=document.getElementById("mSearch");m.hidden=false;var q=document.getElementById("sq");q.value="";runSearch("");setTimeout(function(){q.focus()},30);return}
 if(e.target.closest("#bkBtn")){document.getElementById("mBackup").hidden=false;bkMsg("");return}
 var h=e.target.closest("[data-hit]");if(h){document.getElementById("mSearch").hidden=true;jumpTo(h.getAttribute("data-hit"));return}
 if(e.target.closest("#bkDl")){e.preventDefault();var b=new Blob([JSON.stringify({v:1,t:st.t,s:st.s})],{type:"application/json"}),a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="gta6-platinum-backup.json";document.body.appendChild(a);a.click();a.remove();bkMsg("Backup file downloaded.");return}
 if(e.target.closest("#bkCopy")){e.preventDefault();var code=bkCode(),ta=document.getElementById("bkCode");ta.value=code;try{navigator.clipboard.writeText(code).then(function(){bkMsg("Backup code copied — keep it somewhere safe.")},function(){ta.select();bkMsg("Select the code in the box and copy it.")})}catch(x){ta.select();bkMsg("Select the code in the box and copy it.")}return}
 if(e.target.closest("#bkRestore")){e.preventDefault();var v=document.getElementById("bkCode").value.trim();if(!v){bkMsg("Paste a code or pick a file first.");return}try{var n=bkApply(JSON.parse(decodeURIComponent(escape(atob(v)))));bkMsg("Restored! Added "+n+" ticks.")}catch(x){bkMsg("That code isn't valid.")}return}
},true);
document.addEventListener("input",function(e){if(e.target.id==="sq")runSearch(e.target.value)});
document.addEventListener("change",function(e){if(e.target.id!=="bkFile"||!e.target.files[0])return;var fr=new FileReader();fr.onload=function(){try{var n=bkApply(JSON.parse(fr.result));bkMsg("Restored! Added "+n+" ticks.")}catch(x){bkMsg("That file isn't a valid backup.")}};fr.readAsText(e.target.files[0])});
document.addEventListener("keydown",function(e){if(e.key==="Escape")document.querySelectorAll(".modal").forEach(function(m){m.hidden=true})});
'''
s=s.replace('function renderNav(){',js+'function renderNav(){',1)
TR={"🔍 Search":("🔍 بحث","🔍 Buscar"),"💾 Backup":("💾 نسخة احتياطية","💾 Copia"),
"Search everything — card, car, code, trophy…":("ابحث في كل شي — بطاقة، سيارة، كود، تروفي…","Busca todo — carta, auto, código, trofeo…"),
"💾 Backup your progress":("💾 احفظ تقدمك","💾 Guarda tu progreso"),
"Your ticks live in this browser only. Save a backup to move them to another phone or browser, or to keep them safe.":("علاماتك محفوظة في هالمتصفح بس. سوّ نسخة احتياطية عشان تنقلها لجوال أو متصفح ثاني، أو عشان ما تضيع.","Tus marcas viven solo en este navegador. Guarda una copia para pasarlas a otro móvil o navegador, o para no perderlas."),
"⬇️ Download backup file":("⬇️ تنزيل ملف النسخة","⬇️ Descargar archivo"),"📋 Copy backup code":("📋 نسخ كود النسخة","📋 Copiar código"),
"Restore: pick a backup file or paste a code.":("الاسترجاع: اختر ملف النسخة أو الصق الكود.","Restaurar: elige el archivo o pega el código."),
"Paste backup code here":("الصق كود النسخة هنا","Pega el código aquí"),"♻️ Restore":("♻️ استرجاع","♻️ Restaurar"),
"Type at least 2 letters.":("اكتب حرفين على الأقل.","Escribe al menos 2 letras."),"Nothing found.":("ما لقيت شي.","No se encontró nada."),
"Backup file downloaded.":("نزل ملف النسخة.","Archivo descargado."),"Backup code copied — keep it somewhere safe.":("انسخ الكود — احفظه بمكان آمن.","Código copiado — guárdalo en un lugar seguro."),
"Select the code in the box and copy it.":("حدد الكود في المربع وانسخه.","Selecciona el código y cópialo."),"Paste a code or pick a file first.":("الصق كود أو اختر ملف أول.","Pega un código o elige un archivo primero."),
"That code isn't valid.":("الكود غير صحيح.","Ese código no es válido."),"That file isn't a valid backup.":("الملف مو نسخة صحيحة.","Ese archivo no es una copia válida.")}
dm=re.search(r'var DT=(\{.*?\});\nfunction T\(',s,re.S);DT=json.loads(dm.group(1))
for k,(a,e) in TR.items(): DT['ar'][k]=a;DT['es'][k]=e
s=s.replace(dm.group(1),json.dumps(DT,ensure_ascii=False,separators=(',',':')).replace('</','<\\/'),1)
open(p,'w').write(s);print('ok')
