"""Preserve legacy Word media, native MATH comments and dimension repairs.

Run after a LibreOffice DOC-to-DOCX import. No macros or OLE code is executed.
An image is not a formula merely because it contains an embedded MATH comment:
compound PICT v2 drawings keep their complete layout and separate equation data.
"""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from collections import Counter
from copy import deepcopy
import argparse, hashlib, json, struct, subprocess, sys
from mtef import Reader, walk

ROOT=Path(__file__).resolve().parents[2]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def q(k): n,t=k.split(':');return '{'+NS[n]+'}'+t
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('batch');args=ap.parse_args();batch=args.batch
 book=ROOT/f'gat-{batch}';check=ROOT/f'conversion-batches/checkpoints/{batch}';check.mkdir(parents=True,exist_ok=True)
 for name in ['originals','source-pdf','source-png','source-svg','native-math','vectors','scenes','data']:(book/'assets'/name).mkdir(parents=True,exist_ok=True)
 source=ROOT/f'.conversion-work/gat-{batch}/import/GAT-{batch}.docx'
 (check/'imported.docx').write_bytes(source.read_bytes())
 z=ZipFile(source);r=E.fromstring(z.read('word/document.xml'));rels={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('word/_rels/document.xml.rels'))}
 rows=[];trees={}
 for n in sorted((n for n in z.namelist() if n.startswith('word/media/')),key=lambda n:int(Path(n).stem[5:])):
  b=z.read(n);ident=Path(n).stem;suffix=Path(n).suffix
  (book/'assets/originals'/Path(n).name).write_bytes(b)
  row={'id':ident,'original':n,'sha256':sha(b),'format':suffix[1:],'native_equations':[],'source_kind':'pending'}
  if suffix=='.pct':
   top,left,bottom,right=struct.unpack_from('>4h',b,2);row.update(pict_version=1 if b[10:12]==b'\x11\x01' else 2,width=right-left,height=bottom-top)
   start=0
   while (i:=b.find(b'MATH',start))>=0:
    # MathType's PICT comment header precedes the MTEF record stream by 10 bytes.
    # Parse through the terminating END record, excluding the comment checksum.
    reader=Reader(b[i+10:]);tree=reader.items();mtef=b[i+10:i+10+reader.pos]
    Reader(mtef).parse();key=f'{ident}-{len(row["native_equations"])+1}'
    (book/'assets/native-math'/f'{key}.mtef').write_bytes(mtef);trees[key]=tree
    row['native_equations'].append({'id':key,'offset_in_original':i+10,'bytes':len(mtef),'sha256':sha(mtef)})
    start=i+10+reader.pos
   if row['pict_version']==1:
    row['source_kind']='quickdraw-preview'
  elif suffix=='.emf' and b'%PDF-' in b:
   offset=0;pdfs=[]
   while offset<len(b):
    op,size=struct.unpack_from('<II',b,offset);assert size>=8 and offset+size<=len(b)
    rec=b[offset:offset+size];offset+=size
    if op==70 and b'%PDF-' in rec:
     i=rec.index(b'%PDF-');j=rec.rfind(b'%%EOF')+5;assert j>i;pdfs.append(rec[i:j]+b'\n')
   assert len(pdfs)==1;pdf=pdfs[0];(book/'assets/source-pdf'/f'{ident}.pdf').write_bytes(pdf)
   row.update(source_kind='embedded-pdf',pdf_sha256=sha(pdf))
  elif suffix=='.png':
   (book/'assets/source-png'/f'{ident}.png').write_bytes(b);row['source_kind']='original-png'
  rows.append(row)
 byid={x['id']:x for x in rows};repairs=[]
 for d in r.findall('.//wp:inline',NS)+r.findall('.//wp:anchor',NS):
  f=rels[d.find('.//a:blip',NS).get(q('r:embed'))];row=byid[Path(f).stem];ex=d.find('wp:extent',NS)
  w,h=int(ex.get('cx'))/12700,int(ex.get('cy'))/12700
  # Imported equation PICT extents are 72 times their point dimensions.
  # Detect from BOTH dimensions, not an asset-number cutoff.
  if row.get('pict_version') and w>row['width']*10 and h>row['height']*10:
   assert abs(w/72-(row['width']+1))<=1.05 and abs(h/72-(row['height']+1))<=1.05,(f,w,h,row)
   for e in [ex,d.find('.//a:xfrm/a:ext',NS)]:
    for attr in ['cx','cy']:e.set(attr,str(round(int(e.get(attr))/72)))
   repairs.append({'image':row['id'],'original_extent_pt':[w,h],'scale':1/72})
 write(check/'dimension-repairs.json',repairs)
 write(check/'assets.json',rows);write(check/'mtef-trees.json',trees)
 with ZipFile(check/'sized.docx','w') as out:
  for n in z.namelist():out.writestr(n,E.tostring(r) if n=='word/document.xml' else z.read(n))
 subprocess.run([sys.executable,str(ROOT/'conversion-batches/scripts/quickdraw_preview.py'),str(book),str(check)],check=True,capture_output=True)
 previews=json.loads((check/'quickdraw-equations.json').read_text())
 for row in rows:
  if row['source_kind']=='quickdraw-preview' and row['id']+'.pct' not in previews:row['source_kind']='pending'
 subprocess.run([sys.executable,str(ROOT/'conversion-batches/scripts/fix_pict2.py'),str(book),str(check)],check=True,capture_output=True)
 # One non-PDF/non-equation image per atlas page for vector-preserving export.
 body=r.find('w:body',NS);out=E.Element(q('w:body'));seen=set();atlas=[]
 for d0 in r.findall('.//wp:inline',NS):
  f=rels[d0.find('.//a:blip',NS).get(q('r:embed'))];row=byid[Path(f).stem]
  if f in seen or row['source_kind']!='pending':continue
  seen.add(f);d=deepcopy(d0);cx=int(d.find('wp:extent',NS).get('cx'));cy=int(d.find('wp:extent',NS).get('cy'));scale=min(1,480*12700/cx,640*12700/cy)
  for e in [d.find('wp:extent',NS),d.find('.//a:xfrm/a:ext',NS)]:e.set('cx',str(round(cx*scale)));e.set('cy',str(round(cy*scale)))
  p=E.SubElement(out,q('w:p'));pp=E.SubElement(p,q('w:pPr'));E.SubElement(pp,q('w:spacing'),{q('w:before'):'0',q('w:after'):'0'})
  if atlas:E.SubElement(pp,q('w:pageBreakBefore'))
  rr=E.SubElement(p,q('w:r'));E.SubElement(rr,q('w:drawing')).append(d)
  atlas.append({'id':row['id'],'file':f,'width_pt':cx*scale/12700,'height_pt':cy*scale/12700});row['source_kind']='atlas'
 sp=E.SubElement(out,q('w:sectPr'));E.SubElement(sp,q('w:pgSz'),{q('w:w'):'12240',q('w:h'):'15840'});E.SubElement(sp,q('w:pgMar'),{q('w:top'):'720',q('w:bottom'):'720',q('w:left'):'720',q('w:right'):'720'})
 r.replace(body,out)
 with ZipFile(check/'atlas.docx','w') as zz:
  for n in z.namelist():
   b=z.read(n);fixed=check/'fixed-pict'/Path(n).name
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
 write(check/'atlas.json',atlas);write(check/'assets.json',rows)
 print(json.dumps({'batch':batch,'assets':len(rows),'native_equation_records':len(trees),'source_kinds':dict(Counter(x['source_kind'] for x in rows)),'atlas_pages':len(atlas),'dimension_repairs':len(repairs)}))
if __name__=='__main__':main()
