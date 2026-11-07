"""Convert native, raster-free source PDF drawings into the shared SVG/JSON format."""
from pathlib import Path
import sys,json,hashlib,xml.etree.ElementTree as E
import pdfplumber
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'visual-pipeline'))
from vector_scene import encode,render,SVG
def main():
    book=ROOT/'gat-21-40';rows=json.loads((ROOT/'conversion-21-40/checkpoints/embedded-pdfs.json').read_text())
    decisions={x['id']:x for x in json.loads((ROOT/'conversion-21-40/visual-decisions.json').read_text())['assets']};summary=[]
    for row in rows:
        if row['equation_object']:continue
        ident=row['id'];root=E.parse(book/'assets/source-svg'/f'{ident}.svg').getroot();rasters=list(root.iter('{'+SVG+'}image'))
        assert bool(rasters)==decisions[ident]['contains_raster']
        if rasters:
            summary.append({'id':ident,'status':'original-retained','raster_fragments':len(rasters)});continue
        for i,node in enumerate(root.iter()):
            if node is not root and not node.get('id'):node.set('id',f'primitive-{i:04}')
        with pdfplumber.open(book/'assets/source-pdf'/f'{ident}.pdf') as pdf:
            p=pdf.pages[0]
            labels=[{'id':f'label-{i:04}','text':c['text'],'bbox_pt':[c['x0'],c['top'],c['x1'],c['bottom']], 'font':c['fontname'],'size':c['size']} for i,c in enumerate(p.chars)]
            drawings=[{'id':f'drawing-{i:04}',**{k:x[k] for k in ('object_type','x0','x1','top','bottom','path','pts','linewidth','stroke','fill','stroking_color','non_stroking_color') if k in x}} for i,x in enumerate(p.lines+p.rects+p.curves)]
        scene={'version':1,'kind':'vector','source_asset_id':ident,'title':f'GAT 21–40 {ident}',
               'description':'Original drawing geometry recovered from the embedded source PDF. Layout points are not inferred mathematical coordinates.',
               'view_box':[0,0,row['width'],row['height']],'coordinate_meaning':'PDF layout points with original SVG transforms retained.',
               'representation_level':'drawing-primitives','provenance':{'pdf_sha256':row['pdf_sha256'],'emf_sha256':row['emf_sha256'],'method':'Original PDF extracted from EMF comment; Poppler SVG export.'},
               'elements':[encode(c) for c in root],'labels':labels,'source_drawing_primitives':drawings,
               'notes':decisions[ident]['notes'],'review':'needs_review'}
        (book/'assets/scenes'/f'{ident}.scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
        (book/'assets/vectors'/f'{ident}.svg').write_text(render(scene))
        summary.append({'id':ident,'status':'vector-candidate','labels':len(labels),'primitives':len(drawings)})
    (ROOT/'conversion-21-40/checkpoints/vector-recovery.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('Raster-free vector candidates:',sum(x['status']=='vector-candidate' for x in summary))
if __name__=='__main__':main()
