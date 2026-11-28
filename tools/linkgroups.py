# Builds var LINKS in tools/master.html: groups of checklist keys that are the SAME thing
# (one collectible found at several spots, or the same item listed in several tabs).
# Ticking one key ticks its whole group. Sources: GTABase same-name entries
# (tools/gtabase_dupes.json), our titles (magazines, cards), GTL/CARDS/PINK gid links.
# Card groups never merge two different colours of the same card.
import json,re,os,collections
D=os.path.dirname(os.path.abspath(__file__));p=os.path.join(D,'master.html');s=open(p).read()
def J(v):
  i=s.index(v)+len(v);return json.JSONDecoder().raw_decode(s,i)[0]
F=J('var FULL=');CARDS=J('var CARDS=');SETS=J('var SETS=');GTL=J('var GTL=');SYNCX=J('var SYNCX=')
PINK=J('var PINK=') if 'var PINK=' in s else {}
k0=s.index('"MAGS": [');MAGS=json.JSONDecoder().raw_decode(s,s.index('[',k0+6))[0]
title={};G2K=collections.defaultdict(list)
for g in F:
  for sec,items in g[1]:
    for it in items: title['z'+it[0]]=(g[0],sec,it[1]);G2K[it[0]].append('z'+it[0])
for i,c in enumerate(CARDS): title['c%d'%i]=('card',SETS[c[0]][0],'%s card: %s (%s)'%(SETS[c[0]][0],c[1],c[2]))
def cid(k):
  t=title.get(k)
  if not t: return None
  m=re.match(r'^(.*?) card: (.*?)(?: \(([^)]*)\))?\s*$',t[2])
  if not m or not ('card' in t[0].lower()): return None
  col=(m.group(3) or '').strip().lower()
  if col in ('','—','-'): col=None
  nm=re.sub(r'\s*#\d+$','',m.group(2).strip().lower())
  return (t[1].lower(),nm,col)
par={};ids={}
def f(x):
  par.setdefault(x,x)
  while par[x]!=x: par[x]=par[par[x]];x=par[x]
  return x
def ident(k):
  if k not in ids:
    c=cid(k);ids[k]={(c[0],c[1]):{c[2]}} if c and c[2] else {}
  return ids[k]
refused=[]
def u(a,b,why):
  ra,rb=f(a),f(b)
  if ra==rb: return
  A,B=ident(ra),ident(rb)
  for key in set(A)&set(B):
    if A[key]!=B[key] and A[key] and B[key]:
      refused.append((why,a,b,key,A[key],B[key]));return
  par[ra]=rb
  for key,v in A.items(): B.setdefault(key,set()).update(v)
# 1) our own titles: magazines and cards
def nmag(t):
  t=t.lower().strip();t=re.sub(r'^book:\s*','',t);t=re.sub(r'\(.*?\)','',t);t=re.sub(r'\s*#\s*\d+\s*$','',t);t=re.sub(r'\s+\d+\s*$','',t)
  if not t.startswith(('styling','tattoo')): t=re.sub(r'\bmagazine\b','',t)
  t=t.replace('driveshaft','drive shaft');t=re.sub(r'[^a-z0-9ê ]+',' ',t);return re.sub(r'\s+',' ',t).strip()
by=collections.defaultdict(list)
for g in F:
  if 'Magazine' not in g[0]: continue
  for sec,items in g[1]:
    if sec=='Book Swaps': continue
    for it in items:
      n=nmag(it[1])
      if n and not re.match(r'^(styling magazine|tattoo magazine)$',n) and not n.startswith('styling magazine lucia') and not re.search(r'rack|magazines|magazine behind|comics ',it[1].lower()): by['m|'+n].append('z'+it[0])
for i,m in enumerate(MAGS): by['m|'+nmag(m[0])].append('b%d'%i)
for k in title:
  c=cid(k)
  if c: by[('c',)+c].append(k)
for L in by.values():
  for k in L[1:]: u(L[0],k,'title')
# 2) GTABase: same name = same collectible
for grp in json.load(open(os.path.join(D,'gtabase_dupes.json'))):
  ks=[k for g in grp for k in G2K.get(g,[])]
  for k in ks[1:]: u(ks[0],k,'gtabase')
# 3) the same pin/gid listed in other tabs
def J2(v):
  i=s.index(v)+len(v);return json.JSONDecoder().raw_decode(s,s.index('[',i-1))[0]
OT={}
for nm,pf,ix in (('var CARS=','v',0),('var GARAGES=','x',0),('var WEAP=','g',0)):
  for i,x in enumerate(J(nm)): OT[pf+str(i)]=str(x[ix])
for nm,pf in (('"RANDY": [','r'),('"MOSES": [','o')):
  k1=s.index(nm);
  for i,x in enumerate(json.JSONDecoder().raw_decode(s,s.index('[',k1+len(nm)-1))[0]): OT[pf+str(i)]=x[0]
for i,m in enumerate(MAGS): OT['b%d'%i]=m[0]
for gi,(gn,L) in enumerate(J('var WAINK=').items()):
  for i,w in enumerate(L): OT['w%d_%d'%(gi,i)]=w[0]
for i,m in enumerate(J('var MED=')): OT['m%d'%i]=m[0]+' meditation'
import difflib
STOP={'card','book','the','magazine','issue','of','a','in','is','to','and'}
def toks(t):
  t=re.sub(r'\(.*?\)','',(t or '').lower());t=t.split(' card: ')[-1]
  return {w for w in re.findall(r'[a-z0-9ê]+',t) if w not in STOP and not w.isdigit()}
def same(a,b):
  ta=toks(title[a][2] if a in title else OT.get(a,'')); tb=toks(title[b][2] if b in title else OT.get(b,''))
  if not ta or not tb: return False
  if len(ta&tb)/len(ta|tb)>=0.5 or ta<=tb or tb<=ta: return True
  return difflib.SequenceMatcher(None,' '.join(sorted(ta)),' '.join(sorted(tb))).ratio()>=0.8
def link(k,g,why):
  if not g or g[0]=='?' or g.endswith('*') or k[0]=='k': return
  for z in G2K.get(g,[]):
    if z.startswith('zfence'): continue
    if same(k,z): u(k,z,why)
    else: skipped.append((why,k,z))
skipped=[]
for i,c in enumerate(CARDS):
  if len(c)>6 and c[6]: link('c%d'%i,c[6],'cards')
for k,g in GTL.items(): link(k,g,'gtl')
for k,g in SYNCX.items():
  for z in G2K.get(g,[]): u(k,z,'syncx')
for k,g in PINK.items():
  if isinstance(g,str) and k[0]!='p': link(k,g,'pin')
# hand-checked pairs the name test misses
for a,b in [('g10','zweapon-spawn-014')]: u(a,b,'manual')
C=collections.defaultdict(list)
for k in list(par): C[f(k)].append(k)
groups=sorted(sorted(v) for v in C.values() if len(v)>1)
line='var LINKS='+json.dumps(groups,separators=(',',':'))+';'
if 'var LINKS=' in s: s=re.sub(r'var LINKS=\[.*?\];\n',lambda m:line+'\n',s,count=1)
else: s=s.replace('var PINGID=',line+'\nvar PINGID=',1)
open(p,'w').write(s)
if __name__=='__main__':
  print(len(groups),'groups,',sum(len(g) for g in groups),'keys; refused',len(refused))
  for r in refused[:40]: print(' refused',r)
  print('skipped',len(skipped))
  for r in skipped: print(' skip',r[0],r[1],OT.get(r[1],title.get(r[1],('','',''))[2])[:40],'|',r[2],title.get(r[2],('','',''))[2][:40])
