// Independent math rendering for source comparison sheets; not the textbook renderer.
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const bundled = createRequire(process.env.SISLEY_NODE_PACKAGES + '/package.json');
const sharp = bundled('sharp');
const qa = createRequire(path.resolve(__dirname,'../../.conversion-work/gat-21-40/qa-runtime/package.json'));
const { mathjax } = qa('mathjax-full/js/mathjax.js');
const { TeX } = qa('mathjax-full/js/input/tex.js');
const { SVG } = qa('mathjax-full/js/output/svg.js');
const { liteAdaptor } = qa('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = qa('mathjax-full/js/handlers/html.js');
const { AllPackages } = qa('mathjax-full/js/input/tex/AllPackages.js');
const root = path.resolve(__dirname, '../..');
const adaptor = liteAdaptor(); RegisterHTMLHandler(adaptor);
const doc = mathjax.document('', {InputJax: new TeX({packages:AllPackages}), OutputJax:new SVG({fontCache:'local'})});
const target = path.join(root,'.conversion-work/gat-21-40/math-qa');fs.mkdirSync(target,{recursive:true});
(async()=>{
 for (const item of JSON.parse(fs.readFileSync(path.join(root,'gat-21-40/formula-transcriptions.json'))).assets) {
  let html = adaptor.outerHTML(doc.convert(item.latex,{display:true}));
  if (/data-mjx-error/.test(html)) throw Error(item.id+' math rendering failed');
  let svg = html.slice(html.indexOf('<svg'),html.lastIndexOf('</svg>')+6);
  const vb = /viewBox="([^"]+)"/.exec(svg)[1].split(/\s+/).map(Number);
  svg = svg.replace(/width="[^\"]+"/,`width="${vb[2]*.036}"`).replace(/height="[^\"]+"/,`height="${vb[3]*.036}"`).replaceAll('currentColor','black');
  fs.writeFileSync(path.join(target,item.id+'.svg'),svg);
  await sharp(Buffer.from(svg)).flatten({background:'white'}).png().toFile(path.join(target,item.id+'.png'));
 }
 console.log('Rendered all equation candidates independently with MathJax.');
})().catch(e=>{console.error(e);process.exit(1)});
