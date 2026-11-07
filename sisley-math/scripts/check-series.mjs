import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import katex from 'katex';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const expected={'41-58':[164,434,222,9,76,14],'59-80':[201,514,251,7,54,19],'81-100':[190,765,431,3,46,17],'101-119':[159,531,211,2,65,21]};
const count=(s,re)=>[...s.matchAll(re)].length;
for(const [batch,[questions,placements,formulas,tables,vectors,retained]] of Object.entries(expected)){
 const book=path.join(root,'gat-'+batch),read=f=>JSON.parse(fs.readFileSync(path.join(book,f),'utf8'));
 const manifest=read('manifest.json'),inventory=read('media-inventory.json'),math=read('formula-transcriptions.json').assets,semantic=read('semantic-records.json');
 assert.equal(manifest.questions.length,questions);assert.equal(manifest.placements.length,placements);assert.equal(math.length,formulas);assert.equal(inventory.assets.length,formulas+tables+vectors+retained);
 for(const a of [...math,...Object.values(semantic).flatMap(s=>s.expressions||[])])katex.renderToString(a.latex,{throwOnError:true,strict:'error',trust:false});
 for(const file of [`GAT-${batch}.html`,`GAT-${batch}-changes.html`,'media-review.html','conversion-report.html']){
  const s=fs.readFileSync(path.join(book,file),'utf8');
  for(const [,link] of s.matchAll(/(?:href|src|data-source)="([^"]+)"/g)){
   if(/^(https?:|#|data:|mailto:)/.test(link))continue;
   assert.ok(fs.existsSync(path.resolve(book,link.split(/[?#]/)[0])),`${batch}/${file}: missing ${link}`);
  }
  const ids=[...s.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1]);assert.equal(new Set(ids).size,ids.length,`${batch}/${file}: duplicate IDs`);
  for(const [,code] of s.matchAll(/<script>([\s\S]*?)<\/script>/g))new vm.Script(code,{filename:file});
  assert.ok(!s.includes('katex-error'));
  if(file===`GAT-${batch}.html`){
   assert.equal(count(s,/<table>/g),manifest.placements.filter(p=>p.representation==='table').length);
   assert.equal(count(s,/<img /g),manifest.placements.filter(p=>['svg','image'].includes(p.representation)).length);
   for(const q of manifest.questions)assert.ok(ids.includes(q.id),q.id);
  }
  if(file.endsWith('-changes.html')){
   assert.equal(count(s,/class="changed-math"/g),manifest.placements.filter(p=>p.representation==='latex').length);
   assert.equal(count(s,/class="changed-graph/g),manifest.placements.filter(p=>p.representation!=='latex').length);
  }
  if(file==='media-review.html')assert.equal(count(s,/class="media-card/g),inventory.assets.length);
 }
 console.log(JSON.stringify({batch,questions,placements,formulas,tables,vectors,retained,math_syntax:'pass',local_links:'pass',review_scripts:'syntax-checked'}));
}
