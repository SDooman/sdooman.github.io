"""Recover vector artwork and high-resolution previews; keep raster exceptions."""
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from PIL import Image, ImageOps, ImageDraw
import pdfplumber
import argparse, json, logging, subprocess, sys, hashlib
import xml.etree.ElementTree as E
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'visual-pipeline'))
from vector_scene import encode, render, SVG
from recover_vectors import figure_boxes
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('batch');ap.add_argument('--pdftocairo',required=True);args=ap.parse_args()
 logging.getLogger('pypdf').setLevel(logging.ERROR)
 book=ROOT/f'gat-{args.batch}';check=ROOT/f'conversion-batches/checkpoints/{args.batch}';rows=json.loads((check/'assets.json').read_text());byid={x['id']:x for x in rows}
 atlas=json.loads((check/'atlas.json').read_text());reader=PdfReader(check/'atlas.pdf');figures=figure_boxes(reader);assert len(figures)==len(atlas)
 for a,(pi,box) in zip(atlas,figures):
  if byid[a['id']]['source_kind']!='atlas':continue
  l,b,r,t=box;page=reader.pages[pi];page.mediabox=RectangleObject([l-1,b-1,r+1,t+1]);page.cropbox=page.mediabox
  w=PdfWriter();w.add_page(page);dest=book/'assets/source-pdf'/f'{a["id"]}.pdf';w.write(dest)
  byid[a['id']]['atlas_page']=pi+1;byid[a['id']]['atlas_bbox_pt']=box
 def raster(row):
  ident=row['id'];source=book/'assets/source-pdf'/f'{ident}.pdf'
  if not source.exists() or row['source_kind']=='quickdraw-preview':return
  for opts,dest in [(['-png','-r','216','-singlefile'],book/'assets/source-png'/ident),(['-svg'],book/'assets/source-svg'/f'{ident}.svg')]:
   subprocess.run([args.pdftocairo,*opts,str(source),str(dest)],check=True,capture_output=True)
  with pdfplumber.open(source) as pdf:
   page=pdf.pages[0];row['text']=page.extract_text() or '';row['pdf_width']=page.width;row['pdf_height']=page.height
   labels=[{'text':c['text'],'bbox_pt':[c['x0'],c['top'],c['x1'],c['bottom']],'font':c['fontname'],'size':c['size']} for c in page.chars]
   primitives=[{k:x[k] for k in ('object_type','x0','x1','top','bottom','path','pts','linewidth','stroke','fill','stroking_color','non_stroking_color') if k in x} for x in page.lines+page.rects+page.curves]
  row['pdf_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
  (book/'assets/data'/f'{ident}.labels.json').write_text(json.dumps({'labels':labels,'drawing_primitives':primitives},ensure_ascii=False,indent=2)+'\n')
 with ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(raster,rows))
 # SVG scene schema deliberately rejects embedded images: never count a raster
 # inside an SVG wrapper as a converted vector drawing.
 report=[]
 for row in rows:
  ident=row['id'];p=book/'assets/source-svg'/f'{ident}.svg'
  if not p.exists():row['contains_raster']=True;continue
  root=E.parse(p).getroot();rasters=list(root.iter('{'+SVG+'}image'));row['contains_raster']=bool(rasters);row['raster_fragments']=len(rasters)
  if row.get('pict_version')==1 and row['native_equations']:continue
  if rasters:continue
  box=list(map(float,root.get('viewBox').split()));labels=[];primitives=[];label_file=book/'assets/data'/f'{ident}.labels.json'
  if label_file.exists():data=json.loads(label_file.read_text());labels=data['labels'];primitives=data['drawing_primitives']
  for i,node in enumerate(root.iter()):
   if node is not root and not node.get('id'):node.set('id',f'primitive-{i:04}')
  scene={'version':1,'kind':'vector','source_asset_id':ident,'title':f'GAT {args.batch}, {ident}',
   'description':'Original drawing paths; positions are layout coordinates, not inferred mathematical constraints.',
   'view_box':box,'coordinate_meaning':'PDF/SVG drawing coordinates, top-left origin; source transforms retained.',
   'representation_level':'drawing-primitives','provenance':{'original_sha256':row['sha256'],'source_kind':row['source_kind'],'pdf_sha256':row.get('pdf_sha256')},
   'elements':[encode(c) for c in root],'labels':labels,'source_drawing_primitives':primitives,'review':'needs_review',
   'label_review':'Legacy PDF text encodings may require correction. SVG outlines preserve visual labels.'}
  write(book/'assets/scenes'/f'{ident}.scene.json',scene);(book/'assets/vectors'/f'{ident}.svg').write_text(render(scene));report.append(ident)
 write(check/'assets.json',rows);write(check/'vector-recovery.json',{'vectors':report,'raster_assets':[r['id'] for r in rows if r['contains_raster']]})
 print(json.dumps({'batch':args.batch,'vector_scenes':len(report),'raster_assets':[r['id'] for r in rows if r['contains_raster']]}))
if __name__=='__main__':main()
