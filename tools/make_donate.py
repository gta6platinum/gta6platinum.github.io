# Edit NETS then run: python3 tools/make_donate.py && python3 tools/build_public.py
import qrcode,qrcode.image.svg,io,json
EVM='0xCEa2Ed8fEa320ba952601f8D17AeB07Fcf1aaEb8'
NETS=[("BNB Smart Chain (BEP20)",EVM),("Ethereum (ERC20)",EVM),("Tron (TRC20)","TQ1whfFGSHXE4WL8RcPGhsX2dm4uspQyP9")]
NETS=[n for n in NETS if n[1]]
def q(a):
    img=qrcode.make(a,image_factory=qrcode.image.svg.SvgPathImage,box_size=8,border=2);b=io.BytesIO();img.save(b);s=b.getvalue().decode()
    return s[s.index('<svg'):].replace('<svg','<svg style="width:180px;height:180px;background:#fff;border-radius:10px"',1)
d=open('tools/donate.html').read()
start=d.index('<div class="dtabs">') if '<div class="dtabs">' in d else d.index('<div class="dnet">');end=d.index('<button id="donCopy"')
tabs='<div class="dtabs">'+''.join('<button type="button" class="dtab%s" data-i="%d">%s</button>'%(' on' if i==0 else '',i,n.split(' (')[0]) for i,(n,a) in enumerate(NETS))+'</div>'
panes=''.join('<div class="dpane" data-i="%d"%s><div class="dnet">USDT · %s</div><div class="dqr">%s</div><code class="daddr">%s</code></div>'%(i,'' if i==0 else ' hidden',n,q(a),a) for i,(n,a) in enumerate(NETS))
d=d[:start]+tabs+panes+'\n'+d[end:]
open('tools/donate.html','w').write(d)
