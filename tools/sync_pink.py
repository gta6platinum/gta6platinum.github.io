# Keeps var PINK (non-z pin keys from map/pins.json) in tools/master.html up to date.
import json,re,os
D=os.path.dirname(os.path.abspath(__file__))
p=os.path.join(D,'master.html');s=open(p).read()
pins=json.load(open(os.path.join(D,'..','map','pins.json')))
ks=sorted(k for k in pins if not k.startswith('z'))
line='var PINK='+json.dumps({k:1 for k in ks},separators=(',',':'))+';'
if 'var PINK=' in s: s=re.sub(r'var PINK=\{[^}]*\};',lambda m:line,s,count=1)
else: s=s.replace('var PINGID=',line+'\nvar PINGID=',1)
open(p,'w').write(s)
# prune PINGID entries that have no pin (a dead "On our map" link)
s=open(p).read();gids={v[2] for v in pins.values() if len(v)>2 and v[2]}
i=s.index('var PINGID=')+11;P,e=json.JSONDecoder().raw_decode(s,i)
P2={g:1 for g in P if g in gids}
if len(P2)!=len(P): s=s[:i]+json.dumps(P2,separators=(',',':'))+s[e:];open(p,'w').write(s)
