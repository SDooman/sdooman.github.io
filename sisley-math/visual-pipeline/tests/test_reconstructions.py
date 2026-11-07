"""Checks that protect mathematical meaning and the source-preserving contract."""
import copy
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pipeline
import scene
import vector_scene


def read(relative):
    return json.loads((ROOT/relative).read_text())


class ReconstructionTests(unittest.TestCase):
    def test_complete_inventory_and_source_integrity(self):
        catalog=read('gat-catalog.json')
        totals=pipeline.validate(catalog,ROOT)
        self.assertEqual((totals['source_assets'],totals['appearances']),(336,666))
        pending=[a['id'] for a in catalog['assets'] if a['conversion']['status']=='unconverted']
        self.assertEqual(pending,['image15'])
        self.assertEqual(sum(a['conversion']['kind']=='network-scene' for a in catalog['assets']),4)
        self.assertEqual(sum(a['conversion']['kind']=='vector-scene' for a in catalog['assets']),111)

    def test_no_reconstruction_hides_a_bitmap(self):
        catalog=read('gat-catalog.json')
        for asset in catalog['assets']:
            if asset['conversion']['status']!='candidate':continue
            root=ET.parse(ROOT/asset['conversion']['preview']).getroot()
            with self.subTest(asset=asset['id']):
                self.assertFalse(any(e.tag.rsplit('}',1)[-1] in ('image','foreignObject','script') for e in root.iter()))

    def test_duplicate_network_and_printed_adjacency_agree(self):
        first=scene.adjacency(read('examples/image262.scene.json'))
        second=scene.adjacency(read('examples/image279.scene.json'))
        self.assertEqual(first,second)
        matrices=read('annotated-math.json')['image307']['matrices']
        for matrix in matrices:
            self.assertEqual(matrix['entries'],first['matrix'])

    def test_other_networks_preserve_directions_multiplicity_and_loop(self):
        self.assertEqual(scene.adjacency(read('examples/image308.scene.json'))['matrix'],
                         [[0,1,1,2],[0,0,1,0],[1,2,0,1],[0,0,0,0]])
        self.assertEqual(scene.adjacency(read('examples/image329.scene.json'))['matrix'],
                         [[0,0,3,1],[0,0,1,0],[0,1,1,0],[1,1,1,0]])

    def test_transcribed_reflection_identity(self):
        record=read('annotated-math.json')['image291']
        matrices={m['id']:m['entries'] for m in record['matrices']}
        a,b=matrices['reflection'],matrices['pre_images']
        product=[[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
        self.assertEqual(product,matrices['images'])

    def test_tiny_matrix_entries_match_positioned_source_glyphs(self):
        records=read('annotated-math.json')
        for ident in ['image218','image227','image244','image253']:
            labels=read(f'reconstructions/{ident}.scene.json')['labels']
            digits=[label for label in labels if label['text'].isdigit()]
            smallest=min(label['size'] for label in digits)
            entries=sorted([label for label in digits if abs(label['size']-smallest)<.01],
                           key=lambda label:(round(label['bbox_pt'][1],1),label['bbox_pt'][0]))
            matrix=next(m for m in records[ident]['matrices'] if m['id']=='A')
            with self.subTest(asset=ident):
                self.assertEqual([int(label['text']) for label in entries], [v for row in matrix['entries'] for v in row])

    def test_blanks_and_raised_minus_survive_export(self):
        records=read('annotated-math.json')
        for ident in ['image325','image326']:
            blank=next(m for m in records[ident]['matrices'] if m['id']=='blank_image')
            self.assertEqual(blank['entries'],[[None,None],[None,None]])
            self.assertEqual(vector_scene.matrix_latex(blank['entries']).count(r'\phantom{0}'),4)
        self.assertIn('{}^{-}1',vector_scene.matrix_latex([[1,0],[0,-1]]))

    def test_unknown_plot_coordinates_are_not_inferred(self):
        givens=read('coordinate-givens.json')
        self.assertEqual(len(givens),12)
        unknown=[p for p in givens['image92']['points'] if p['id']=='A'][0]
        self.assertIsNone(unknown['coordinates'])
        for ident,record in givens.items():
            self.assertEqual(read(f'reconstructions/{ident}.scene.json')['coordinate_givens'],record)

    def test_vector_validation_rejects_rasters_and_external_resources(self):
        drawing=read('reconstructions/image2.scene.json')
        for element in [{'tag':'image','attributes':{}},
                        {'tag':'use','attributes':{'href':'https://example.test/a.svg'}},
                        {'tag':'path','attributes':{'onclick':'alert(1)'}}]:
            bad=copy.deepcopy(drawing);bad['elements'].append(element)
            with self.assertRaises(ValueError):vector_scene.validate(bad)


if __name__=='__main__':unittest.main()
