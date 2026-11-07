import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pipeline
import scene


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'source.png').write_bytes(b'original source bytes')
        self.catalog = {'version':1, 'document':{'sha256':'document-hash'}, 'assets':[
            {'id':'figure', 'source':'source.png', 'sha256':pipeline.sha(self.root/'source.png'),
             'classification':pipeline.classify(), 'conversion':pipeline.unconverted()}],
            'placements':[{'id':'p1','asset_id':'figure','page':1,'bbox_pt':[0,0,10,10]}]}
        self.catalog_path = self.root/'catalog.json'
        pipeline.write(self.catalog_path, self.catalog)

    def test_repeated_placements_count_once_as_asset(self):
        self.catalog['placements'].append({'id':'p2','asset_id':'figure','page':2})
        self.assertEqual(pipeline.validate(self.catalog,self.root)['appearances'],2)
        self.assertEqual(pipeline.counts(self.catalog)['source_assets'],1)

    def test_changed_original_is_rejected(self):
        (self.root/'source.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Source changed'):
            pipeline.validate(self.catalog,self.root)

    def test_invalid_decision_does_not_modify_catalog(self):
        before=self.catalog_path.read_bytes()
        patch={'document_sha256':'document-hash','reviewer':'test', 'assets':[
            {'id':'figure','sha256':self.catalog['assets'][0]['sha256'],'category':'invented-category'}]}
        pipeline.write(self.root/'patch.json',patch)
        with self.assertRaises(ValueError):
            pipeline.apply_decisions(SimpleNamespace(catalog=self.catalog_path,decisions=self.root/'patch.json'))
        self.assertEqual(before,self.catalog_path.read_bytes())

    def test_review_does_not_mark_conversion_verified(self):
        patch={'document_sha256':'document-hash','reviewer':'test','assets':[
            {'id':'figure','sha256':self.catalog['assets'][0]['sha256'],'category':'geometry'}]}
        pipeline.write(self.root/'patch.json',patch)
        pipeline.apply_decisions(SimpleNamespace(catalog=self.catalog_path,decisions=self.root/'patch.json'))
        asset=pipeline.read(self.catalog_path)['assets'][0]
        self.assertEqual(asset['classification']['status'],'reviewed')
        self.assertEqual(asset['conversion']['review'],'needs_review')

    def test_stale_document_and_asset_decisions_are_rejected(self):
        for document_hash,asset_hash in [('other',self.catalog['assets'][0]['sha256']),('document-hash','other')]:
            patch={'document_sha256':document_hash,'reviewer':'test','assets':[{'id':'figure','sha256':asset_hash,'category':'formula'}]}
            pipeline.write(self.root/'patch.json',patch)
            with self.assertRaises(ValueError):
                pipeline.apply_decisions(SimpleNamespace(catalog=self.catalog_path,decisions=self.root/'patch.json'))

    def test_disconnected_groups_are_not_merged(self):
        boxes=[[0,0,10,10],[15,0,20,10],[200,200,210,210]]
        self.assertEqual(pipeline.merge_boxes(boxes),[[0,0,20,10],[200,200,210,210]])

    def test_network_semantics_independent_of_layout(self):
        graph=pipeline.read(pipeline.HERE/'examples/image262.scene.json')
        expected=[[0,1,2,1,0],[1,0,0,0,0],[1,0,0,0,1],[0,1,1,0,0],[0,0,0,1,0]]
        self.assertEqual(scene.adjacency(graph)['matrix'],expected)
        moved=copy.deepcopy(graph)
        moved['nodes'][0]['x']+=30
        self.assertEqual(scene.adjacency(moved),scene.adjacency(graph))
        self.assertNotEqual(scene.render(moved),scene.render(graph))
        tree=ET.fromstring(scene.render(graph))
        self.assertEqual(len(tree.findall('.//*[@data-node]')),5)
        self.assertEqual(len(tree.findall('.//*[@data-edge]')),10)

    def test_loops_and_parallel_edges_are_counted(self):
        graph={'version':1,'kind':'network','width':100,'height':100,
               'nodes':[{'id':'A','label':'<script>','x':50,'y':50,'label_dx':0,'label_dy':20}],
               'edges':[{'id':f'e{i}','from':'A','to':'A','directed':True,'controls':[[0,0],[100,0]]} for i in range(2)]}
        self.assertEqual(scene.adjacency(graph)['matrix'],[[2]])
        self.assertNotIn('<script>',scene.render(graph))
        ET.fromstring(scene.render(graph))


if __name__ == '__main__':
    unittest.main()
