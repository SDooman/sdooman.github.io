#!/usr/bin/env python3
"""Local, reviewable visual inventory. Run --help; no remote OCR or model calls."""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
from urllib.parse import quote

from scene import render as render_scene, adjacency, validate as validate_scene
from vector_scene import render as render_vector, validate as validate_vector

HERE = Path(__file__).resolve().parent
TAXONOMY = json.loads((HERE / 'taxonomy.json').read_text())['categories']
CATEGORIES = {c['id']: c for c in TAXONOMY}
RETAINED_CATEGORIES = ['geometry', 'reflection_translation', 'shapes_symmetry',
                       'coordinate_plot', 'rotation', 'annotated_matrix', 'network',
                       'calculation_flow', 'map', 'screenshot']


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Replace only after the complete JSON has been serialized.
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path, directory):
    return Path(os.path.relpath(Path(path).resolve(), Path(directory).resolve())).as_posix()


def local(base, name):
    if not isinstance(name, str) or not name or '://' in name or name.startswith('data:'):
        raise ValueError('Expected a local file reference')
    return (base / name).resolve()


def require_new(path):
    if Path(path).exists():
        raise ValueError(f'Refusing to overwrite {path}; choose a new output path')


def classify(category='unclassified', status='unclassified', method='pending visual review'):
    return {'category': category, 'status': status, 'method': method, 'notes': ''}


def unconverted():
    return {'status': 'unconverted', 'kind': 'image', 'review': 'needs_review'}


def counts(catalog):
    placements = Counter(p['asset_id'] for p in catalog['placements'])
    categories = Counter(a['classification']['category'] for a in catalog['assets'])
    return {'source_assets': len(catalog['assets']),
            'distinct_file_hashes': len({a['sha256'] for a in catalog['assets']}),
            'appearances': len(catalog['placements']),
            'categories': [{'id': key, 'assets': value,
                            'appearances': sum(placements[a['id']] for a in catalog['assets']
                                               if a['classification']['category'] == key)}
                           for key, value in sorted(categories.items())]}


def validate(catalog, base):
    if catalog.get('version') != 1:
        raise ValueError('Unsupported catalog version')
    if not catalog.get('document', {}).get('sha256'):
        raise ValueError('Missing source document hash')
    document = catalog['document']
    if document.get('source') and sha(local(base, document['source'])) != document['sha256']:
        raise ValueError('Source document changed')
    assets = catalog['assets']
    ids = [a['id'] for a in assets]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate asset IDs')
    for asset in assets:
        path = local(base, asset['source'])
        if sha(path) != asset['sha256']:
            raise ValueError(f'Source changed: {asset["id"]}')
        if asset.get('original') and sha(local(base, asset['original'])) != asset['original_sha256']:
            raise ValueError(f'Original changed: {asset["id"]}')
        cls = asset['classification']
        if cls['category'] not in CATEGORIES or cls['status'] not in ('unclassified', 'proposed', 'reviewed'):
            raise ValueError('Invalid classification')
        if cls['status'] == 'reviewed' and cls['category'] == 'unclassified':
            raise ValueError('Unclassified assets cannot be reviewed classifications')
        conv = asset['conversion']
        if conv['status'] not in ('unconverted', 'candidate', 'converted') or conv['review'] not in ('needs_review', 'verified'):
            raise ValueError('Invalid conversion state')
        if conv['kind'] not in ('image', 'latex', 'network-scene', 'vector-scene'):
            raise ValueError('Converter not implemented; preserve the image and record a proposed target in the taxonomy')
        if conv['status'] == 'unconverted' and (conv['kind'] != 'image' or conv['review'] == 'verified'):
            raise ValueError('Unconverted assets must retain an image and need review')
        if conv['status'] != 'unconverted' and conv['kind'] == 'image':
            raise ValueError('Converted assets need a machine-readable representation')
        if conv['kind'] == 'latex' and (not isinstance(conv.get('latex'), str) or not conv['latex'].strip()):
            raise ValueError('Missing LaTeX string')
        if conv['kind'] in ('network-scene','vector-scene'):
            scene = read(local(base, conv['path']))
            (validate_scene if conv['kind']=='network-scene' else validate_vector)(scene)
            if scene.get('source_asset_id', asset['id']) != asset['id']:
                raise ValueError('Scene references a different source asset')
            expected = (render_scene if conv['kind']=='network-scene' else render_vector)(scene)
            if local(base, conv['preview']).read_text() != expected:
                raise ValueError('Scene preview is stale; rerun the corresponding renderer')
        if conv['review'] == 'verified' and not conv.get('review_evidence'):
            raise ValueError('Verified conversions need review evidence')
    placement_ids = [p['id'] for p in catalog['placements']]
    if len(placement_ids) != len(set(placement_ids)):
        raise ValueError('Duplicate placement IDs')
    used = set()
    for placement in catalog['placements']:
        if placement['asset_id'] not in ids:
            raise ValueError('Placement references missing asset')
        used.add(placement['asset_id'])
        box = placement.get('bbox_pt')
        if box is not None and (len(box) != 4 or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in box)
                                or box[0] >= box[2] or box[1] >= box[3]):
            raise ValueError('Invalid placement bounding box')
    if used != set(ids):
        raise ValueError('Every asset must have at least one placement')
    return counts(catalog)


def import_gat(args):
    require_new(args.output)
    book, output = Path(args.book).resolve(), Path(args.output).resolve()
    manifest, transcriptions = read(book / 'manifest.json'), read(book / 'formula-transcriptions.json')
    taxonomy = read(args.decisions)['categories']
    if len(taxonomy) != len(RETAINED_CATEGORIES):
        raise ValueError('Unexpected retained taxonomy')
    mapping = {}
    for group, category in zip(taxonomy, RETAINED_CATEGORIES):
        for ident in group['image_ids']:
            if ident in mapping:
                raise ValueError('Overlapping taxonomy')
            mapping[ident] = category
    original_assets = {a['browser_asset']: a for a in manifest['unique_assets']}
    catalog = {'version': 1, 'document': {'title': 'GAT assignments 1-20',
                'filename': manifest['source_filename'], 'sha256': manifest['source_sha256'],
                'pagination_note': manifest['pagination_note'],
                'reference_page_count': manifest['reference_render_page_count']},
               'coverage': {'status': 'legacy_inventory_imported',
                            'note': 'All 336 source graphics classified; source pagination and mathematical fidelity are not fully verified.'},
               'assets': [], 'placements': [], 'pages': []}
    seen = {}
    for item in transcriptions['assets']:
        ident = item['image_id']
        category = 'formula' if item['status'] == 'latex' else mapping.pop(ident)
        source = book / item['source_asset']
        digest = sha(source)
        original = original_assets[item['source_asset']]
        asset = {'id': ident, 'source': rel(source, output.parent), 'sha256': digest,
                 'original': rel(book / original['original'], output.parent),
                 'original_sha256': original['sha256_original'],
                 'classification': classify(category, 'reviewed', 'prior assistant visual review; imported taxonomy'),
                 'conversion': unconverted(),
                 'issues': item.get('source_image_issues', []) + ([item['note']] if item.get('note') else [])}
        if digest in seen:
            asset['duplicate_of'] = seen[digest]
        seen.setdefault(digest, ident)
        if item['status'] == 'latex':
            asset['conversion'] = {'status': 'converted', 'kind': 'latex', 'latex': item['latex'],
                                   'review': 'needs_review',
                                   'evidence': 'Existing KaTeX syntax and source-glyph checks; not a claim of complete mathematical proofreading.'}
        catalog['assets'].append(asset)
    if mapping:
        raise ValueError('Taxonomy contains assets absent from the source')
    by_source = {item['source_asset']: item['image_id'] for item in transcriptions['assets']}
    for p in manifest['placements']:
        catalog['placements'].append({'id': p['id'], 'asset_id': by_source[p['asset']],
            'page': p['reference_page'], 'bbox_pt': p['bbox_pt'],
            'coordinate_system': 'pdf-bottom-left', 'question_id': p['question_id']})
    validate(catalog, output.parent)
    write(output, catalog)
    print(json.dumps(counts(catalog)))


def merge_boxes(boxes, gap=6):
    """Conservative candidate grouping, NOT semantic figure segmentation."""
    groups = []
    for box in boxes:
        box = list(box)
        while True:
            matches = [i for i, other in enumerate(groups)
                       if box[0] <= other[2] + gap and other[0] <= box[2] + gap
                       and box[1] <= other[3] + gap and other[1] <= box[3] + gap]
            if not matches:
                break
            for i in reversed(matches):
                other = groups.pop(i)
                box = [min(box[0], other[0]), min(box[1], other[1]),
                       max(box[2], other[2]), max(box[3], other[3])]
        groups.append(box)
    return sorted(groups, key=lambda b: (b[1], b[0]))


def ingest_pdf(args):
    import pdfplumber
    from PIL import ImageDraw
    source, output = Path(args.pdf).resolve(), Path(args.output).resolve()
    require_new(output)
    # Validate input and selections before making the output directory.
    manual = read(args.regions) if args.regions else []
    with pdfplumber.open(source) as pdf:
        selected = set(map(int, args.pages.split(','))) if args.pages else set(range(1, len(pdf.pages) + 1))
        if not selected or not selected.issubset(range(1, len(pdf.pages) + 1)):
            raise ValueError('Page selection must be comma-separated, valid 1-based page numbers')
        for region in manual:
            if region['page'] not in selected or len(region['bbox_pt']) != 4:
                raise ValueError('Manual regions must have four coordinates and belong to selected pages')
        output.mkdir(parents=True)
        for folder in ('assets', 'pages', 'objects'):
            (output / folder).mkdir()
        shutil.copy2(source, output / 'source.pdf')
        catalog = {'version': 1, 'document': {'title': source.stem, 'filename': source.name,
                    'sha256': sha(source), 'source': 'source.pdf', 'reference_page_count': len(pdf.pages)},
                   'coverage': {'status': 'page_review_required', 'processed_pages': sorted(selected),
                      'total_pages': len(pdf.pages),
                      'note': 'Image placements and vector clusters are candidates only. Text-only math, scans, compound figures and clipping require page review; no OCR is run.'},
                   'assets': [], 'placements': [], 'pages': []}
        by_hash = {}
        for page_number in sorted(selected):
            page = pdf.pages[page_number-1]
            bounds = page.bbox
            def box(obj):
                return [obj['x0'], obj['top'], obj['x1'], obj['bottom']]
            def clip(b, padding=0):
                return [max(bounds[0], b[0]-padding), max(bounds[1], b[1]-padding),
                        min(bounds[2], b[2]+padding), min(bounds[3], b[3]+padding)]
            vectors = page.lines + page.rects + page.curves
            candidates = [(box(obj), 'embedded_image') for obj in page.images]
            candidates += [(b, 'vector_cluster') for b in merge_boxes([box(obj) for obj in vectors])]
            candidates += [(r['bbox_pt'], 'manual_region') for r in manual if r['page'] == page_number]
            picture = page.to_image(resolution=args.dpi, force_mediabox=True).original.convert('RGB')
            # PageImage pixel coordinates are relative to the media box at this DPI.
            sx, sy = picture.width/(bounds[2]-bounds[0]), picture.height/(bounds[3]-bounds[1])
            def pixel(b):
                return [(b[0]-bounds[0])*sx, (b[1]-bounds[1])*sy,
                        (b[2]-bounds[0])*sx, (b[3]-bounds[1])*sy]
            picture.save(output / f'pages/page-{page_number:04}.png')
            overlay = picture.copy()
            draw = ImageDraw.Draw(overlay)
            page_placements = []
            for number, (raw_box, detection) in enumerate(candidates, 1):
                b = clip(raw_box, 3 if detection == 'vector_cluster' else 0)
                if b[0] >= b[2] or b[1] >= b[3]:
                    continue
                pid = f'p{page_number:04}-r{number:04}'
                crop = picture.crop(tuple(int(round(x)) for x in pixel(b)))
                if not crop.width or not crop.height:
                    continue
                # Hash normalized RGB pixels and dimensions, independent of PNG encoder metadata.
                digest = hashlib.sha256(str(crop.size).encode() + crop.tobytes()).hexdigest()
                ident = by_hash.get(digest)
                if ident is None:
                    ident = 'visual-' + digest[:20]
                    by_hash[digest] = ident
                    path = output / f'assets/{ident}.png'
                    crop.save(path)
                    fraction = (b[2]-b[0])*(b[3]-b[1]) / (page.width*page.height)
                    cls = classify('scan', 'proposed', 'image covers over 70% of page; inspect before accepting') if detection == 'embedded_image' and fraction > .7 else classify()
                    catalog['assets'].append({'id': ident, 'source': rel(path, output), 'sha256': sha(path),
                        'pixel_sha256': digest, 'classification': cls, 'conversion': unconverted(),
                        'issues': ['Rendered page crop; not an isolated original image stream. Check the full page for nearby labels and clipping.']})
                catalog['placements'].append({'id': pid, 'asset_id': ident, 'page': page_number,
                    'bbox_pt': b, 'coordinate_system': 'pdf-top-left', 'page_origin_pt': list(bounds[:2]),
                    'detection': detection, 'nearby_text': page.crop(tuple(clip(b, 18))).extract_text() or ''})
                page_placements.append(pid)
                draw.rectangle(pixel(b), outline='#ca283e', width=2)
            overlay.save(output / f'pages/page-{page_number:04}-regions.png')
            # Keep vector drawing instructions and positioned characters, not just a raster crop.
            object_fields = ('object_type','x0','x1','top','bottom','text','fontname','size',
                             'path','pts','linewidth','stroke','fill','stroking_color','non_stroking_color')
            write(output / f'objects/page-{page_number:04}.json',
                  [{k: obj[k] for k in object_fields if k in obj} for obj in page.chars + vectors])
            catalog['pages'].append({'page': page_number, 'bbox_pt': list(bounds),
                'preview': f'pages/page-{page_number:04}.png', 'regions_preview': f'pages/page-{page_number:04}-regions.png',
                'objects': f'objects/page-{page_number:04}.json', 'review': 'needs_review',
                'embedded_images': len(page.images), 'vector_primitives': len(vectors),
                'text_characters': len(page.chars), 'placement_ids': page_placements})
            page.close()
        validate(catalog, output)
        write(output / 'catalog.json', catalog)
        print(json.dumps(counts(catalog)))


def apply_decisions(args):
    path = Path(args.catalog).resolve()
    catalog = read(path)
    patch = read(args.decisions)
    if patch.get('document_sha256') != catalog['document']['sha256']:
        raise ValueError('Decisions belong to a different source document')
    if not patch.get('reviewer', '').strip():
        raise ValueError('Name the reviewer')
    assets = {a['id']: a for a in catalog['assets']}
    seen = set()
    for decision in patch['assets']:
        ident = decision['id']
        if ident in seen:
            raise ValueError('Duplicate decision')
        seen.add(ident)
        asset = assets[ident]
        if decision['sha256'] != asset['sha256']:
            raise ValueError(f'Stale decision for {ident}')
        if 'category' in decision:
            category = decision['category']
            asset['classification'] = classify(category, 'unclassified' if category == 'unclassified' else 'reviewed', 'review decision')
            asset['classification'].update({'reviewer': patch['reviewer'], 'notes': decision.get('notes', '')})
        if 'conversion' in decision:
            asset['conversion'] = copy.deepcopy(decision['conversion'])
    # Transactional: validate every decision and file before replacing the catalog.
    validate(catalog, path.parent)
    write(path, catalog)
    print(json.dumps(counts(catalog)))


def report(args):
    path = Path(args.catalog).resolve()
    output = Path(args.output).resolve()
    catalog = read(path)
    validate(catalog, path.parent)
    display = copy.deepcopy(catalog)
    for asset in display['assets']:
        asset['source'] = quote(rel(local(path.parent, asset['source']), output.parent), safe='/')
        for field in ('preview', 'path'):
            if field in asset['conversion']:
                asset['conversion'][field] = quote(rel(local(path.parent, asset['conversion'][field]), output.parent), safe='/')
    for page in display.get('pages', []):
        for field in ('preview', 'regions_preview', 'objects'):
            page[field] = quote(rel(local(path.parent, page[field]), output.parent), safe='/')
    payload = json.dumps({'catalog': display, 'taxonomy': TAXONOMY}, ensure_ascii=False).replace('<', '\\u003c')
    template = (HERE / 'review-template.html').read_text()
    output.write_text(template.replace('__CATALOG_DATA__', payload).replace('__REVIEW_SCRIPT__', (HERE / 'review.js').read_text()))
    print(str(output))


def render(args):
    scene = read(args.scene)
    Path(args.output).write_text(render_scene(scene))
    if args.adjacency:
        write(args.adjacency, adjacency(scene))


def render_vector_command(args):
    from vector_scene import latex_records
    scene = read(args.scene)
    Path(args.output).write_text(render_vector(scene))
    if args.math:
        write(args.math, latex_records(scene))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('import-gat', help='Import existing LaTeX and retained-image classifications')
    p.add_argument('book'); p.add_argument('decisions'); p.add_argument('output'); p.set_defaults(run=import_gat)
    p = commands.add_parser('ingest-pdf', help='Inventory raster placements, vector candidates and pages for review')
    p.add_argument('pdf'); p.add_argument('output'); p.add_argument('--pages', help='Comma-separated 1-based page numbers; default all')
    p.add_argument('--regions', help='Additional regions JSON: [{"page":1,"bbox_pt":[x0,top,x1,bottom]}]')
    p.add_argument('--dpi', type=int, default=144); p.set_defaults(run=ingest_pdf)
    p = commands.add_parser('apply', help='Apply reviewed classifications or authored conversion candidates')
    p.add_argument('catalog'); p.add_argument('decisions'); p.set_defaults(run=apply_decisions)
    p = commands.add_parser('report', help='Build an offline, filterable visual review page')
    p.add_argument('catalog'); p.add_argument('output'); p.set_defaults(run=report)
    p = commands.add_parser('validate', help='Check source hashes, states, references and totals')
    p.add_argument('catalog'); p.set_defaults(run=lambda a: print(json.dumps(validate(read(a.catalog), Path(a.catalog).resolve().parent))))
    p = commands.add_parser('render-network', help='Render a directed multigraph scene to SVG and adjacency data')
    p.add_argument('scene'); p.add_argument('output'); p.add_argument('--adjacency'); p.set_defaults(run=render)
    p = commands.add_parser('render-vector', help='Render an editable vector scene; optionally export its structured math')
    p.add_argument('scene'); p.add_argument('output'); p.add_argument('--math'); p.set_defaults(run=render_vector_command)
    args = parser.parse_args()
    if getattr(args, 'dpi', 144) < 36 or getattr(args, 'dpi', 144) > 600:
        parser.error('DPI must be between 36 and 600')
    try:
        args.run(args)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
