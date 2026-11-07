// Portable batch renderer: Markdown is the reading source; the image checkpoint
// supplies placement-level provenance for the highlighted review.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
import katex from 'katex';
import {Marked} from 'marked';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const batch=process.argv.find(a=>/^\d+-\d+$/.test(a));
assert(batch,'Pass a batch such as 41-58');
const titleRange=batch.replace('-', '–');
const book=path.join(root,'gat-'+batch);
const check=path.join(root,'conversion-batches/checkpoints',batch);
const bookFile='GAT-'+batch;
const read=(p)=>JSON.parse(fs.readFileSync(p,'utf8'));
const write=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
const escape=(s)=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const math=(latex,displayMode=false)=>{
 const output=katex.renderToString(latex,{displayMode,throwOnError:true,strict:'error',trust:false,output:'htmlAndMathml'});
 return displayMode?output:`<span class="math-inline">${output}</span>`;
};
const marked=new Marked({extensions:[
 {name:'blockMath',level:'block',start:s=>s.indexOf('$$'),tokenizer(s){const m=/^\$\$\s*\n([\s\S]*?)\n\$\$(?:\n|$)/.exec(s);if(m)return {type:'blockMath',raw:m[0],latex:m[1]};},renderer:t=>math(t.latex,true)},
 {name:'inlineMath',level:'inline',start:s=>s.indexOf('$'),tokenizer(s){const m=/^\$(?!\$)((?:\\.|[^\\\n$])+?)\$(?!\$)/.exec(s);if(m)return {type:'inlineMath',raw:m[0],latex:m[1]};},renderer:t=>math(t.latex)}
]});
const parsed=s=>marked.parse(s).replace(/href="([^"#]+)\.md([#"])/g,'href="$1.html$2');
const inline=s=>marked.parseInline(String(s??''));
const formulas=read(path.join(book,'formula-transcriptions.json')).assets;
const formulaById=new Map(formulas.map(a=>[a.id,a]));
const decisions=read(path.join(check,'visual-decisions.json')).assets;
const decisionById=new Map(decisions.map(a=>[a.id,a]));
const semantics=read(path.join(book,'semantic-records.json'));
const manifest=read(path.join(book,'manifest.json'));
const pages=read(path.join(check,'page-placements.json'));
assert.equal(pages.figures.length,manifest.placements.length);
manifest.reference_render_page_count=pages.pages;
manifest.pagination_note=`Reference pages use the repaired LibreOffice copy. Original Word print pagination is unverified; source metadata reports ${manifest.original_cached_page_count} pages.`;
const assetById=new Map(manifest.assets.map(a=>[a.id,a]));
const placementById=new Map(manifest.placements.map((p,i)=>{
 p.reference_page=pages.figures[i].page;p.bbox_pt=pages.figures[i].bbox;
 const d=decisionById.get(p.asset_id);p.category=d.category;d.retained=!formulaById.has(p.asset_id)&&d.category!=='table'&&d.contains_raster;
 p.representation=formulaById.has(p.asset_id)?'latex':d.category==='table'?'table':d.retained?'image':'svg';
 return [p.id,p];
}));
for(const q of manifest.questions) q.reference_pages=[...new Set(manifest.placements.filter(p=>p.question_id===q.id).map(p=>p.reference_page))];
write(path.join(book,'manifest.json'),manifest);
const source=fs.readFileSync(path.join(check,'image-based.md'),'utf8');
const imageRE=/<img src="assets\/source-png\/(image\d+)\.png"[^>]+data-placement="([^"]+)"[^>]*\/>/g;
function tableMarkdown(t){
 const cell=v=>String(v??'').replaceAll('|','\\|');
 return (t.title?'**'+t.title+'**\n\n':'')+'| '+t.headers.map(cell).join(' | ')+' |\n| '+t.headers.map(()=>'---').join(' | ')+' |\n'+t.rows.map(r=>'| '+r.map(cell).join(' | ')+' |').join('\n');
}
let replaced=0;
const convertedMarkdown=source.replace(imageRE,(original,id,pid)=>{
 replaced++;const p=placementById.get(pid);assert.equal(p.asset_id,id);
 if(formulaById.has(id))return '$'+formulaById.get(id).latex.trim()+'$';
 if(p.representation==='table')return '\n\n'+tableMarkdown(semantics[id])+'\n\n';
 if(p.representation==='svg')return original.replace('assets/source-png/'+id+'.png','assets/vectors/'+id+'.svg');
 return original;
});
assert.equal(replaced,manifest.placements.length);
// Applying the initial media conversion is explicit; ordinary builds preserve
// subsequent edits to the user-facing Markdown.
if(process.argv.includes('--apply-media'))fs.writeFileSync(path.join(book,bookFile+'.md'),convertedMarkdown);
const md=fs.readFileSync(path.join(book,bookFile+'.md'),'utf8');
const require=createRequire(import.meta.url);const katexRoot=path.dirname(require.resolve('katex/package.json'));
const vendor=path.join(book,'assets/vendor/katex');fs.mkdirSync(vendor,{recursive:true});
for(const file of ['katex.min.css'])fs.copyFileSync(path.join(katexRoot,'dist',file),path.join(vendor,file));
fs.cpSync(path.join(katexRoot,'dist/fonts'),path.join(vendor,'fonts'),{recursive:true});fs.copyFileSync(path.join(katexRoot,'LICENSE'),path.join(vendor,'LICENSE'));
const baseCSS=`html{scroll-behavior:smooth}body{max-width:1000px;margin:32px auto;padding:0 24px;font:18px/1.65 Georgia,serif;color:#202124;background:white}h1,h2,h3,nav,summary,button,select,.review-summary{font-family:system-ui,sans-serif}h1{font-size:2rem;line-height:1.3}h2{border-top:1px solid #ddd;margin-top:56px;padding-top:24px}h3{margin-top:28px}nav{font-size:14px;margin-bottom:24px;display:flex;flex-wrap:wrap;gap:16px}a{color:#175f9e}img{max-width:100%;height:auto;vertical-align:middle}table{border-collapse:collapse;font-size:16px;max-width:100%;margin:20px 0}th,td{padding:8px 12px;border:1px solid #ccc;text-align:left}th{background:#f3f5f7}pre{overflow:auto;font-size:14px}blockquote{margin:16px 0;padding:8px 16px;background:#f5f5f5;font-size:16px}.katex{font-size:1.06em}.katex-display{overflow-x:auto;overflow-y:hidden;padding:6px 0}.review-table{display:table;border-collapse:collapse;font:14px/1.4 system-ui,sans-serif;width:100%;margin:12px 0}.review-row{display:table-row}.review-cell{display:table-cell;border:1px solid #ccd2d7;padding:7px;vertical-align:middle}.review-header{font-weight:600;background:#f1f4f7}.data-links{display:block;font:13px/1.5 system-ui,sans-serif;margin-top:8px}.retained-media{border-color:#c59734!important;background:#fffbef!important}.review-summary{font-size:15px;color:#475569}.media-gallery{display:grid;gap:24px}.media-card{padding:22px;border:1px solid #ddd;border-radius:6px;scroll-margin-top:130px}.media-card h2{font-size:18px;border:0;margin:0 0 12px;padding:0}.media-card .graph-pair{align-items:center}.media-card img{max-height:320px;object-fit:contain}.gallery-controls{position:sticky;top:0;background:#fff;padding:12px;border-bottom:1px solid #ddd;z-index:5;font:14px system-ui;display:flex;gap:12px;flex-wrap:wrap}.code-source{overflow-wrap:anywhere;font:13px/1.5 monospace}.gallery-filtered{display:none}@media(max-width:640px){body{padding:0 14px;font-size:17px}table{font-size:13px}th,td{padding:5px}.review-cell{padding:4px}.media-card{padding:12px}}@media print{nav,.changes-bar,.gallery-controls{display:none}h2{break-before:page}}`;
const changesCSS=fs.readFileSync(path.join(root,'scripts/changes.css'),'utf8')+'\n.math-inline{display:inline-block;max-width:100%;overflow-x:auto;vertical-align:middle;padding:4px 0}.changed-math{overflow-x:auto}';
function document(title,body,js=''){
 return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><link rel="stylesheet" href="assets/vendor/katex/katex.min.css"><style>${baseCSS}\n${changesCSS}</style></head><body><nav><a href="${bookFile}.html">Textbook</a><a href="${bookFile}-changes.html">Highlighted changes</a><a href="media-review.html">All media comparisons</a><a href="conversion-report.html">Conversion notes</a><a href="../index.html">All batches</a></nav><main>${body}</main>${js?'<script>'+js+'</script>':''}</body></html>\n`;
}
fs.writeFileSync(path.join(book,bookFile+'.html'),document('GAT Assignments '+titleRange,parsed(md)));
function tableHTML(t){
 const row=(values,head=false)=>`<span class="review-row" role="row">${values.map(v=>`<span class="review-cell${head?' review-header':''}" role="${head?'columnheader':'cell'}">${inline(v)}</span>`).join('')}</span>`;
 return (t.title?`<span class="diagram-caption">${escape(t.title)}</span>`:'')+`<span class="review-table" role="table">${row(t.headers,true)}${t.rows.map(r=>row(r)).join('')}</span>`;
}
function expressions(s){
 return s?.expressions||[];
}
function candidate(id,width='500'){
 const d=decisionById.get(id),s=semantics[id];
 if(formulaById.has(id))return math(formulaById.get(id).latex,true);
 if(s?.kind==='table')return tableHTML(s);
 if(d.retained)return `<span class="diagram-caption">Original retained</span><span class="change-note">${escape(d.notes.at(-1))}</span>`+(s?.lines?.length?`<span class="screenshot-transcript">${s.lines.map(line=>'<span style="display:block">'+escape(line)+'</span>').join('')}</span>`:'');
 return `<img loading="lazy" src="assets/vectors/${id}.svg" alt="Recovered ${escape(d.category.replaceAll('_',' '))}, ${id}" width="${width}">`;
}
function links(id){
 const d=decisionById.get(id);let l=[];
 if(formulaById.has(id))l.push('<a href="formula-transcriptions.json">LaTeX data</a>');
 if(fs.existsSync(path.join(book,'assets/vectors',id+'.svg'))&&!formulaById.has(id))l.push(`<a href="assets/vectors/${id}.svg">SVG</a>`,`<a href="assets/scenes/${id}.scene.json">Drawing JSON</a>`);
 if(semantics[id])l.push(`<a href="assets/data/${id}.json">Structured data</a>`);
 const a=assetById.get(id);l.push(`<a href="assets/originals/${path.basename(a.original)}">Original file</a>`);if(fs.existsSync(path.join(book,'assets/source-pdf',id+'.pdf')))l.push(`<a href="assets/source-pdf/${id}.pdf">Source PDF</a>`);
 return `<span class="data-links">${l.join(' · ')}</span>`;
}
function panels(id,pid){
 const items=expressions(semantics[id]);
 return items.length?`<button type="button" class="toggle-diagram-math" aria-expanded="false" aria-controls="math-${pid}">Show readable formulas</button><span class="diagram-math" id="math-${pid}" hidden>${items.map(m=>`<span class="math-entry">${math(m.latex,true)}</span>`).join('')}</span>`:'';
}
const label=d=>d.retained?'Original retained':d.category==='table'?'Image → editable table':'Drawing recovered as vectors';
let review=source.replace(imageRE,(original,id,pid)=>{
 const p=placementById.get(pid),d=decisionById.get(id),f=formulaById.get(id);
 if(f)return `<button type="button" class="changed-math" id="change-${pid}" data-source="assets/source-png/${id}.png" data-page="${p.reference_page}" data-placement="${pid}" title="Image converted to formula — click to compare">${math(f.latex)}</button>`;
 const notes=d.notes.length?d.notes.join(' '):'Review candidate — compare the content and labels with the original.';
 return `<span class="changed-graph${d.retained?' retained-media':''}" id="diagram-${pid}" data-diagram="${id}" data-placement="${pid}" role="group" aria-label="${escape(label(d))}"><span class="diagram-heading">${escape(label(d))}</span><span class="change-note">${escape(notes)} Reference page ${p.reference_page}.</span><span class="graph-pair"><span class="diagram-side"><span class="diagram-caption">Source preview</span>${original.replace('<img ','<img loading="lazy" ')}</span><span class="diagram-side"><span class="diagram-caption">${d.retained?'Preservation note':'Editable representation'}</span>${candidate(id,p.display_width_px)}</span></span>${panels(id,pid)}${links(id)}</span>`;
});
const counts={};for(const d of decisions)counts[d.category]=(counts[d.category]||0)+1;
const retained=decisions.filter(d=>d.retained).length,tables=counts.table||0,vectors=decisions.length-formulas.length-tables-retained;
const summary=`${formulas.length} formula images → LaTeX · ${tables} image tables → editable tables · ${vectors} drawings → SVG/JSON · ${retained} originals retained`;
const uniquePlacements=manifest.assets.map(a=>manifest.placements.find(p=>p.asset_id===a.id));
const controls=`<aside class="changes-bar" aria-label="Highlighted changes"><strong>Assignments ${titleRange}</strong><span class="formula-key">Yellow: formula</span><span class="graph-key">Blue: drawing/table</span><label>Browse <select id="change-filter"><option value="diagrams">Drawings and tables</option><option value="all">All changes</option></select></label><button type="button" id="previous-change">Previous</button><button type="button" id="next-change">Next</button><span id="change-count" aria-live="polite"></span><a href="media-review.html">Quick media review</a></aside><p class="review-summary">${summary}. Click a yellow formula to see its original. Amber marks retained artwork. All replacements are review candidates.</p>`;
const dialog=`<dialog id="source-dialog" aria-labelledby="source-title"><div class="dialog-heading"><h2 id="source-title">Image → formula</h2><button type="button" id="close-source" autofocus>Close</button></div><p id="source-page"></p><div class="source-pair"><section><h3>Original</h3><img id="original-formula" alt="Original formula"></section><section><h3>LaTeX</h3><div id="converted-formula"></div></section></div></dialog>`;
fs.writeFileSync(path.join(book,bookFile+'-changes.html'),document('GAT '+titleRange+' — highlighted changes',controls+parsed(review)+dialog,fs.readFileSync(path.join(root,'scripts/changes.js'),'utf8')));
let gallery=`<h1>GAT ${titleRange} media review</h1><p class="review-summary">${summary}. Every source graphic appears once below. Use the filters to skim one category.</p><div class="gallery-controls"><label>Show <select id="media-filter"><option value="all">All ${decisions.length} graphics</option><option value="nonformula" selected>Drawings, tables and retained originals (${decisions.length-formulas.length})</option><option value="formula">Formulas (${formulas.length})</option><option value="table">Tables (${tables})</option><option value="retained">Retained originals (${retained})</option></select></label><span id="gallery-count" aria-live="polite"></span><a href="${bookFile}-changes.html">Read in textbook context</a></div><div class="media-gallery">`;
for(const p of uniquePlacements){
 const id=p.asset_id,d=decisionById.get(id),f=formulaById.get(id);
 gallery+=`<section class="media-card${d.category==='formula'?' gallery-filtered':''}${d.retained?' retained-media':''}" id="${id}" data-category="${d.category}" data-retained="${d.retained}"><h2>${id} · ${escape(d.category.replaceAll('_',' '))} · <a href="${bookFile}-changes.html#${f?'change-'+p.id:'diagram-'+p.id}">Assignment ${p.assignment}, ${p.question_id?.split('-').at(-1).toUpperCase()||''}</a></h2><span class="graph-pair"><span class="diagram-side"><span class="diagram-caption">Source preview · reference page ${p.reference_page}</span><img loading="lazy" src="assets/source-png/${id}.png" alt="Original ${id}" width="${Math.max(p.display_width_px,100)}"></span><span class="diagram-side"><span class="diagram-caption">${f?'LaTeX candidate':label(d)}</span>${candidate(id,Math.max(p.display_width_px,100))}</span></span>${d.notes.map(n=>'<p class="change-note">'+escape(n)+'</p>').join('')}${expressions(semantics[id]).map(m=>math(m.latex,true)).join('')}${f?'<details><summary>LaTeX source</summary><code class="code-source">'+escape(f.latex)+'</code></details>':''}${links(id)}</section>`;
}
gallery+='</div>';
const galleryJS=`const filter=document.getElementById('media-filter'),cards=[...document.querySelectorAll('.media-card')];function apply(){let n=0;for(const c of cards){const show=filter.value==='all'||filter.value==='nonformula'&&c.dataset.category!=='formula'||filter.value==='retained'&&c.dataset.retained==='true'||filter.value===c.dataset.category;c.classList.toggle('gallery-filtered',!show);if(show)n++;}document.getElementById('gallery-count').textContent=n+' graphics';}filter.addEventListener('change',apply);if(location.hash){const c=document.getElementById(location.hash.slice(1));if(c?.classList.contains('media-card'))filter.value=c.dataset.category==='formula'?'formula':'nonformula';}apply();`;
fs.writeFileSync(path.join(book,'media-review.html'),document('GAT '+titleRange+' — media comparison',gallery,galleryJS));
const taxonomy=read(path.join(root,'visual-pipeline/taxonomy.json'));
const pageIssues=new Map();
for(const p of manifest.placements){
 const notes=decisionById.get(p.asset_id).notes;if(!notes.length)continue;
 const key=p.reference_page+'|'+notes.join(' '),entry=pageIssues.get(key)||{page:p.reference_page,notes:notes.join(' '),links:new Map()};
 entry.links.set(p.question_id||p.assignment,`[${p.assignment} ${p.question_id?.split('-').at(-1).toUpperCase()||''}](${bookFile}-changes.html#${formulaById.has(p.asset_id)?'change-':'diagram-'}${p.id})`);
 pageIssues.set(key,entry);
}
const report=[`# Conversion notes for GAT ${titleRange}`,
`All ${manifest.assignments.length} assignments, ${manifest.questions.length} main question anchors, ${manifest.placements.length} graphic placements and ${decisions.length} unique source graphics are accounted for. ${summary}.`,
'## Graphics by category','| Category | Unique graphics |','| --- | ---: |',
...Object.entries(counts).map(([key,n])=>`| ${taxonomy.categories.find(c=>c.id===key)?.label||key} | ${n} |`),
'','## Pagination',`The original file metadata reports ${manifest.original_cached_page_count} pages. The repaired reference copy has ${pages.pages} pages. Numbers below refer to that copy; original printed numbering is not certified. Markdown reflows text, headers and spacing.`,
'## Issues by reference page','| Reference page | Assignment/question | Issue |','| --- | --- | --- |',
...[...pageIssues.values()].map(row=>`| ${row.page} | ${[...row.links.values()].join(', ')} | ${row.notes} |`),
'','## What is preserved',
'Original DOC files, unchanged embedded media, native equation records, parsed equation trees, drawing JSON and conversion scripts are retained. Formulas are recovered from native MTEF where available; a separate source-inspected mapping covers formula pictures without native equations. No exercise answers or missing data have been filled in.',
'Equation source previews are decoded from QuickDraw text and line records. Composite PICT drawings are rendered through a font-repaired Word atlas; embedded PDF artwork is extracted directly when available. These are reconstructed previews, not certified screenshots from the original version of Word. The original binary files remain linked for independent checking.',
'Vector JSON exposes paths and positioned labels. Layout coordinates do not imply exact mathematical coordinates, and extracted PDF text may contain legacy encodings. Native equation records embedded in larger figures are exposed separately; editing them does not yet relayout the drawing.',
`${retained} graphics still contain raster artwork. Their original previews remain in the reading copy. Formula and table pictures converted to text are counted as converted even when their originals were raster images.`,
'All replacements are review candidates. Structural checks, symbol comparisons and visual spot checks are not a full mathematical proofreading pass. Browser interactions have not been automatically tested because local-file browser access is restricted in this session.',
'',`[Highlighted textbook](${bookFile}-changes.html) · [All media comparisons](media-review.html) · [Plain textbook](${bookFile}.html)`];
fs.writeFileSync(path.join(book,'conversion-report.md'),report.join('\n\n').replace(/\n\n(?=\|)/g,'\n'));
fs.writeFileSync(path.join(book,'conversion-report.html'),document('GAT '+titleRange+' conversion notes',parsed(fs.readFileSync(path.join(book,'conversion-report.md'),'utf8'))));
write(path.join(book,'media-inventory.json'),{version:1,source_sha256:manifest.source_sha256,counts,assets:decisions.map(d=>({...d,source:assetById.get(d.id),placements:manifest.placements.filter(p=>p.asset_id===d.id),conversion:formulaById.has(d.id)?{kind:'latex',latex:formulaById.get(d.id).latex}:semantics[d.id]?.kind==='table'?{kind:'table-json',path:`assets/data/${d.id}.json`}:d.retained?{kind:'original-retained',path:`assets/source-png/${d.id}.png`}:{kind:'vector-scene',path:`assets/scenes/${d.id}.scene.json`,preview:`assets/vectors/${d.id}.svg`}}))});
console.log(JSON.stringify({batch,assignments:manifest.assignments.length,questions:manifest.questions.length,placements:manifest.placements.length,formulas:formulas.length,tables,vector_drawings:vectors,retained_images:retained,reference_pages:pages.pages,katex:katex.version}));
