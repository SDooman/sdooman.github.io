from zipfile import ZipFile
from pathlib import Path
from lxml import etree as E
from copy import deepcopy
import struct,json
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
z=ZipFile('.conversion-work/sized.docx');r=E.fromstring(z.read('word/document.xml'));rels={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('word/_rels/document.xml.rels'))}
def q(k):n,t=k.split(':');return '{'+ns[n]+'}'+t
body=r.find('w:body',ns);out=E.Element(q('w:body'));seen=set();meta=[]
for d in r.findall('.//wp:inline',ns):
 f=rels[d.find('.//a:blip',ns).get(q('r:embed'))];b=z.read('word/'+f)
 if f in seen or (f.endswith('.pct') and b[10:12]==b'\x11\x01'):continue
 seen.add(f);d=deepcopy(d);cx=int(d.find('wp:extent',ns).get('cx'));cy=int(d.find('wp:extent',ns).get('cy'))
 scale=min(1,480*12700/cx,640*12700/cy)
 for e in [d.find('wp:extent',ns),d.find('.//a:xfrm/a:ext',ns)]:
  e.set('cx',str(round(cx*scale)));e.set('cy',str(round(cy*scale)))
 p=E.SubElement(out,q('w:p'));pp=E.SubElement(p,q('w:pPr'));E.SubElement(pp,q('w:spacing'),{q('w:before'):'0',q('w:after'):'0'})
 if meta:E.SubElement(pp,q('w:pageBreakBefore'))
 rr=E.SubElement(p,q('w:r'));E.SubElement(rr,q('w:drawing')).append(d)
 meta.append({'file':f,'width_pt':cx*scale/12700,'height_pt':cy*scale/12700})
sp=E.SubElement(out,q('w:sectPr'));E.SubElement(sp,q('w:pgSz'),{q('w:w'):'12240',q('w:h'):'15840'});E.SubElement(sp,q('w:pgMar'),{q('w:top'):'720',q('w:bottom'):'720',q('w:left'):'720',q('w:right'):'720'})
r.replace(body,out)
with ZipFile('.conversion-work/atlas.docx','w') as zz:
 for n in z.namelist():
  b=z.read(n)
  fixed=Path('.conversion-work',Path(n).name)
  if n.endswith('.pct') and fixed.exists():b=fixed.read_bytes()
  if n=='word/document.xml':b=E.tostring(r)
  if n.endswith('.emf'):
   parts=[];o=0
   while o<len(b):
    t,size=struct.unpack_from('<II',b,o)
    if t not in (70,67,75):parts.append(b[o:o+size])
    o+=size
   b=bytearray(b''.join(parts));struct.pack_into('<II',b,48,len(b),len(parts))
  zz.writestr(n,b)
Path('.conversion-work/atlas.json').write_text(json.dumps(meta,indent=2));print('Atlas pages:',len(meta))
