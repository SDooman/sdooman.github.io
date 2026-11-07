import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import katex from 'katex';
import { Marked } from 'marked';
import assert from 'node:assert/strict';

const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'gat-1-20');
const katexRoot = path.dirname(require.resolve('katex/package.json'));
const vendor = path.join(out, 'assets/vendor/katex');
fs.mkdirSync(vendor, { recursive: true });
fs.copyFileSync(path.join(katexRoot, 'dist/katex.min.css'), path.join(vendor, 'katex.min.css'));
fs.cpSync(path.join(katexRoot, 'dist/fonts'), path.join(vendor, 'fonts'), { recursive: true });
fs.copyFileSync(path.join(katexRoot, 'LICENSE'), path.join(vendor, 'LICENSE'));
fs.writeFileSync(path.join(vendor, 'VERSION'), `${katex.version}\n`);

let renderedMath = 0;
let reviewPlacements = null;
let reviewIndex = 0;
const escape = (s) => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
function math(latex, displayMode) {
  renderedMath++;
  const result = katex.renderToString(latex, {
    displayMode, throwOnError: true, strict: 'error', trust: false,
    output: 'htmlAndMathml',
  });
  if (!reviewPlacements) return result;
  const placement = reviewPlacements[reviewIndex++];
  assert.ok(placement, 'More formulas than recorded placements');
  assert.ok(latex === placement.latex || /^[.,]$/.test(latex.slice(placement.latex.length)) && latex.startsWith(placement.latex), `Formula/source order mismatch at ${placement.id}`);
  return `<button type="button" class="changed-math${displayMode ? ' changed-display' : ''}" id="change-${placement.id}" data-source="${escape(placement.asset)}" data-page="${placement.reference_page}" data-placement="${placement.id}" title="Image converted to a formula — click to compare with the original">${result}</button>`;
}

// Tokenize math before ordinary Markdown can reinterpret backslashes or underscores.
// This is intentionally limited to the standard $ and $$ delimiters used here.
const marked = new Marked({ extensions: [
  {
    name: 'blockMath', level: 'block',
    start(src) { return src.indexOf('$$'); },
    tokenizer(src) {
      const match = /^\$\$\s*\n([\s\S]*?)\n\$\$(?:\n|$)/.exec(src);
      if (match) return { type: 'blockMath', raw: match[0], latex: match[1] };
    },
    renderer(token) { return `${math(token.latex, true)}\n`; },
  },
  {
    name: 'inlineMath', level: 'inline',
    start(src) { return src.indexOf('$'); },
    tokenizer(src) {
      const match = /^\$(?!\$)([^\n$]+?)\$(?!\$)/.exec(src);
      if (match) return { type: 'inlineMath', raw: match[0], latex: match[1] };
    },
    renderer(token) { return math(token.latex, false); },
  },
] });

const style = `
html{scroll-behavior:smooth}body{max-width:900px;margin:40px auto;padding:0 24px;font:18px/1.65 Georgia,serif;color:#202124;background:white}
h1,h2,h3,nav,summary{font-family:system-ui,sans-serif}h1{font-size:2rem;line-height:1.25}h2{border-top:1px solid #ddd;margin-top:64px;padding-top:24px}h3{margin-top:32px}
img{max-width:100%;height:auto;vertical-align:middle}p:has(>img:only-child){padding:8px 0}blockquote{margin:16px 0;padding:12px 16px;background:#f5f5f5;font-size:16px}
a{color:#175f9e}table{border-collapse:collapse;font-size:15px;max-width:100%}th,td{padding:10px;border:1px solid #ddd;text-align:left;vertical-align:top}pre{overflow-x:auto;font-size:14px;background:#f5f5f5;padding:12px}
.katex{font-size:1.08em}.katex-display{overflow-x:auto;overflow-y:hidden;padding:8px 2px;text-align:left}.katex-display>.katex{text-align:left}nav{font-size:14px;margin-bottom:28px}nav a{margin-right:18px}
.formula-pair{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;border-bottom:1px solid #ddd;padding:24px 0}.formula-pair h3{margin:0;font-size:16px}.formula-pair .source{min-height:60px;display:flex;align-items:center}.formula-pair code{overflow-wrap:anywhere;font-size:13px}.formula-note{grid-column:1/-1;font-size:15px;color:#555}
@media(max-width:600px){body{margin:24px auto;padding:0 16px;font-size:17px}.formula-pair{grid-template-columns:1fr}table{font-size:13px}th,td{padding:6px}}@media print{nav{display:none}body{max-width:none;margin:0}.katex-display{overflow:visible}h2{break-before:page}}
`;
function document(title, content) {
  return `<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${title}</title><link rel="stylesheet" href="assets/vendor/katex/katex.min.css"><style>${style}</style></head><body><nav><a href="GAT-1-20.html">Textbook</a><a href="GAT-1-20-changes.html#new-network">Highlighted changes</a><a href="conversion-report.html">Conversion notes</a><a href="formula-review.html">Formula review</a><a href="formula-comparison.html">Source comparison</a></nav><main>${content}</main></body></html>\n`;
}
const counts = {};
for (const [name, title] of [['GAT-1-20','GAT Assignments 1–20'],['conversion-report','Conversion notes'],['formula-review','Formula review']]) {
  const input = path.join(out, `${name}.md`);
  if (!fs.existsSync(input)) continue;
  renderedMath=0;
  const html = marked.parse(fs.readFileSync(input, 'utf8')).replace(/href="([^"#]+)\.md([#"])/g, 'href="$1.html$2');
  fs.writeFileSync(path.join(out, `${name}.html`), document(title, html));
  counts[name] = renderedMath;
}

const transcription = JSON.parse(fs.readFileSync(path.join(out, 'formula-transcriptions.json'), 'utf8'));
let comparison = '<h1>Formula source comparison</h1><p>Each distinct formula is shown once beside its retained source image. Raised minus signs, incomplete exercises, and source notation are preserved. See the formula review for issues.</p>';
for (const item of transcription.assets.filter(a => a.status === 'latex')) {
  const links = item.question_ids.map(id=>`<a href="GAT-1-20.html#${id}">${id}</a>`).join(', ');
  comparison += `<section class="formula-pair" id="${item.image_id}"><div><h3>${item.image_id}: source image</h3><div class="source"><img src="${item.source_asset}" alt="Original ${item.image_id}"></div></div><div><h3>LaTeX transcription</h3>${math(item.latex,true)}<code>${escape(item.latex)}</code></div><div class="formula-note">Reference pages ${item.reference_pages.join(', ')} · ${links}${item.note?`<p>${escape(item.note)}</p>`:''}</div></section>`;
}
fs.writeFileSync(path.join(out,'formula-comparison.html'), document('Formula source comparison',comparison));

// A reading copy with changes in their original question context. Match each
// formula to its recorded placement, so identical formulas never lose provenance.
const manifest = JSON.parse(fs.readFileSync(path.join(out, 'manifest.json'), 'utf8'));
reviewPlacements = manifest.placements.filter(p => p.representation === 'latex');
reviewIndex = 0;
let review = marked.parse(fs.readFileSync(path.join(out, 'GAT-1-20.md'), 'utf8'))
  .replace(/href="([^"#]+)\.md([#"])/g, 'href="$1.html$2');
assert.equal(reviewIndex, reviewPlacements.length);
reviewPlacements = null;
// Copy reconstructions and their readable math into the portable textbook bundle.
// Historical replay can rebuild from this bundled manifest without the pipeline.
const pipelineRoot = path.join(root, 'visual-pipeline');
const diagramManifest = path.join(out, 'diagram-conversions.json');
if (fs.existsSync(path.join(pipelineRoot, 'gat-catalog.json'))) {
  const catalog = JSON.parse(fs.readFileSync(path.join(pipelineRoot, 'gat-catalog.json'), 'utf8'));
  const diagrams = [];
  fs.mkdirSync(path.join(out, 'assets/reconstructions'), {recursive: true});
  for (const asset of catalog.assets.filter(a => ['network-scene','vector-scene'].includes(a.conversion.kind))) {
    const converted = `assets/reconstructions/${asset.id}.svg`;
    fs.copyFileSync(path.resolve(pipelineRoot, asset.conversion.preview), path.join(out, converted));
    const mathPath = path.resolve(pipelineRoot, asset.conversion.path.replace('.scene.json', '.math.json'));
    diagrams.push({id:asset.id, source:`assets/${asset.id}.png`, converted,
      category:asset.classification.category, kind:asset.conversion.kind,
      representation_level:asset.conversion.representation_level || 'network',
      approximate_trace:asset.id==='image1', review:asset.conversion.review,
      math:fs.existsSync(mathPath) ? JSON.parse(fs.readFileSync(mathPath,'utf8')) : []});
  }
  fs.writeFileSync(diagramManifest, JSON.stringify({version:1, diagrams}, null, 2)+'\n');
}
const diagramData = JSON.parse(fs.readFileSync(diagramManifest, 'utf8')).diagrams;
const diagramsBySource = new Map(diagramData.map(item => [item.source, item]));
const imagePlacements = manifest.placements.filter(p => p.representation === 'image');
let imageIndex = 0, diagramAppearances = 0;
const occurrences = new Map();
review = review.replace(/<img\s+src="(assets\/image\d+\.png)"[^>]*>/g, (original, src) => {
  const placement = imagePlacements[imageIndex++];
  assert.equal(placement.asset, src, 'Image/source order changed');
  const item = diagramsBySource.get(src);
  if (!item) return original;
  diagramAppearances++;
  const occurrence = (occurrences.get(item.id) || 0) + 1;
  occurrences.set(item.id, occurrence);
  const anchor = item.id === 'image262' && occurrence === 1 ? 'new-network' : `diagram-${item.id}-${occurrence}`;
  const title = item.kind === 'network-scene' ? 'Network redrawn' : item.approximate_trace ? 'Drawing recovered · waveform traced' : item.math.length ? 'Drawing and formulas recovered' : 'Drawing recovered as vectors';
  const note = item.approximate_trace ? 'The waveform is an approximate trace, not an exact function. Compare its shape with the original.' : 'Review candidate — compare the drawing and labels with the original.';
  const width = /\bwidth="([^"]+)"/.exec(original)?.[1] || '600';
  const mathContent = item.math.length ? `<button type="button" class="toggle-diagram-math" aria-expanded="false" aria-controls="math-${placement.id}">Show readable formulas</button><span class="diagram-math" id="math-${placement.id}" hidden>${item.math.map(m => `<span class="math-entry"><span class="math-entry-label">${escape(m.id.replaceAll('_',' '))}</span>${math(m.latex, true)}</span>`).join('')}</span>` : '';
  // Phrasing elements keep the handful of inline source diagrams valid inside
  // their original paragraphs; CSS supplies the block comparison layout.
  return `<span class="changed-graph" id="${anchor}" data-diagram="${item.id}" data-placement="${placement.id}" role="group" aria-label="${title}"><span class="diagram-heading">${title}</span><span class="change-note">${note} Reference page ${placement.reference_page}.</span><span class="graph-pair"><span class="diagram-side"><span class="diagram-caption">Original image</span>${original.replace('<img ', '<img loading="lazy" ')}</span><span class="diagram-side"><span class="diagram-caption">Reconstruction</span><img loading="lazy" src="${item.converted}" alt="Reconstruction of ${item.id}" width="${width}"></span></span>${mathContent}</span>`;
});
assert.equal(imageIndex, imagePlacements.length);
assert.equal(occurrences.size, diagramData.length, 'A reconstruction is missing from the reading copy');
const controls = `<aside class="changes-bar" aria-label="Highlighted changes"><strong>Changes highlighted</strong><span class="formula-key">Yellow: image → formula</span><span class="graph-key">Blue: reconstructed diagram</span><a href="#diagram-image279-1">Networks</a><a href="#diagram-image218-1">Matrices</a><a href="#diagram-image1-1">Geometry</a><label>Browse <select id="change-filter"><option value="diagrams">Diagrams only</option><option value="all">All changes</option></select></label><button type="button" id="previous-change">Previous</button><button type="button" id="next-change">Next</button><span id="change-count" aria-live="polite"></span></aside><p class="change-intro">${diagramData.length} diagram reconstructions appear in ${diagramAppearances} places, each beside its original. Blue comparisons include four networks and ten annotated-math drawings; use “Show readable formulas” to inspect their transcriptions. The calculator screenshot remains an image. Yellow highlights mark 546 earlier formula replacements; click one to compare it with its source.</p>`;
const dialog = `<dialog id="source-dialog" aria-labelledby="source-title"><div class="dialog-heading"><h2 id="source-title">Image → formula</h2><button type="button" id="close-source" autofocus>Close</button></div><p id="source-page"></p><div class="source-pair"><section><h3>Original image</h3><img id="original-formula" alt="Original formula image"></section><section><h3>Converted formula</h3><div id="converted-formula"></div></section></div></dialog>`;
let reviewDocument = document('GAT Assignments 1–20 — highlighted changes', controls + review + dialog);
reviewDocument = reviewDocument.replace('</style>', fs.readFileSync(path.join(root, 'scripts/changes.css'), 'utf8') + '</style>');
reviewDocument = reviewDocument.replace('</body>', `<script>${fs.readFileSync(path.join(root, 'scripts/changes.js'), 'utf8')}</script></body>`);
fs.writeFileSync(path.join(out, 'GAT-1-20-changes.html'), reviewDocument);
console.log(JSON.stringify({math_renderings:counts,katex:katex.version,offline:true}));
