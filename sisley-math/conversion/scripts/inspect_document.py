from zipfile import ZipFile
from lxml import etree as E
from pathlib import Path
from collections import Counter
import struct
z=ZipFile('.conversion-work/GAT 1-20.docx'); ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
r=E.fromstring(z.read('word/document.xml'))
rels={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('word/_rels/document.xml.rels'))}
for d in r.findall('.//wp:inline',ns):
 name=d.find('wp:docPr',ns).get('name'); f=rels[d.find('.//a:blip',ns).get('{'+ns['r']+'}embed')]
 if int(name.replace('Image',''))<542:
  for q in [d.find('wp:extent',ns),d.find('.//a:xfrm/a:ext',ns)]:
   for a in ['cx','cy']:q.set(a,str(round(int(q.get(a))/72)))
with ZipFile('.conversion-work/sized.docx','w') as out:
 for n in z.namelist():out.writestr(n,E.tostring(r) if n=='word/document.xml' else z.read(n))
print('PICT types',Counter(p.read_bytes()[10:12].hex() for p in Path('gat-1-20/assets/originals').glob('*.pct')))
print('Page breaks before',len(r.findall('.//w:pageBreakBefore',ns)))
for i,p in enumerate(r.findall('.//w:body/w:p',ns)):
 if p.find('w:pPr/w:sectPr',ns) is not None:print('sect',i, E.tostring(p.find('w:pPr/w:sectPr',ns)).decode()[-800:])
