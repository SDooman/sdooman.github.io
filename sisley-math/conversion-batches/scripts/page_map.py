"""Map tagged reference figures to document-order placements."""
from pathlib import Path
from pypdf import PdfReader
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'visual-pipeline'))
from recover_vectors import figure_boxes
batch=sys.argv[1];check=ROOT/f'conversion-batches/checkpoints/{batch}'
pdf=PdfReader(check/'reference.pdf');figures=figure_boxes(pdf)
manifest=json.loads((ROOT/f'gat-{batch}/manifest.json').read_text())
assert len(figures)==len(manifest['placements'])
(check/'page-placements.json').write_text(json.dumps({'pages':len(pdf.pages),'figures':[{'page':page+1,'bbox':list(box)} for page,box in figures]},indent=2)+'\n')
print(batch,len(pdf.pages),'reference pages',len(figures),'placements')
