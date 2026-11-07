"""Build a reference-only Word copy with portable previews; source is immutable."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import sys,json
ROOT=Path(__file__).resolve().parents[2];batch=sys.argv[1];check=ROOT/f'conversion-batches/checkpoints/{batch}';book=ROOT/f'gat-{batch}'
z=ZipFile(check/'sized.docx');rels=E.fromstring(z.read('word/_rels/document.xml.rels'));types=E.fromstring(z.read('[Content_Types].xml'))
replacements={}
for rel in rels:
 target=rel.get('Target','')
 if target.startswith('media/'):
  name=Path(target).stem+'.png';rel.set('Target','media/'+name);replacements['word/media/'+name]=(book/'assets/source-png'/name).read_bytes()
if not any(t.get('Extension')=='png' for t in types):E.SubElement(types,'{'+types.nsmap[None]+'}Default',Extension='png',ContentType='image/png')
with ZipFile(check/'reference.docx','w') as out:
 for n in z.namelist():
  if n.startswith('word/media/'):continue
  data=E.tostring(rels) if n=='word/_rels/document.xml.rels' else E.tostring(types) if n=='[Content_Types].xml' else z.read(n)
  out.writestr(n,data)
 for n,b in replacements.items():out.writestr(n,b)
print(batch,'reference copy prepared')
