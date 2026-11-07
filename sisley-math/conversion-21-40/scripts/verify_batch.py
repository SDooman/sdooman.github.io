"""Source-based checks for the 21–40 conversion, including discovered regressions."""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import hashlib,json,sys,unittest,re
import xml.etree.ElementTree as E
from lxml import html
import pdfplumber
from mtef import Reader,walk
from transcribe_math import sequence
ROOT=Path(__file__).resolve().parents[2];BOOK=ROOT/'gat-21-40';CHECK=ROOT/'conversion-21-40/checkpoints'
sys.path.insert(0,str(ROOT/'visual-pipeline'))
from vector_scene import render,SVG
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class PreservationChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=read(BOOK/'manifest.json');cls.rows=read(CHECK/'embedded-pdfs.json')
        cls.trees=read(CHECK/'mtef-trees.json');cls.formulas={a['id']:a for a in read(BOOK/'formula-transcriptions.json')['assets']}
        cls.semantics=read(BOOK/'semantic-records.json');cls.decisions=read(ROOT/'conversion-21-40/visual-decisions.json')['assets']
    def test_originals_and_embedded_pdfs(self):
        self.assertEqual(self.manifest['source_sha256'],sha(ROOT/'source/GAT-21-40.docx'))
        with ZipFile(ROOT/'source/GAT-21-40.docx') as z:
            for row in self.rows:
                ident=row['id'];original=BOOK/'assets/originals'/f'{ident}.emf'
                self.assertEqual(original.read_bytes(),z.read(row['original']))
                self.assertEqual(sha(original),row['emf_sha256'])
                self.assertEqual(sha(BOOK/'assets/source-pdf'/f'{ident}.pdf'),row['pdf_sha256'])
    def test_native_equations_replay(self):
        self.assertEqual(len(self.trees),435)
        versions=Counter()
        for ident,tree in self.trees.items():
            data=(BOOK/'assets/ole'/f'{ident}.mtef').read_bytes();versions[data[0]]+=1
            self.assertEqual(Reader(data).parse(),tree)
            self.assertEqual(sequence(tree),self.formulas[ident]['latex'])
        self.assertEqual(versions,{2:430,4:5})
    def test_formula_glyph_inventory_against_source_pdf(self):
        for row in self.rows:
            ident=row['id']
            if ident not in self.trees:continue
            actual=Counter(chr(n['code']) for n in walk(self.trees[ident]) if n['type']==2 and n['face'] not in (4,5,11,22) and n['code']<128 and (chr(n['code']).isalnum() or chr(n['code']) in '=+'))
            source=Counter(c for c in row['text'] if c.isascii() and (c.isalnum() or c in '=+'))
            self.assertEqual(actual,source,ident)
    def test_legacy_raised_minus_and_exercise_blanks(self):
        # C5 was visually verified as a raised minus in all eight affected PDFs.
        affected={'image102','image208','image210','image211','image212','image213','image215','image364'}
        found=set()
        for ident,tree in self.trees.items():
            if any(n['type']==2 and n['code']==197 for n in walk(tree)):
                found.add(ident);self.assertNotIn(r'\approx',self.formulas[ident]['latex']);self.assertIn(r'{}^{-}',self.formulas[ident]['latex'])
        self.assertEqual(found,affected)
        self.assertIn(r'\hspace{1.25em}',self.formulas['image533']['latex'])
        self.assertIn(r'\hspace{2.25em}',self.formulas['image533']['latex'])
        self.assertTrue(all(c is None for row in self.semantics['image3']['entries'] for c in row))
        self.assertIsNone(self.semantics['image205']['rows'][0][1])
    def test_vectors_and_retained_rasters(self):
        scenes=list((BOOK/'assets/scenes').glob('*.scene.json'));self.assertEqual(len(scenes),105)
        for path in scenes:
            scene=read(path);ident=scene['source_asset_id'];self.assertEqual(render(scene),(BOOK/'assets/vectors'/f'{ident}.svg').read_text())
            self.assertEqual(scene['provenance']['pdf_sha256'],sha(BOOK/'assets/source-pdf'/f'{ident}.pdf'))
        retained={d['id'] for d in self.decisions if d['contains_raster']}
        self.assertEqual(retained,{'image133','image175','image430','image450','image453','image462'})
        for ident in retained:self.assertTrue(list(E.parse(BOOK/'assets/source-svg'/f'{ident}.svg').getroot().iter('{'+SVG+'}image')))
    def test_table_digits_against_positioned_source_text(self):
        tables={k:v for k,v in self.semantics.items() if v['kind']=='table'};self.assertEqual(len(tables),16)
        for ident,value in tables.items():
            self.assertTrue(all(len(row)==len(value['headers']) for row in value['rows']))
            with pdfplumber.open(BOOK/'assets/source-pdf'/f'{ident}.pdf') as pdf:
                chars=pdf.pages[0].dedupe_chars().chars;actual=Counter(c['text'] for c in chars if c['text'].isdigit())
            content=''.join(str(c) for row in value['rows'] for c in row if c is not None)+''.join(value['headers']);title=value.get('title') or ''
            # The source PDF for 464 draws its entire table twice; the title is once.
            if ident=='image464':content*=2
            expected=Counter(c for c in content+title if c.isdigit())
            self.assertEqual(actual,expected,ident)
        self.assertEqual(self.semantics['image431']['rows'],self.semantics['image449']['rows'])
        self.assertEqual(self.semantics['image397']['rows'],self.semantics['image429']['rows'])
        self.assertEqual(self.semantics['image397']['rows'],self.semantics['image465']['rows'])
    def test_network_directionality_and_blank_matrix(self):
        network=self.semantics['image2'];edges=[(x['from'],x['to']) for x in network['edges']]
        self.assertEqual(len(network['nodes']),5);self.assertEqual(len(edges),13)
        self.assertIn(('D','SE'),edges);self.assertNotIn(('SE','D'),edges)
        self.assertIn(('NY','SL'),edges);self.assertIn(('SL','NY'),edges)
        self.assertEqual(self.semantics['image3']['row_labels'],['D','LA','NY','SL','SE'])
    def test_assignment_question_and_placement_coverage(self):
        self.assertEqual([x['assignment'] for x in self.manifest['assignments']],list(range(21,41)))
        questions=self.manifest['questions'];self.assertEqual(len(questions),175);self.assertEqual(len({q['id'] for q in questions}),175)
        roman=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI']
        for a in range(21,41):
            labels=[q['label'] for q in questions if q['assignment']==a];self.assertEqual(labels,roman[:len(labels)])
        placements=self.manifest['placements'];self.assertEqual(len(placements),546)
        self.assertEqual(Counter(p['representation'] for p in placements),{'latex':435,'svg':89,'table':16,'image':6})
        self.assertEqual(len(self.decisions),546);self.assertTrue(all(p['reference_page'] in range(1,96) for p in placements))
    def test_review_and_reading_links_and_targets(self):
        for name in ('GAT-21-40.html','GAT-21-40-changes.html','media-review.html','conversion-report.html'):
            tree=html.parse(str(BOOK/name));ids=tree.xpath('//@id');self.assertEqual(len(ids),len(set(ids)),name)
            for link in tree.xpath('//@src|//@href|//@data-source'):
                if link.startswith(('http:','https:','data:','mailto:')):continue
                filename,sep,anchor=link.partition('#');target=BOOK/filename.split('?')[0] if filename else BOOK/name
                self.assertTrue(target.exists(),(name,link))
                if anchor and target.suffix=='.html':self.assertTrue(html.parse(str(target)).xpath('//*[@id=$id]',id=anchor),(name,link))
            for control in tree.xpath('//@aria-controls'):self.assertIn(control,ids)
            if name.endswith('-changes.html'):
                self.assertEqual(len(tree.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," changed-math ")]')),435)
                self.assertEqual(len(tree.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," changed-graph ")]')),111)
            if name=='GAT-21-40.html':self.assertEqual(len(tree.xpath('//table')),16)

if __name__=='__main__':unittest.main(verbosity=2)
