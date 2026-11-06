import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import katex from 'katex';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const dir=path.join(root,'gat-1-20');
const read=(name)=>fs.readFileSync(path.join(dir,name),'utf8');
const catalog=JSON.parse(read('formula-transcriptions.json'));
const manifest=JSON.parse(read('manifest.json'));
const md=read('GAT-1-20.md'), html=read('GAT-1-20.html');
const decode=(s)=>s.replace(/&#x([0-9a-f]+);/gi,(_,n)=>String.fromCodePoint(parseInt(n,16))).replace(/&#(\d+);/g,(_,n)=>String.fromCodePoint(+n)).replace(/&quot;/g,'"').replace(/&apos;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
const count=(items)=>{const c=new Map();for(const i of items)c.set(i,(c.get(i)||0)+1);return c;};
const compare=(a,b,message)=>assert.deepEqual([...a].sort(),[...b].sort(),message);
const formulas=catalog.assets.filter(a=>a.status==='latex');
assert.equal(catalog.assets.length,336);
assert.equal(formulas.length,220);
assert.equal(new Set(catalog.assets.map(a=>a.image_id)).size,336);

const expected=new Map();
for(const a of formulas){
  katex.renderToString(a.latex,{throwOnError:true,strict:'error',trust:false});
  expected.set(a.latex,(expected.get(a.latex)||0)+a.occurrences);
  assert.ok(fs.existsSync(path.join(dir,a.source_asset)),`Missing source: ${a.source_asset}`);
}
const annotations=[...html.matchAll(/<annotation encoding="application\/x-tex">([\s\S]*?)<\/annotation>/g)].map(m=>decode(m[1]));
const canonical=annotations.map(s=>expected.has(s)?s:expected.has(s.slice(0,-1))&&/[.,]$/.test(s)?s.slice(0,-1):s);
compare(count(canonical),expected,'Rendered math differs from transcription records');
assert.equal(annotations.length,546);
assert.ok(!html.includes('katex-error'));
assert.ok(!/!\[Equation/.test(md),'Equation image reference remains in Markdown');
assert.equal((md.match(/\$\$/g)||[]).length%2,0);
for(const price of ['$3.00','$5.00','$8.00'])assert.ok(html.includes(price),`Price incorrectly parsed as math: ${price}`);

const imagePaths=[...html.matchAll(/<img\b[^>]*\bsrc="([^"]+)"/g)].map(m=>m[1]);
assert.equal(imagePaths.length,120);
assert.equal(new Set(imagePaths).size,116);
for(const src of imagePaths)assert.ok(fs.existsSync(path.join(dir,src)),`Missing image: ${src}`);
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
assert.equal(new Set(ids).size,ids.length,'Duplicate anchors');
assert.equal(ids.filter(id=>/^gat-\d\d-/.test(id)).length,170);
assert.equal(ids.filter(id=>/^assignment-\d\d$/.test(id)).length,20);
for(const q of manifest.questions)assert.ok(ids.includes(q.id),`Missing question: ${q.id}`);
for(const [,href]of html.matchAll(/\bhref="([^"]+)"/g)){
  if(/^(?:https?:|mailto:)/.test(href))continue;
  const [file,anchor]=href.split('#');
  if(file)assert.ok(fs.existsSync(path.join(dir,file)),`Missing link: ${href}`);
  else if(anchor)assert.ok(ids.includes(anchor),`Missing anchor: ${anchor}`);
}
const css=read('assets/vendor/katex/katex.min.css');
for(const [,font]of css.matchAll(/url\(([^)]+)\)/g))assert.ok(fs.existsSync(path.join(dir,'assets/vendor/katex',font)),`Missing math font: ${font}`);

// Independent source audit: compare the characters in each recovered SVG with
// the transcription, then check matrix row order using drawing coordinates.
const drawnMinusCounts={image28:2,image29:1,image30:1,image32:2,image36:1,image98:1};
function glyphs(s){return [...s.replaceAll('−','-').replaceAll('′',"'").replaceAll('"',"''")].filter(c=>/[\p{L}\p{N}\-+=⋅∘ℓ×π.,']/u.test(c));}
function plainLatex(s){
  s=s.replace(/\\phantom\{[^}]*\}/g,'');
  for(const [k,v]of Object.entries({cdot:'⋅',circ:'∘',ell:'ℓ',times:'×',pi:'π'}))s=s.replace(new RegExp('\\\\'+k+'(?![A-Za-z])','g'),v);
  return s.replace(/\\(?:begin|end)\{[^}]*\}/g,'').replace(/\\[A-Za-z]+/g,'');
}
let matrixRows=0;
for(const a of formulas.filter(a=>a.source_asset.endsWith('.svg'))){
  const svg=read(a.source_asset);
  const texts=[...svg.matchAll(/<text\b([^>]*)>([\s\S]*?)<\/text>/g)].map(m=>({text:decode(m[2]),x:+/\bx="([^"]+)"/.exec(m[1])[1],y:+/\by="([^"]+)"/.exec(m[1])[1]}));
  const sourceGlyphs=texts.map(t=>t.text).join('')+'-'.repeat(drawnMinusCounts[a.image_id]||0);
  compare(count(glyphs(sourceGlyphs)),count(glyphs(plainLatex(a.latex))),`Source glyph mismatch: ${a.image_id}`);
  const matrices=[...a.latex.matchAll(/\\begin\{bmatrix\}([\s\S]*?)\\end\{bmatrix\}/g)].map(m=>m[1]);
  if(!matrices.length)continue;
  const brackets=[...svg.matchAll(/<path d="M ([\d.]+) ([\d.]+) H ([\d.]+) V ([\d.]+) H ([\d.]+)"/g)].map(m=>({x:+m[3],top:+m[2],bottom:+m[4],left:+m[1]>+m[3]}));
  const lefts=brackets.filter(b=>b.left).sort((a,b)=>a.x-b.x);
  assert.equal(lefts.length,matrices.length,`Matrix count: ${a.image_id}`);
  for(let i=0;i<lefts.length;i++){
    const left=lefts[i],right=Math.min(...brackets.filter(b=>!b.left&&b.x>left.x).map(b=>b.x));
    const cells=texts.filter(t=>t.x>left.x&&t.x<right-3.24&&t.y>=left.top-3&&t.y<=left.bottom+2);
    const ys=[...new Set(cells.filter(t=>t.text!=='−').map(t=>t.y))].sort((a,b)=>a-b);
    const sourceRows=ys.map(y=>cells.filter(t=>t.y===y||(t.text==='−'&&t.y<y&&y-t.y<=6)).sort((a,b)=>a.x-b.x).map(t=>t.text).join('').replaceAll('−','-').replaceAll(' ',''));
    const latexRows=matrices[i].split('\\\\').map(row=>plainLatex(row).replace(/[{}^&\s]/g,'')).filter(Boolean);
    assert.deepEqual(latexRows,sourceRows,`Matrix rows: ${a.image_id}, matrix ${i+1}`);
    matrixRows+=latexRows.length;
  }
}
assert.equal((formulas.find(a=>a.image_id==='image263').latex.match(/\\phantom\{0\}/g)||[]).length,15);
assert.equal((formulas.find(a=>a.image_id==='image255').latex.match(/\\phantom\{116\}/g)||[]).length,5);
console.log(JSON.stringify({formula_assets:220,rendered_math:546,retained_images:120,question_anchors:170,svg_sources_checked:212,matrix_rows_checked:matrixRows,missing_files:0,latex_errors:0}));
