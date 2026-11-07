"""Source-based integrity checks and regressions discovered during conversion."""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import hashlib,json,sys,unittest,re
import xml.etree.ElementTree as E
from lxml import html,etree
import pdfplumber
from mtef import Reader,walk
from transcribe_math import sequence
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'visual-pipeline'))
from vector_scene import render,SVG
BATCHES=['41-58','59-80','81-100','101-119']
def read(p):return json.loads(p.read_text())
def digest(b):return hashlib.sha256(b).hexdigest()
def ascii_inventory(s):return Counter(c for c in s if c.isascii() and c.isalnum())
class PreservationChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data={}
  for b in BATCHES:
   book=ROOT/f'gat-{b}';check=ROOT/f'conversion-batches/checkpoints/{b}'
   cls.data[b]={'book':book,'check':check,'manifest':read(book/'manifest.json'),'rows':read(check/'assets.json'),'trees':read(check/'mtef-trees.json'),'formulas':{x['id']:x for x in read(book/'formula-transcriptions.json')['assets']},'semantic':read(book/'semantic-records.json'),'inventory':read(book/'media-inventory.json')}
 def test_original_files_and_unchanged_embedded_media(self):
  for b,d in self.data.items():
   self.assertEqual(d['manifest']['source_sha256'],digest((ROOT/f'source/GAT-{b}.doc').read_bytes()))
   with ZipFile(d['check']/'imported.docx') as z:
    for r in d['rows']:
     raw=(d['book']/'assets/originals'/Path(r['original']).name).read_bytes()
     self.assertEqual(raw,z.read(r['original']));self.assertEqual(digest(raw),r['sha256'])
     if r.get('pdf_sha256'):self.assertEqual(digest((d['book']/f'assets/source-pdf/{r["id"]}.pdf').read_bytes()),r['pdf_sha256'])
 def test_all_native_records_replay_and_offsets(self):
  total=0
  for b,d in self.data.items():
   native=read(d['book']/'native-equations.json')
   for r in d['rows']:
    original=(d['book']/'assets/originals'/Path(r['original']).name).read_bytes()
    for eq in r['native_equations']:
     raw=(d['book']/f'assets/native-math/{eq["id"]}.mtef').read_bytes();i=eq['offset_in_original']
     self.assertEqual(raw,original[i:i+eq['bytes']]);self.assertEqual(digest(raw),eq['sha256'])
     self.assertEqual(Reader(raw).parse(),d['trees'][eq['id']]);self.assertEqual(sequence(d['trees'][eq['id']]),native[eq['id']]['latex']);total+=1
    if r['id'] in d['formulas'] and d['formulas'][r['id']]['method']=='native-equation-tree':
     self.assertEqual(d['formulas'][r['id']]['latex'],native[r['native_equations'][0]['id']]['latex'])
  self.assertEqual(total,1101)
 def test_source_glyph_inventory(self):
  checked=0
  for b,d in self.data.items():
   source=read(d['check']/'quickdraw-equations.json')
   for r in d['rows']:
    if r.get('pict_version')!=1 or len(r['native_equations'])!=1:continue
    tree=d['trees'][r['native_equations'][0]['id']]
    actual=Counter(chr(n['code']) for n in walk(tree) if n['type']==2 and n['face'] not in (4,5,11,22) and n['code']<128 and chr(n['code']).isalnum())
    expected=ascii_inventory(''.join(t['text'] for t in source[r['id']+'.pct']['texts']))
    # In this one source preview a small literal o represents the degree glyph.
    if (b,r['id'])==('59-80','image310'):expected.subtract({'o':1});expected=+expected
    self.assertEqual(actual,expected,(b,r['id']));checked+=1
  self.assertEqual(checked,1026)
 def test_legacy_symbol_and_blank_regressions(self):
  affected=[]
  for b,d in self.data.items():
   native=read(d['book']/'native-equations.json')
   for ident,tree in d['trees'].items():
    degree=sum(n['type']==2 and n['code']==202 for n in walk(tree))
    if degree:self.assertEqual(native[ident]['latex'].count(r'{}^{\circ}'),degree);affected.append((b,ident))
   for table in d['semantic'].values():
    if table['kind']=='table':self.assertTrue(all(len(row)==len(table['headers']) for row in table['rows']))
  self.assertEqual(len(affected),8)
  self.assertIn(r'={} ^{-}11'.replace(' ',''),self.data['81-100']['formulas']['image149']['latex'])
  self.assertIn(r'\frac ba\cdot ',self.data['81-100']['formulas']['image204']['latex'])
  self.assertIn('{cc|c}',self.data['41-58']['formulas']['image78']['latex'])
  self.assertIn("``common sense''",self.data['101-119']['formulas']['image273']['latex'])
  self.assertIn(r'\$',self.data['59-80']['formulas']['image123']['latex'])
  self.assertEqual(self.data['59-80']['semantic']['image4']['rows'][-1],list('gcgfbdea'))
  self.assertEqual(sum(c is None for row in self.data['81-100']['semantic']['image388']['rows'] for c in row),12)
 def test_vectors_are_replayable_and_raster_free(self):
  total=0
  for b,d in self.data.items():
   for p in (d['book']/'assets/scenes').glob('*.scene.json'):
    scene=read(p);ident=scene['source_asset_id'];self.assertEqual(render(scene),(d['book']/f'assets/vectors/{ident}.svg').read_text())
    row=next(x for x in d['rows'] if x['id']==ident);self.assertEqual(scene['provenance']['original_sha256'],row['sha256'])
   for a in d['inventory']['assets']:
    if a['conversion']['kind']=='vector-scene':
     self.assertFalse(list(E.parse(d['book']/a['conversion']['preview']).getroot().iter('{'+SVG+'}image')));total+=1
  self.assertEqual(total,241)
 def test_table_content_against_source_text(self):
  compared=[]
  for b,d in self.data.items():
   for ident,t in d['semantic'].items():
    if t['kind']!='table':continue
    if b=='101-119':continue # Two raster tables were visually transcribed and compared.
    with pdfplumber.open(d['book']/f'assets/source-pdf/{ident}.pdf') as pdf:
     source=''.join(c['text'] for c in pdf.pages[0].dedupe_chars().chars)
    content=''.join(str(v) for row in t['rows'] for v in row if v is not None)+''.join(t['headers'])+(t.get('title') or '')
    self.assertEqual(ascii_inventory(source),ascii_inventory(content),(b,ident));compared.append((b,ident))
  self.assertEqual(len(compared),19)
 def test_complete_text_questions_and_media_coverage(self):
  totals=Counter()
  for b,d in self.data.items():
   m=d['manifest'];first,last=map(int,b.split('-'));self.assertEqual([a['assignment'] for a in m['assignments']],list(range(first,last+1)))
   self.assertEqual(len({q['id'] for q in m['questions']}),len(m['questions']))
   roman=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV']
   for a in m['assignments']:
    labels=[q['label'] for q in m['questions'] if q['assignment']==a['assignment']];self.assertEqual(labels,roman[:len(labels)],(b,a))
   with ZipFile(d['check']/'sized.docx') as z:
    r=etree.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    self.assertEqual(len(''.join(r.xpath('.//w:body//w:t/text()',namespaces=ns))),m['body_text_characters'])
    self.assertEqual(len(r.xpath('.//w:drawing',namespaces=ns)),len(m['placements']))
   self.assertEqual({a['id'] for a in m['assets']},{p['asset_id'] for p in m['placements']})
   self.assertEqual(len({p['id'] for p in m['placements']}),len(m['placements']))
   self.assertTrue(all(1<=p['reference_page']<=m['reference_render_page_count'] for p in m['placements']))
   image_md=(d['check']/'image-based.md').read_text();self.assertEqual(image_md.count('data-placement='),len(m['placements']))
   totals.update(assignments=len(m['assignments']),questions=len(m['questions']),placements=len(m['placements']),assets=len(m['assets']))
  self.assertEqual(dict(totals),{'assignments':79,'questions':714,'placements':2244,'assets':1448})
 def test_review_links_and_control_targets(self):
  cache={}
  def document(p):
   key=str(p.resolve())
   if key not in cache:cache[key]=html.parse(key)
   return cache[key]
  for b,d in self.data.items():
   for name in (f'GAT-{b}.html',f'GAT-{b}-changes.html','media-review.html','conversion-report.html'):
    tree=document(d['book']/name);ids=tree.xpath('//@id');self.assertEqual(len(ids),len(set(ids)))
    for link in tree.xpath('//@src|//@href|//@data-source'):
     if link.startswith(('http:','https:','data:','mailto:')):continue
     filename,sep,anchor=link.partition('#');target=d['book']/filename.split('?')[0] if filename else d['book']/name
     self.assertTrue(target.exists(),(b,name,link))
     if anchor and target.suffix=='.html':self.assertTrue(document(target).xpath('//*[@id=$id]',id=anchor),(b,name,link))
    for target in tree.xpath('//@aria-controls'):self.assertIn(target,ids)
if __name__=='__main__':unittest.main(verbosity=2)
