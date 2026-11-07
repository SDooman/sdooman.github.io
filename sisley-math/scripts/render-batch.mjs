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
const book=path.join(root,'gat-21-40');
const read=(p)=>JSON.parse(fs.readFileSync(p,'utf8'));
const write=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
const escape=(s)=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const math=(latex,displayMode=false)=>katex.renderToString(latex,{displayMode,throwOnError:true,strict:'error',trust:false,output:'htmlAndMathml'});
const marked=new Marked({extensions:[
 {name:'blockMath',level:'block',start:s=>s.indexOf('$$'),tokenizer(s){const m=/^\$\$\s*\n([\s\S]*?)\n\$\$(?:\n|$)/.exec(s);if(m)return {type:'blockMath',raw:m[0],latex:m[1]};},renderer:t=>math(t.latex,true)},
 {name:'inlineMath',level:'inline',start:s=>s.indexOf('$'),tokenizer(s){const m=/^\$(?!\$)([^\n$]+?)\$(?!\$)/.exec(s);if(m)return {type:'inlineMath',raw:m[0],latex:m[1]};},renderer:t=>math(t.latex)}
]});
const parsed=s=>marked.parse(s).replace(/href="([^"#]+)\.md([#"])/g,'href="$1.html$2');
const inline=s=>marked.parseInline(String(s??''));
const formulas=read(path.join(book,'formula-transcriptions.json')).assets;
const formulaById=new Map(formulas.map(a=>[a.id,a]));
const decisions=read(path.join(root,'conversion-21-40/visual-decisions.json')).assets;
const decisionById=new Map(decisions.map(a=>[a.id,a]));
const semantics=read(path.join(book,'semantic-records.json'));
const manifest=read(path.join(book,'manifest.json'));
const pages=read(path.join(root,'conversion-21-40/checkpoints/page-placements.json'));
assert.equal(pages.figures.length,manifest.placements.length);
manifest.reference_render_page_count=pages.pages;
manifest.pagination_note='Reference pages are from the repaired LibreOffice render with original embedded PDF artwork. Original Word print pagination is unverified; saved metadata reports 85 pages.';
const assetById=new Map(manifest.assets.map(a=>[a.id,a]));
const placementById=new Map(manifest.placements.map((p,i)=>{
 p.reference_page=pages.figures[i].page;p.bbox_pt=pages.figures[i].bbox;
 const d=decisionById.get(p.asset_id);p.category=d.category;
 p.representation=formulaById.has(p.asset_id)?'latex':d.category==='table'?'table':d.contains_raster?'image':'svg';
 return [p.id,p];
}));
for(const q of manifest.questions) q.reference_pages=[...new Set(manifest.placements.filter(p=>p.question_id===q.id).map(p=>p.reference_page))];
write(path.join(book,'manifest.json'),manifest);
const source=fs.readFileSync(path.join(root,'conversion-21-40/checkpoints/image-based.md'),'utf8');
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
assert.equal(replaced,546);
// Applying the initial media conversion is explicit; ordinary builds preserve
// subsequent edits to the user-facing Markdown.
if(process.argv.includes('--apply-media'))fs.writeFileSync(path.join(book,'GAT-21-40.md'),convertedMarkdown);
const md=fs.readFileSync(path.join(book,'GAT-21-40.md'),'utf8');
const require=createRequire(import.meta.url);const katexRoot=path.dirname(require.resolve('katex/package.json'));
const vendor=path.join(book,'assets/vendor/katex');fs.mkdirSync(vendor,{recursive:true});
for(const file of ['katex.min.css'])fs.copyFileSync(path.join(katexRoot,'dist',file),path.join(vendor,file));
fs.cpSync(path.join(katexRoot,'dist/fonts'),path.join(vendor,'fonts'),{recursive:true});fs.copyFileSync(path.join(katexRoot,'LICENSE'),path.join(vendor,'LICENSE'));
const baseCSS=`html{scroll-behavior:smooth}body{max-width:1000px;margin:32px auto;padding:0 24px;font:18px/1.65 Georgia,serif;color:#202124;background:white}h1,h2,h3,nav,summary,button,select,.review-summary{font-family:system-ui,sans-serif}h1{font-size:2rem;line-height:1.3}h2{border-top:1px solid #ddd;margin-top:56px;padding-top:24px}h3{margin-top:28px}nav{font-size:14px;margin-bottom:24px;display:flex;flex-wrap:wrap;gap:16px}a{color:#175f9e}img{max-width:100%;height:auto;vertical-align:middle}table{border-collapse:collapse;font-size:16px;max-width:100%;margin:20px 0}th,td{padding:8px 12px;border:1px solid #ccc;text-align:left}th{background:#f3f5f7}pre{overflow:auto;font-size:14px}blockquote{margin:16px 0;padding:8px 16px;background:#f5f5f5;font-size:16px}.katex{font-size:1.06em}.katex-display{overflow-x:auto;overflow-y:hidden;padding:6px 0}.review-table{display:table;border-collapse:collapse;font:14px/1.4 system-ui,sans-serif;width:100%;margin:12px 0}.review-row{display:table-row}.review-cell{display:table-cell;border:1px solid #ccd2d7;padding:7px;vertical-align:middle}.review-header{font-weight:600;background:#f1f4f7}.data-links{display:block;font:13px/1.5 system-ui,sans-serif;margin-top:8px}.retained-media{border-color:#c59734!important;background:#fffbef!important}.review-summary{font-size:15px;color:#475569}.media-gallery{display:grid;gap:24px}.media-card{padding:22px;border:1px solid #ddd;border-radius:6px;scroll-margin-top:130px}.media-card h2{font-size:18px;border:0;margin:0 0 12px;padding:0}.media-card .graph-pair{align-items:center}.media-card img{max-height:320px;object-fit:contain}.gallery-controls{position:sticky;top:0;background:#fff;padding:12px;border-bottom:1px solid #ddd;z-index:5;font:14px system-ui;display:flex;gap:12px;flex-wrap:wrap}.code-source{overflow-wrap:anywhere;font:13px/1.5 monospace}.gallery-filtered{display:none}@media(max-width:640px){body{padding:0 14px;font-size:17px}table{font-size:13px}th,td{padding:5px}.review-cell{padding:4px}.media-card{padding:12px}}@media print{nav,.changes-bar,.gallery-controls{display:none}h2{break-before:page}}`;
const changesCSS=fs.readFileSync(path.join(root,'scripts/changes.css'),'utf8');
function document(title,body,js=''){
 return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><link rel="stylesheet" href="assets/vendor/katex/katex.min.css"><style>${baseCSS}\n${changesCSS}</style></head><body><nav><a href="GAT-21-40.html">Textbook</a><a href="GAT-21-40-changes.html">Highlighted changes</a><a href="media-review.html">All media comparisons</a><a href="conversion-report.html">Conversion notes</a><a href="../gat-1-20/GAT-1-20.html">Assignments 1–20</a></nav><main>${body}</main>${js?'<script>'+js+'</script>':''}</body></html>\n`;
}
fs.writeFileSync(path.join(book,'GAT-21-40.html'),document('GAT Assignments 21–40',parsed(md)));
function tableHTML(t){
 const row=(values,head=false)=>`<span class="review-row" role="row">${values.map(v=>`<span class="review-cell${head?' review-header':''}" role="${head?'columnheader':'cell'}">${inline(v)}</span>`).join('')}</span>`;
 return (t.title?`<span class="diagram-caption">${escape(t.title)}</span>`:'')+`<span class="review-table" role="table">${row(t.headers,true)}${t.rows.map(r=>row(r)).join('')}</span>`;
}
function expressions(s){
 if(s?.expressions)return s.expressions;
 if(s?.kind==='annotated-matrix')return [{id:'blank flight matrix',latex:String.raw`\begin{array}{c|ccccc}&D&\mathrm{LA}&\mathrm{NY}&\mathrm{SL}&\mathrm{SE}\\`+s.row_labels.map(label=>'\\mathrm{'+label+'}&'+Array(5).fill('\\phantom{0}').join('&')).join('\\\\')+String.raw`\end{array}`}];
 return [];
}
function candidate(id,width='500'){
 const d=decisionById.get(id),s=semantics[id];
 if(formulaById.has(id))return math(formulaById.get(id).latex,true);
 if(s?.kind==='table')return tableHTML(s);
 if(d.contains_raster)return `<span class="diagram-caption">Original retained</span><span class="change-note">${escape(d.notes.at(-1))}</span>`+(s?.lines?.length?`<span class="screenshot-transcript">${s.lines.map(line=>'<span style="display:block">'+escape(line)+'</span>').join('')}</span>`:'');
 return `<img loading="lazy" src="assets/vectors/${id}.svg" alt="Recovered ${escape(d.category.replaceAll('_',' '))}, ${id}" width="${width}">`;
}
function links(id){
 const d=decisionById.get(id);let l=[];
 if(formulaById.has(id))l.push('<a href="formula-transcriptions.json">LaTeX data</a>');
 if(!d.contains_raster&&!formulaById.has(id))l.push(`<a href="assets/vectors/${id}.svg">SVG</a>`,`<a href="assets/scenes/${id}.scene.json">Drawing JSON</a>`);
 if(semantics[id])l.push(`<a href="assets/data/${id}.json">Structured data</a>`);
 l.push(`<a href="assets/source-pdf/${id}.pdf">Original drawing</a>`);
 return `<span class="data-links">${l.join(' · ')}</span>`;
}
function panels(id,pid){
 const items=expressions(semantics[id]);
 return items.length?`<button type="button" class="toggle-diagram-math" aria-expanded="false" aria-controls="math-${pid}">Show readable formulas</button><span class="diagram-math" id="math-${pid}" hidden>${items.map(m=>`<span class="math-entry">${math(m.latex,true)}</span>`).join('')}</span>`:'';
}
const label=d=>d.contains_raster?'Original retained':d.category==='table'?'Image → editable table':d.category==='annotated_matrix'||d.category==='calculation_flow'?'Drawing + readable formulas':'Drawing recovered as vectors';
let review=source.replace(imageRE,(original,id,pid)=>{
 const p=placementById.get(pid),d=decisionById.get(id),f=formulaById.get(id);
 if(f)return `<button type="button" class="changed-math" id="change-${pid}" data-source="assets/source-png/${id}.png" data-page="${p.reference_page}" data-placement="${pid}" title="Image converted to formula — click to compare">${math(f.latex)}</button>`;
 const notes=d.notes.length?d.notes.join(' '):'Review candidate — compare the content and labels with the original.';
 return `<span class="changed-graph${d.contains_raster?' retained-media':''}" id="diagram-${id}-1" data-diagram="${id}" data-placement="${pid}" role="group" aria-label="${escape(label(d))}"><span class="diagram-heading">${escape(label(d))}</span><span class="change-note">${escape(notes)} Reference page ${p.reference_page}.</span><span class="graph-pair"><span class="diagram-side"><span class="diagram-caption">Original</span>${original.replace('<img ','<img loading="lazy" ')}</span><span class="diagram-side"><span class="diagram-caption">${d.contains_raster?'Preservation note':'Editable representation'}</span>${candidate(id,p.display_width_px)}</span></span>${panels(id,pid)}${links(id)}</span>`;
});
const summary='435 formula images → LaTeX · 16 image tables → editable tables · 89 drawings → SVG/JSON · 6 originals retained';
const controls=`<aside class="changes-bar" aria-label="Highlighted changes"><strong>Assignments 21–40</strong><span class="formula-key">Yellow: formula</span><span class="graph-key">Blue: drawing/table</span><label>Browse <select id="change-filter"><option value="diagrams">Drawings and tables</option><option value="all">All changes</option></select></label><button type="button" id="previous-change">Previous</button><button type="button" id="next-change">Next</button><span id="change-count" aria-live="polite"></span><a href="media-review.html">Quick media review</a></aside><p class="review-summary">${summary}. Click a yellow formula to see its original. Amber marks retained artwork. All replacements are review candidates.</p>`;
const dialog=`<dialog id="source-dialog" aria-labelledby="source-title"><div class="dialog-heading"><h2 id="source-title">Image → formula</h2><button type="button" id="close-source" autofocus>Close</button></div><p id="source-page"></p><div class="source-pair"><section><h3>Original</h3><img id="original-formula" alt="Original formula"></section><section><h3>LaTeX</h3><div id="converted-formula"></div></section></div></dialog>`;
fs.writeFileSync(path.join(book,'GAT-21-40-changes.html'),document('GAT 21–40 — highlighted changes',controls+parsed(review)+dialog,fs.readFileSync(path.join(root,'scripts/changes.js'),'utf8')));
let gallery=`<h1>GAT 21–40 media review</h1><p class="review-summary">${summary}. Every source graphic appears once below. Use the filters to skim one category.</p><div class="gallery-controls"><label>Show <select id="media-filter"><option value="all">All 546 graphics</option><option value="nonformula" selected>Drawings, tables and retained originals (111)</option><option value="formula">Formulas (435)</option><option value="table">Tables (16)</option><option value="retained">Retained originals (6)</option></select></label><span id="gallery-count" aria-live="polite"></span><a href="GAT-21-40-changes.html">Read in textbook context</a></div><div class="media-gallery">`;
for(const p of manifest.placements){
 const id=p.asset_id,d=decisionById.get(id),f=formulaById.get(id);
 gallery+=`<section class="media-card${d.category==='formula'?' gallery-filtered':''}${d.contains_raster?' retained-media':''}" id="${id}" data-category="${d.category}" data-retained="${d.contains_raster}"><h2>${id} · ${escape(d.category.replaceAll('_',' '))} · <a href="GAT-21-40-changes.html#${f?'change-'+p.id:'diagram-'+id+'-1'}">Assignment ${p.assignment}, ${p.question_id?.split('-').at(-1).toUpperCase()||''}</a></h2><span class="graph-pair"><span class="diagram-side"><span class="diagram-caption">Original · reference page ${p.reference_page}</span><img loading="lazy" src="assets/source-png/${id}.png" alt="Original ${id}" width="${Math.max(p.display_width_px,100)}"></span><span class="diagram-side"><span class="diagram-caption">${f?'LaTeX candidate':label(d)}</span>${candidate(id,Math.max(p.display_width_px,100))}</span></span>${d.notes.map(n=>'<p class="change-note">'+escape(n)+'</p>').join('')}${expressions(semantics[id]).map(m=>math(m.latex,true)).join('')}${f?'<details><summary>LaTeX source</summary><code class="code-source">'+escape(f.latex)+'</code></details>':''}${links(id)}</section>`;
}
gallery+='</div>';
const galleryJS=`const filter=document.getElementById('media-filter'),cards=[...document.querySelectorAll('.media-card')];function apply(){let n=0;for(const c of cards){const show=filter.value==='all'||filter.value==='nonformula'&&c.dataset.category!=='formula'||filter.value==='retained'&&c.dataset.retained==='true'||filter.value===c.dataset.category;c.classList.toggle('gallery-filtered',!show);if(show)n++;}document.getElementById('gallery-count').textContent=n+' graphics';}filter.addEventListener('change',apply);if(location.hash){const c=document.getElementById(location.hash.slice(1));if(c?.classList.contains('media-card'))filter.value=c.dataset.category==='formula'?'formula':'nonformula';}apply();`;
fs.writeFileSync(path.join(book,'media-review.html'),document('GAT 21–40 — media comparison',gallery,galleryJS));
const taxonomy=read(path.join(root,'visual-pipeline/taxonomy.json'));const counts={};for(const d of decisions)counts[d.category]=(counts[d.category]||0)+1;
const report=['# Conversion notes for GAT 21–40',`All 20 assignments, ${manifest.questions.length} main question anchors and 546 graphic placements are preserved. The Markdown contains the original body text, 435 LaTeX replacements, 16 editable tables, 89 SVG drawings and six retained images. Original EMFs, embedded PDFs and raster previews remain available.`,
 '## Graphics by category','| Category | Count | Representation |','| --- | ---: | --- |',
 ...Object.entries(counts).map(([key,n])=>`| ${taxonomy.categories.find(c=>c.id===key)?.label||key} | ${n} | ${key==='formula'?'LaTeX and native equation tree':key==='table'?'Markdown/HTML table, JSON and source vectors':key==='screenshot'?'Original and transcript/data reference':key==='geometry'?'SVG/JSON; two mixed raster illustrations retained':'SVG/JSON; annotated math records where applicable'} |`),
 '','## Pagination',`The source metadata reports **85 pages**. The original LibreOffice render left legacy EMFs blank. A reference copy using the recovered original artwork renders to **${pages.pages} pages**. Reference page numbers below identify that copy; original printed numbering and page breaks are not certified. Print spacing, headers and footers are reflowed in Markdown.`,
 '## Issues by reference page','| Reference page | Assignment/question | Issue |','| --- | --- | --- |',
 ...manifest.placements.filter(p=>decisionById.get(p.asset_id).notes.length).map(p=>`| ${p.reference_page} | [${p.assignment} ${p.question_id?.split('-').at(-1).toUpperCase()||''}](GAT-21-40-changes.html#diagram-${p.asset_id}-1) | ${decisionById.get(p.asset_id).notes.join(' ')} |`),
 '','## Review and reuse','All replacements are candidates for source-fidelity review. The original equation tree, source glyphs and rendered formulas are kept separately. Syntax and symbol checks do not establish an answer-key audit. Exercise blanks, source errors and historical data are preserved; no missing answers have been supplied.',
 'The 105 raster-free vector scenes include the 16 tables; the counts are overlapping representations, not additional graphics. SVG glyph outlines preserve labels visually. Positioned text in drawing JSON can contain legacy symbol encodings and should not be treated as corrected mathematical text. Drawing coordinates are layout positions, not inferred lengths or constraints.',
 'The 16 structured table records drive the Markdown/HTML tables. Annotated mathematical records have readable LaTeX panels, but changing those records does not yet relayout their source vector drawings. Learner execution, animation and progress storage remain future work.',
 'The six raster-containing graphics retain their original pixels. Three are calculator plots, one is a calculator results screen, and two are geometry illustrations with raster components. This conversion does not claim those six are fully vectorized.',
 '','[Highlighted textbook](GAT-21-40-changes.html) · [All media comparisons](media-review.html) · [Plain textbook](GAT-21-40.html)'];
fs.writeFileSync(path.join(book,'conversion-report.md'),report.join('\n\n').replace(/\n\n(?=\|)/g,'\n'));
fs.writeFileSync(path.join(book,'conversion-report.html'),document('GAT 21–40 conversion notes',parsed(fs.readFileSync(path.join(book,'conversion-report.md'),'utf8'))));
write(path.join(book,'media-inventory.json'),{version:1,source_sha256:manifest.source_sha256,counts,assets:decisions.map(d=>({...d,source:assetById.get(d.id),placement:manifest.placements.find(p=>p.asset_id===d.id),conversion:formulaById.has(d.id)?{kind:'latex',latex:formulaById.get(d.id).latex}:semantics[d.id]?.kind==='table'?{kind:'table-json',path:`assets/data/${d.id}.json`}:d.contains_raster?{kind:'original-retained',path:`assets/source-png/${d.id}.png`}:{kind:'vector-scene',path:`assets/scenes/${d.id}.scene.json`,preview:`assets/vectors/${d.id}.svg`}}))});
console.log(JSON.stringify({assignments:20,questions:manifest.questions.length,formulas:formulas.length,tables:16,vector_drawings:89,retained_images:6,reference_pages:pages.pages,katex:katex.version}));
