import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const batches=['41-58','59-80','81-100','101-119'];
if(!process.argv.includes('--index-only'))for(const b of batches){
 const run=spawnSync(process.execPath,[path.join(root,'scripts/render-series.mjs'),b,...(process.argv.includes('--apply-media')?['--apply-media']:[])],{stdio:'inherit'});
 if(run.status!==0)process.exit(run.status||1);
}
const cards=batches.map(b=>{
 const inv=JSON.parse(fs.readFileSync(path.join(root,'gat-'+b,'media-inventory.json')));
 const counts={};for(const a of inv.assets)counts[a.conversion.kind]=(counts[a.conversion.kind]||0)+1;
 return `<article><h2>Assignments ${b.replace('-','–')}</h2><p>${counts.latex} formulas · ${counts['table-json']} tables · ${counts['vector-scene']} vector drawings · ${counts['original-retained']} retained originals</p><p><a class="button" href="gat-${b}/GAT-${b}-changes.html">Review highlighted textbook →</a></p><p><a href="gat-${b}/media-review.html">Skim media comparisons</a> · <a href="gat-${b}/GAT-${b}.html">Read textbook</a> · <a href="gat-${b}/GAT-${b}.md">Markdown</a> · <a href="gat-${b}/conversion-report.html">Page-by-page issues</a></p></article>`;
}).join('');
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sisley math — textbook review</title><style>body{max-width:1080px;margin:52px auto;padding:0 24px;background:#f5f6f8;color:#243047;font:17px/1.6 system-ui,sans-serif}h1{font-size:2.4rem;line-height:1.2}h2{font-size:1.3rem}a{color:#185e99}header p{max-width:780px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px;margin:30px 0}article{background:white;border:1px solid #d9e0e8;padding:24px;border-radius:10px}article p{font-size:15px}.button{display:inline-block;background:#175b93;color:#fff;padding:10px 15px;border-radius:6px;text-decoration:none}.key{display:inline-block;padding:2px 8px;border-radius:3px;font-size:14px}.formula{background:#fff1ad}.vector{background:#dcefff}.retained{background:#ffebcf}footer{padding:20px 0;font-size:14px;color:#526076}</style></head><body><header><h1>Sisley math textbook review</h1><p>The next four batches are ready to compare. The highlighted textbooks keep changes in context; the media galleries show every unique graphic once, beside its editable candidate.</p><p><span class="key formula">Yellow: click a formula to compare</span> <span class="key vector">Blue: drawing or table</span> <span class="key retained">Amber: original artwork retained</span></p></header><main><div class="cards">${cards}</div><h2>Earlier batches</h2><p><a href="gat-1-20/GAT-1-20-changes.html">Assignments 1–20</a> · <a href="gat-21-40/GAT-21-40-changes.html">Assignments 21–40</a></p><p>All replacements remain review candidates. Page numbers in the issue reports refer to the repaired reference copies, whose pagination differs from the original Word documents. Original media and conversion scripts are preserved.</p></main><footer>Offline reading copies · Markdown + LaTeX + SVG + JSON · <a href="README.md">Project documentation</a></footer></body></html>\n`;
fs.writeFileSync(path.join(root,'index.html'),html);
console.log('Built the textbook review overview.');
