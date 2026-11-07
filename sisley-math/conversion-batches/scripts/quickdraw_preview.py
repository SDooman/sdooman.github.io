from pathlib import Path
import sys
BOOK=Path(sys.argv[1]); CHECK=Path(sys.argv[2])
import struct,json,html
from collections import Counter
from reportlab.pdfbase import _fontdata
from reportlab.pdfbase._glyphlist import _glyphname2unicode
symbol={i:chr(_glyphname2unicode[g]) for i,g in enumerate(_fontdata.encodings['SymbolEncoding']) if g in _glyphname2unicode}
symbol.update(dict(zip([0xe6,0xe7,0xe8,0xf6,0xf7,0xf8,0xe9,0xea,0xeb,0xf9,0xfa,0xfb], '⎛⎜⎝⎞⎟⎠⎡⎢⎣⎤⎥⎦⎧⎨⎩⎪')))
symbol.update({0xec:'⎧',0xed:'⎨',0xee:'⎩',0xef:'⎪'})
usage=Counter();errors={};allmeta={}
for p in (BOOK/'assets/originals').glob('*.pct'):
 b=p.read_bytes()
 if b[10:12]!=b'\x11\x01':continue
 pos=12;fonts={0:'Times',20:'Times',21:'Helvetica',23:'Symbol'};font=0;size=12;face=0;x=y=0;tx=ty=0;els=[];texts=[];pw=ph=1;lines=[]
 top,left,bottom,right=struct.unpack_from('>4h',b,2);ratio_x=ratio_y=1
 def get(fmt):
  global pos
  n=struct.calcsize(fmt);v=struct.unpack_from(fmt,b,pos);pos+=n;return v[0] if len(v)==1 else v
 def pascal():
  global pos
  n=get('>B');s=b[pos:pos+n];pos+=n;return s
 try:
  while pos<len(b):
   at=pos;op=get('>B')
   if op==0xff:break
   elif op==0:pass
   elif op==0xa0:get('>H')
   elif op==0xa1:
    k,n=get('>HH');pos+=n
   elif op==1:
    n=get('>H');pos+=n-2
   elif op in [2,9,10]:pos+=8
   elif op==3:font=get('>H')
   elif op==4:face=get('>B')
   elif op in [5,8]:get('>H')
   elif op==6:pos+=4
   elif op==7:ph,pw=get('>hh')
   elif op==0xb:pos+=4
   elif op==0xc:pos+=4
   elif op==0xd:size=get('>H')
   elif op in [0xe,0xf]:pos+=4
   elif op==0x10:
    ny,nx,dy,dx=get('>hhhh');ratio_x=nx/dx;ratio_y=ny/dy
   elif op==0x2c:
    n=get('>H');end=pos+n;fid=get('>H');fonts[fid]=pascal().decode('mac_roman');pos=end
   elif op in [0x2d,0x2e]:
    n=get('>H');pos+=n
   elif op==0x20:
    y1,x1,y2,x2=get('>hhhh');lines.append((x1,y1,x2,y2,pw,ph));x,y=x2,y2
   elif op==0x21:
    y2,x2=get('>hh');lines.append((x,y,x2,y2,pw,ph));x,y=x2,y2
   elif op==0x22:
    y1,x1,dx,dy=get('>hhhh') if False else get('>hhbb');lines.append((x1,y1,x1+dx,y1+dy,pw,ph));x,y=x1+dx,y1+dy
   elif op==0x23:
    dx,dy=get('>bb');lines.append((x,y,x+dx,y+dy,pw,ph));x+=dx;y+=dy
   elif op in [0x28,0x29,0x2a,0x2b]:
    if op==0x28:ty,tx=get('>hh')
    elif op==0x29:tx+=get('>B')
    elif op==0x2a:ty+=get('>B')
    else:
     dx,dy=get('>BB');tx+=dx;ty+=dy
    raw=pascal();fn=fonts.get(font,str(font));s=''
    for c in raw:
     usage[(fn,c)]+=1
     if fn=='Symbol':s+=symbol.get(c,chr(c))
     elif fn=='MT Extra':s+= {'l':'ℓ','o':'∘'}.get(chr(c),chr(c))
     else:s+=bytes([c]).decode('mac_roman')
    texts.append({'x':tx,'y':ty,'text':s,'font':fn,'size':size*ratio_y,'text_ratio':[ratio_x,ratio_y],'face':face,'raw':raw.hex()})
   elif 0x30<=op<=0x34:
    t,l,bb,rr=get('>hhhh')
    if op in (0x30,0x31):els.append(f'<rect x="{l}" y="{t}" width="{rr-l}" height="{bb-t}" fill="'+('black' if op==0x31 else 'none')+'" stroke="black"/>')
   else:raise ValueError(f'unsupported opcode {op:02x} at {at}')
  for x1,y1,x2,y2,pw,ph in lines:
   if (x1,y1)==(x2,y2):continue
   els.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" stroke-width="{max(0.6,pw,ph)}"/>')
  bracket_groups={}
  for t in texts:
   ch=t['text'].strip()
   if ch in '⎛⎜⎝⎞⎟⎠⎡⎢⎣⎤⎥⎦⎧⎨⎩⎪' and ch:
    side='left' if ch in '⎛⎜⎝⎡⎢⎣⎧⎨⎩⎪' else 'right'
    kind='round' if ch in '⎛⎜⎝⎞⎟⎠' else 'curly' if ch in '⎧⎨⎩⎪' else 'square'
    bracket_groups.setdefault((t['x'],side,kind),[]).append(t)
  for (bx,side,kind),ts in bracket_groups.items():
   sz=ts[0]['size'];yt=min(t['y'] for t in ts)-sz*.78;yb=max(t['y'] for t in ts)+sz*.22
   if side=='left':vx=bx;tip=bx+sz*.27
   else:vx=bx+sz*.42;tip=vx-sz*.27
   if kind=='curly':
    ym=(yt+yb)/2;d=f'M {tip} {yt} Q {vx} {yt} {vx} {yt+sz*.35} V {ym-sz*.25} Q {vx} {ym} {vx-sz*.2} {ym} Q {vx} {ym} {vx} {ym+sz*.25} V {yb-sz*.35} Q {vx} {yb} {tip} {yb}'
   elif kind=='square':d=f'M {tip} {yt} H {vx} V {yb} H {tip}'
   else:d=f'M {tip} {yt} C {vx} {yt+(yb-yt)*.15} {vx} {yb-(yb-yt)*.15} {tip} {yb}'
   els.append(f'<path d="{d}" fill="none" stroke="black" stroke-width="0.65"/>')
  for t in texts:
   if t['text'].strip() and t['text'].strip() in '⎛⎜⎝⎞⎟⎠⎡⎢⎣⎤⎥⎦⎧⎨⎩⎪':continue
   style='italic' if t['face']&2 else 'normal';weight='bold' if t['face']&1 else 'normal'
   els.append(f'<text x="{t["x"]}" y="{t["y"]}" font-family="STIXGeneral, Times New Roman, Times, serif" font-size="{t["size"]}" font-style="{style}" font-weight="{weight}">{html.escape(t["text"])}</text>')
  width,height=right-left+2,bottom-top+2
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width*4/3:g}" height="{height*4/3:g}" viewBox="{left-1} {top-1} {width} {height}"><title>Equation from source image {p.stem}</title>'+''.join(els)+'</svg>'
  (BOOK/'assets/source-svg'/f'{p.stem}.svg').write_text(svg)
  allmeta[p.name]={'width':width*4/3,'height':height*4/3,'texts':texts,'lines':lines}
 except Exception as e:errors[p.name]=str(e)
(CHECK/'quickdraw-equations.json').write_text(json.dumps(allmeta,indent=2,ensure_ascii=False))
print('Converted',len(allmeta),'Errors',errors)
print('Symbol usage',[(f,hex(c),chr(c),n) for (f,c),n in usage.items() if f not in ('Times','Helvetica')])
