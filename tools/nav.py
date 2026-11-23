# One-time patch: original header banner + sidebar (desktop) / bottom bar (mobile) navigation
import json,re
p='tools/master.html';s=open(p).read()
assert 'id="nav"' not in s
banner='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="k" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a0f3d"/><stop offset=".45" stop-color="#b8326f"/><stop offset=".75" stop-color="#ff8a4c"/><stop offset="1" stop-color="#ffc94d"/></linearGradient><linearGradient id="w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#22e1d6" stop-opacity=".55"/><stop offset="1" stop-color="#0d0716"/></linearGradient></defs><rect width="1200" height="300" fill="url(#k)"/><circle cx="820" cy="215" r="92" fill="#ffd36b" opacity=".9"/><g fill="#2a0f3d" opacity=".18"><rect x="760" y="150" width="120" height="6"/><rect x="740" y="172" width="160" height="7"/><rect x="730" y="196" width="180" height="8"/></g><path d="M0 230 L60 205 90 215 120 170 150 175 160 120 175 120 185 175 220 160 250 200 300 190 330 140 345 140 360 195 420 180 470 210 520 200 560 150 580 150 600 205 660 195 700 222 1200 222 1200 300 0 300Z" fill="#1a0a26" opacity=".85"/><rect y="236" width="1200" height="64" fill="url(#w)"/><g stroke="#ffe9b0" stroke-opacity=".35" stroke-width="2"><path d="M700 252h240M740 266h160M780 280h80"/></g><g fill="#0d0716"><path d="M1010 300c4-70 8-120 22-170l6 2c-12 50-16 100-18 168z"/><path d="M1035 132c-30-14-62-10-86 8 26-4 52 0 74 10zM1035 132c10-28 34-46 64-50-22 14-40 30-52 54zM1035 132c32-4 60 8 80 30-26-12-52-18-78-14zM1035 132c-18-22-44-34-72-32 24 8 46 22 62 42zM1035 132c4 26-2 52-20 72 8-24 10-48 4-70z"/><path d="M90 300c2-56 6-96 18-136l5 2c-10 40-13 80-14 134z"/><path d="M110 168c-24-12-50-8-70 6 21-3 42 0 60 8zM110 168c8-22 27-37 51-40-18 11-32 24-42 43zM110 168c26-3 48 6 64 24-21-10-42-14-62-11zM110 168c-14-18-35-27-58-26 19 6 37 18 50 34z"/></g></svg>'''
import base64
uri='data:image/svg+xml;base64,'+base64.b64encode(banner.encode()).decode()
css='''
header{position:relative;background:linear-gradient(180deg,rgba(13,7,22,.15),rgba(13,7,22,.85)),url("'''+uri+'''") center/cover no-repeat;padding:34px 16px 12px;border-bottom:1px solid var(--line)}
header h1{text-shadow:0 2px 12px #000a}
#tabs{display:none}
.nav{position:fixed;z-index:40;background:linear-gradient(180deg,#2a0f3d,#13072a);box-shadow:0 20px 40px -20px #000c;display:flex}
.nav button{background:none;border:0;color:var(--mute);font:inherit;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:2px;border-radius:16px;transition:background .25s,color .25s}
.nav button i{font-style:normal;font-size:20px;line-height:1}
.nav button span{font-size:10px;white-space:nowrap;max-width:76px;overflow:hidden;text-overflow:ellipsis}
.nav button:hover{color:#fff}
.nav button.on{color:#1a1027;background:radial-gradient(circle at 40% 35%,#fff,var(--teal) 140%);box-shadow:0 0 0 4px #ffffff22,0 0 22px #22e1d688}
.sheet{position:fixed;inset:0;z-index:45;background:#000a;display:flex;align-items:flex-end}
.sheet[hidden]{display:none}
.sheet .sc{background:var(--card);border-top:1px solid var(--line);border-radius:22px 22px 0 0;width:100%;padding:16px 12px 96px;display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.sheet .sc button{background:var(--card2);border:1px solid var(--line);color:var(--txt);border-radius:14px;padding:12px 4px;font:inherit;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer}
.sheet .sc button i{font-style:normal;font-size:22px}
.sheet .sc button.on{border-color:var(--pink);color:var(--pink)}
@media (min-width:901px){
 .nav{top:16px;bottom:16px;inset-inline-start:16px;width:88px;flex-direction:column;align-items:center;gap:4px;padding:14px 0;border-radius:40px;overflow-y:auto;scrollbar-width:none}
 .nav button{width:76px;padding:8px 0}
 .nav .mb{display:none}
 #app{padding-inline-start:120px}
}
@media (max-width:900px){
 .nav{left:10px;right:10px;bottom:10px;height:64px;border-radius:999px;justify-content:space-around;align-items:center;padding:0 6px}
 .nav button{padding:6px 8px;min-width:58px}
 .nav .dk{display:none}
 footer{padding-bottom:100px}
 #donBtn{bottom:86px!important}
}
'''
s=s.replace('</style>',css+'</style>',1)
s=s.replace('<div class="tabs" id="tabs"></div></header>','<div class="tabs" id="tabs"></div></header><nav class="nav" id="nav"></nav><div class="sheet" id="sheet" hidden><div class="sc" id="sheetc"></div></div>',1)
SH={"ch2":"Chapter","cards":"Cards","wink":"WAiNK","med":"Meditate","trophy":"Trophies","weap":"Weapons","cars":"Cars","garage":"Garage","more":"More finds","full":"Checklist","codes":"Codes","sum":"Totals"}
AR={"Chapter":"الفصل","Cards":"البطاقات","WAiNK":"WAiNK","Meditate":"تأمل","Trophies":"التروفيات","Weapons":"الأسلحة","Cars":"السيارات","Garage":"الكراج","More finds":"مقتنيات","Checklist":"القائمة","Codes":"الأكواد","Totals":"المجموع","More":"المزيد"}
ES={"Chapter":"Capítulo","Cards":"Cartas","WAiNK":"WAiNK","Meditate":"Meditar","Trophies":"Trofeos","Weapons":"Armas","Cars":"Autos","Garage":"Garaje","More finds":"Más","Checklist":"Lista","Codes":"Códigos","Totals":"Totales","More":"Más"}
old='function renderTabs(){document.getElementById("tabs").innerHTML='
assert old in s
newf='''var SHORT='''+json.dumps(SH)+''',MOBT=["ch2","cards","trophy","full"];
function tIcon(t){return t[1].split(" ")[0]}
function renderNav(){var n=document.getElementById("nav");if(!n)return;
var b=function(t,cls){return '<button data-tab="'+t[0]+'" class="'+cls+(t[0]===cur?' on':'')+'"><i>'+tIcon(t)+'</i><span>'+esc(T(SHORT[t[0]]||t[1]))+'</span></button>'};
var h=TABS.map(function(t){return b(t,"dk")}).join("");
h+=TABS.filter(function(t){return MOBT.indexOf(t[0])>=0}).map(function(t){return b(t,"mb")}).join("");
var inMore=MOBT.indexOf(cur)<0;h+='<button class="mb'+(inMore?' on':'')+'" data-sheet="1"><i>☰</i><span>'+esc(T("More"))+'</span></button>';
n.innerHTML=h;document.getElementById("sheetc").innerHTML=TABS.map(function(t){return '<button data-tab="'+t[0]+'" class="'+(t[0]===cur?'on':'')+'"><i>'+tIcon(t)+'</i>'+esc(T(t[1].replace(/^\\S+\\s/,"")))+'</button>'}).join("");document.getElementById("sheet").hidden=true}
'''
s=s.replace(old,newf+old,1)
s=s.replace('join("");TUI(document.getElementById("tabs"))}','join("");TUI(document.getElementById("tabs"));renderNav()}',1)
o='closest("[data-tab]");if(tb){go(tb.getAttribute("data-tab"));return}'
s=s.replace(o,o+'if(e.target.closest("[data-sheet]")){document.getElementById("sheet").hidden=false;return}if(e.target.id==="sheet"){e.target.hidden=true;return}',1)
dm=re.search(r'var DT=(\{.*?\});\nfunction T\(',s,re.S);DT=json.loads(dm.group(1))
for k,v in AR.items(): DT['ar'].setdefault(k,v)
for k,v in ES.items(): DT['es'].setdefault(k,v)
s=s.replace(dm.group(1),json.dumps(DT,ensure_ascii=False,separators=(',',':')).replace('</','<\\/'),1)
open(p,'w').write(s);print('ok')
