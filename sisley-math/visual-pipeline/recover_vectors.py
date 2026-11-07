#!/usr/bin/env python3
"""Recover the saved GAT diagram atlas as vector scenes with source provenance.

Requires pdftocairo (Poppler), pdfplumber, pypdf and Pillow. Does not modify PDFs.
"""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import pdfplumber
from pypdf import PdfReader
from PIL import Image
from vector_scene import SVG, XLINK, encode, render, latex_records


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n')


def figure_boxes(reader):
    pages = {page.indirect_reference.idnum:i for i,page in enumerate(reader.pages)}
    figures = []
    def walk(obj):
        if isinstance(obj,list):
            for child in obj: walk(child)
            return
        obj = obj.get_object() if hasattr(obj,'get_object') else obj
        if not isinstance(obj,dict): return
        if obj.get('/S') == '/Figure':
            figures.append((pages[obj.raw_get('/Pg').idnum], list(map(float,obj['/A']['/BBox']))))
        if '/K' in obj: walk(obj['/K'])
    walk(reader.trailer['/Root']['/StructTreeRoot']['/K'])
    return figures


def simplify(points, tolerance):
    if len(points) < 3: return points
    a,b=points[0],points[-1]
    den=((b[0]-a[0])**2+(b[1]-a[1])**2)**.5
    distances=[abs((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))/(den or 1) for p in points]
    index=max(range(len(points)),key=distances.__getitem__)
    if distances[index] <= tolerance: return [a,b]
    return simplify(points[:index+1],tolerance)[:-1]+simplify(points[index:],tolerance)


def remove_rasters(root, ident, original_png, crop_box):
    """Handle only two inspected exceptions; never relabel embedded rasters as vectors."""
    images = list(root.iter(f'{{{SVG}}}image'))
    if not images: return []
    if ident == 'image253':
        # The three original embedded objects are uniform one-pixel swatches.
        for image in images:
            href=image.get(f'{{{XLINK}}}href') or image.get('href')
            pixels=Image.open(io.BytesIO(base64.b64decode(href.split(',',1)[1]))).convert('RGBA')
            colors=set(pixels.get_flattened_data())
            if pixels.size != (1,1) or len(colors) != 1:
                raise ValueError('Unexpected raster in image253')
            r,g,b,a=next(iter(colors))
            image.tag=f'{{{SVG}}}rect'
            for key in (f'{{{XLINK}}}href','href','preserveAspectRatio'):
                image.attrib.pop(key,None)
            image.set('fill',f'rgb({r},{g},{b})')
            image.set('fill-opacity',str(a/255))
        return ['Three inspected uniform 1-by-1 pixel swatches replaced by equivalent SVG rectangles.']
    if ident != 'image1':
        raise ValueError(f'Unexpected raster content in {ident}; preserve the original')
    # The left waveform is four raster fragments. Trace a polyline from its
    # visible centreline, not a guessed sine function or implicit exact curve.
    pixels=Image.open(original_png).convert('L')
    points=[]
    for x in range(0, min(700,pixels.width)):
        ys=[y for y in range(0, min(205,pixels.height)) if pixels.getpixel((x,y)) < 150]
        if ys:
            points.append([crop_box[0]+x/3, crop_box[1]+sum(ys)/len(ys)/3])
    if len(points) < 600:
        raise ValueError('Unexpected image1 waveform bounds')
    points=simplify(points,.20)
    ids={image.get('id') for image in images}
    for parent in root.iter():
        for child in list(parent):
            href=child.get(f'{{{XLINK}}}href') or child.get('href')
            if child.tag == f'{{{SVG}}}image' or (href and href.startswith('#') and href[1:] in ids):
                parent.remove(child)
    ET.SubElement(root,f'{{{SVG}}}polyline',{'id':'traced-waveform','points':' '.join(f'{x:.4f},{y:.4f}' for x,y in points),
                    'fill':'none','stroke':'black','stroke-width':'.8','stroke-linejoin':'round'})
    return ['Waveform traced from raster centreline with 0.20-point simplification tolerance. Approximate shape only; no exact function inferred.']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkpoints',type=Path)
    parser.add_argument('--pdftocairo',default='pdftocairo')
    parser.add_argument('--catalog',type=Path,default=Path(__file__).parent/'gat-catalog.json')
    parser.add_argument('--output',type=Path,default=Path(__file__).parent/'reconstructions')
    args=parser.parse_args()
    checkpoint=args.checkpoints.resolve(); output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    catalog=json.loads(args.catalog.read_text())
    source_assets={a['id']:a for a in catalog['assets']}
    atlas=json.loads((checkpoint/'atlas.json').read_text())
    semantics=json.loads((Path(__file__).parent/'annotated-math.json').read_text())
    coordinate_givens=json.loads((Path(__file__).parent/'coordinate-givens.json').read_text())
    pdf_path=checkpoint/'atlas.pdf';reader=PdfReader(pdf_path);figures=figure_boxes(reader)
    assert len(figures)==len(atlas)
    summary=[];pdf_hash=sha(pdf_path)
    with pdfplumber.open(pdf_path) as pdf, tempfile.TemporaryDirectory() as temporary:
        for item,(page_index,box) in zip(atlas,figures):
            ident=Path(item['file']).stem
            asset=source_assets[ident]
            if asset['classification']['category'] in ('formula','network','screenshot'):continue
            original=(args.catalog.parent/asset['source']).resolve()
            if sha(original) != asset['sha256']:raise ValueError(f'Changed source {ident}')
            l,b,r,t=box; height=float(reader.pages[page_index].mediabox.height)
            # Match the exact integer-pixel crop used for the retained PNGs.
            x0=max(0,int(l*3)-3)/3;y0=max(0,int((height-t)*3)-3)/3
            x1=(int(r*3)+3)/3;y1=(int((height-b)*3)+3)/3
            crop=[x0,y0,x1-x0,y1-y0]
            png=Image.open(original)
            assert png.size == (round(crop[2]*3),round(crop[3]*3))
            svg_path=Path(temporary)/f'{ident}.svg'
            subprocess.run([args.pdftocairo,'-svg','-f',str(page_index+1),'-l',str(page_index+1),str(pdf_path),str(svg_path)],check=True,capture_output=True)
            root=ET.parse(svg_path).getroot()
            notes=remove_rasters(root,ident,original,crop)
            # Stable IDs make individual drawing objects addressable by future editors.
            for index,node in enumerate(root.iter()):
                if node is not root and not node.get('id'):node.set('id',f'primitive-{index:04}')
            page=pdf.pages[page_index]
            labels=[{'id':f'label-{i:04}','text':c['text'],'bbox_pt':[c['x0'],c['top'],c['x1'],c['bottom']],
                     'font':c['fontname'],'size':c['size']} for i,c in enumerate(page.chars)]
            primitives=[]
            for i,obj in enumerate(page.lines+page.rects+page.curves):
                primitives.append({'id':f'drawing-{i:04}',**{k:obj[k] for k in ('object_type','x0','x1','top','bottom','path','pts','linewidth','stroke','fill','stroking_color','non_stroking_color') if k in obj}})
            scene={'version':1,'kind':'vector','source_asset_id':ident,'title':f'Recovered drawing of GAT {ident}',
                   'description':'Source vector paths preserved. Drawing positions do not imply exact mathematical coordinates or constraints.',
                   'view_box':crop,'coordinate_meaning':'PDF drawing points, top-left origin; original PDF transforms retained within SVG elements.',
                   'representation_level':'annotated-math' if ident in semantics else 'drawing-primitives',
                   'provenance':{'atlas_sha256':pdf_hash,'atlas_page':page_index+1,'original_asset_sha256':asset['original_sha256'],
                                 'png_sha256':asset['sha256'],'method':'Poppler SVG extraction from saved vector atlas; exact retained PNG crop'},
                   'elements':[encode(child) for child in root],
                   'labels':labels,'source_drawing_primitives':primitives,
                   'label_review':'Extracted PDF text may contain legacy symbol encodings; SVG glyph outlines preserve the visible labels.',
                   'notes':notes,'review':'needs_review'}
            if ident in semantics:scene['semantics']=semantics[ident]
            if ident in coordinate_givens:scene['coordinate_givens']=coordinate_givens[ident]
            write(output/f'{ident}.scene.json',scene)
            (output/f'{ident}.svg').write_text(render(scene))
            if ident in semantics:write(output/f'{ident}.math.json',latex_records(scene))
            summary.append({'id':ident,'atlas_page':page_index+1,'paths':len(primitives),'labels':len(labels),
                            'representation_level':scene['representation_level'],'notes':notes})
            page.close()
    write(output/'recovery-report.json',{'atlas_sha256':pdf_hash,'assets':summary})
    print(json.dumps({'recovered_assets':len(summary),'annotated_math':sum(x['representation_level']=='annotated-math' for x in summary)}))


if __name__=='__main__':main()
