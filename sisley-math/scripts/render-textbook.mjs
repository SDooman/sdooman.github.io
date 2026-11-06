import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import katex from 'katex';
import { Marked } from 'marked';

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
function math(latex, displayMode) {
  renderedMath++;
  return katex.renderToString(latex, {
    displayMode, throwOnError: true, strict: 'error', trust: false,
    output: 'htmlAndMathml',
  });
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
  return `<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${title}</title><link rel="stylesheet" href="assets/vendor/katex/katex.min.css"><style>${style}</style></head><body><nav><a href="GAT-1-20.html">Textbook</a><a href="conversion-report.html">Conversion notes</a><a href="formula-review.html">Formula review</a><a href="formula-comparison.html">Source comparison</a></nav><main>${content}</main></body></html>\n`;
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
const escape = (s) => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
let comparison = '<h1>Formula source comparison</h1><p>Each distinct formula is shown once beside its retained source image. Raised minus signs, incomplete exercises, and source notation are preserved. See the formula review for issues.</p>';
for (const item of transcription.assets.filter(a => a.status === 'latex')) {
  const links = item.question_ids.map(id=>`<a href="GAT-1-20.html#${id}">${id}</a>`).join(', ');
  comparison += `<section class="formula-pair" id="${item.image_id}"><div><h3>${item.image_id}: source image</h3><div class="source"><img src="${item.source_asset}" alt="Original ${item.image_id}"></div></div><div><h3>LaTeX transcription</h3>${math(item.latex,true)}<code>${escape(item.latex)}</code></div><div class="formula-note">Reference pages ${item.reference_pages.join(', ')} · ${links}${item.note?`<p>${escape(item.note)}</p>`:''}</div></section>`;
}
fs.writeFileSync(path.join(out,'formula-comparison.html'), document('Formula source comparison',comparison));
console.log(JSON.stringify({math_renderings:counts,katex:katex.version,offline:true}));
