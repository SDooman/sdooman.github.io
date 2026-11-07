import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import katex from 'katex';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),book=path.join(root,'gat-21-40');
const read=name=>JSON.parse(fs.readFileSync(path.join(book,name),'utf8'));
const manifest=read('manifest.json'),formulas=read('formula-transcriptions.json').assets,semantic=read('semantic-records.json');
assert.equal(formulas.length,435);assert.equal(manifest.questions.length,175);assert.equal(manifest.placements.length,546);
for(const a of formulas)katex.renderToString(a.latex,{throwOnError:true,strict:'error',trust:false});
for(const a of Object.values(semantic))for(const e of a.expressions||[])katex.renderToString(e.latex,{throwOnError:true,strict:'error',trust:false});
const count=(s,re)=>[...s.matchAll(re)].length;
for(const file of ['GAT-21-40.html','GAT-21-40-changes.html','media-review.html','conversion-report.html']){
 const s=fs.readFileSync(path.join(book,file),'utf8');
 for(const [,link] of s.matchAll(/(?:href|src|data-source)="([^"]+)"/g)){
  if(/^(https?:|#|data:|mailto:)/.test(link))continue;
  assert.ok(fs.existsSync(path.resolve(book,link.split(/[?#]/)[0])),`${file}: missing ${link}`);
 }
 const ids=[...s.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1]);assert.equal(new Set(ids).size,ids.length,`${file}: duplicate IDs`);
 for(const [,code] of s.matchAll(/<script>([\s\S]*?)<\/script>/g))new vm.Script(code,{filename:file});
 assert.ok(!s.includes('katex-error'));
 if(file==='GAT-21-40.html'){
  assert.equal(count(s,/<table>/g),16);assert.equal(count(s,/<img /g),95);
  for(const q of manifest.questions)assert.ok(ids.includes(q.id));
 }
 if(file==='GAT-21-40-changes.html'){
  assert.equal(count(s,/class="changed-math"/g),435);assert.equal(count(s,/class="changed-graph/g),111);
  assert.equal(count(s,/class="toggle-diagram-math"/g),29);
 }
 if(file==='media-review.html')assert.equal(count(s,/class="media-card/g),546);
}
console.log(JSON.stringify({batch:'21–40',assignments:20,questions:175,media:546,latex:435,tables:16,svg_drawings:89,retained_originals:6,local_links:'pass',math_syntax:'pass',review_scripts:'syntax-checked'}));
