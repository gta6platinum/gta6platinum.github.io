"""Recolor gtadb.org GTA VI map tiles (CC BY 4.0, https://map.gtadb.org) into the site's night style.
Adaptation: colour remap only. Usage: python3 restyle_tiles.py SRC_DIR DST_DIR [maxz]"""
import sys,os,numpy as np
from PIL import Image
def ramp(l,stops):
    xs=np.array([p for p,_ in stops]);out=np.zeros(l.shape+(3,))
    for k in range(3):out[...,k]=np.interp(l,xs,[c[k] for _,c in stops])
    return out
def restyle(im):
    a=np.asarray(im.convert('RGB')).astype(np.float32)/255
    r,g,b=a[...,0],a[...,1],a[...,2]
    mx=a.max(-1);mn=a.min(-1);sat=(mx-mn)/(mx+1e-6);lum=0.299*r+0.587*g+0.114*b
    wn=np.clip(1-(sat-0.04)/0.14,0,1)            # neutral (urban, roads)
    hw=np.clip((b-np.maximum(r,g))/0.08+0.5,0,1)  # blue-ish
    hs=np.clip((r-b-0.06)/0.08,0,1)*np.clip((g-b-0.03)/0.08,0,1) # sandy
    rest=1-wn
    ww=rest*hw*(1-hs);ws=rest*hs;wg=np.clip(rest-ww-ws,0,1)
    neu=ramp(lum,[(0,(0.06,0.05,0.10)),(0.55,(0.17,0.14,0.26)),(0.72,(0.36,0.30,0.50)),(0.84,(0.62,0.48,0.72)),(0.93,(1.0,0.62,0.82)),(1,(1.0,0.75,0.88))])
    wat=ramp(lum,[(0,(0.03,0.03,0.09)),(0.45,(0.07,0.06,0.17)),(0.7,(0.13,0.11,0.28)),(1,(0.25,0.22,0.45))])
    grn=ramp(lum,[(0,(0.04,0.09,0.08)),(0.4,(0.07,0.17,0.15)),(0.65,(0.12,0.27,0.22)),(1,(0.30,0.45,0.38))])
    snd=ramp(lum,[(0,(0.35,0.25,0.14)),(1,(0.95,0.72,0.45))])
    out=neu*wn[...,None]+wat*ww[...,None]+grn*wg[...,None]+snd*ws[...,None]
    return Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8))
if __name__=='__main__':
    src,dst=sys.argv[1],sys.argv[2];mz=int(sys.argv[3]) if len(sys.argv)>3 else 5
    for z in range(0,mz+1):
        d=os.path.join(src,str(z))
        if not os.path.isdir(d):continue
        os.makedirs(os.path.join(dst,str(z)),exist_ok=True)
        for f in os.listdir(d):
            o=os.path.join(dst,str(z),f.replace('.jpg','.webp'))
            if os.path.exists(o):continue
            restyle(Image.open(os.path.join(d,f))).save(o,'WEBP',quality=72,method=4)
        print('z',z,'done',flush=True)
