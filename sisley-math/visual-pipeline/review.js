'use strict';
const {catalog, taxonomy} = JSON.parse(document.getElementById('inventory-data').textContent);
const $ = id => document.getElementById(id);
const categories = new Map(taxonomy.map(c => [c.id, c]));
const placements = new Map(catalog.assets.map(a => [a.id, catalog.placements.filter(p => p.asset_id === a.id)]));
const decisions = new Map();
let page = 0;
const perPage = 16;
function element(tag, text, className) {
  const e = document.createElement(tag);
  if (text !== undefined) e.textContent = text;
  if (className) e.className = className;
  return e;
}
function option(value, label) { const e = element('option', label); e.value = value; return e; }
for (const c of taxonomy) {
  const count = catalog.assets.filter(a => a.classification.category === c.id).length;
  $('category').append(option(c.id, `${c.label} (${count})`));
}
$('title').textContent = catalog.document.title;
$('summary').textContent = `${catalog.assets.length} source graphics · ${catalog.placements.length} appearances · ${new Set(catalog.assets.map(a => a.sha256)).size} distinct file hashes`;
$('coverage').textContent = [catalog.coverage.note, catalog.document.pagination_note].filter(Boolean).join(' ');
if (catalog.pages?.length) {
  $('pageSection').hidden = false;
  for (const p of catalog.pages) {
    const link = element('a', `Page ${p.page} · ${p.placement_ids.length} candidate regions`);
    link.href = p.regions_preview;
    const img = element('img'); img.src = p.regions_preview; img.alt = `Detected regions on page ${p.page}`; img.loading = 'lazy';
    link.append(img); $('pages').append(link);
  }
}
function filtered() {
  const query = $('search').value.trim().toLowerCase();
  return catalog.assets.filter(a => {
    const cls = decisions.get(a.id)?.category ?? a.classification.category;
    return ($('category').value === 'all' || cls === $('category').value)
      && ($('conversion').value === 'all' || a.conversion.status === $('conversion').value)
      && (!query || [a.id, categories.get(cls).label, ...placements.get(a.id).map(p => `page ${p.page} ${p.question_id || ''}`)].join(' ').toLowerCase().includes(query));
  });
}
function sourceImage(src, alt) {
  const box = element('div', undefined, 'imagebox');
  const link = element('a'); link.href = src;
  const img = element('img'); img.src = src; img.alt = alt; img.loading = 'lazy';
  link.append(img); box.append(link); return box;
}
function render() {
  const list = filtered();
  page = Math.max(0, Math.min(page, Math.ceil(list.length/perPage)-1));
  $('cards').replaceChildren();
  $('pagination').textContent = list.length ? `${page*perPage+1}–${Math.min((page+1)*perPage,list.length)} of ${list.length}` : 'No matches';
  $('prev').disabled = page === 0; $('next').disabled = (page+1)*perPage >= list.length;
  for (const a of list.slice(page*perPage,(page+1)*perPage)) {
    const card = element('article', undefined, 'card'); card.id = a.id;
    card.append(element('h2', a.id));
    card.append(element('span', categories.get(a.classification.category).label, 'badge'));
    card.append(element('span', `${a.conversion.status} · ${a.conversion.review.replaceAll('_',' ')}`, 'badge pending'));
    const uses = placements.get(a.id);
    card.append(element('p', `Pages ${[...new Set(uses.map(p=>p.page))].join(', ')} · ${uses.length} appearance(s)${a.duplicate_of ? ` · exact duplicate of ${a.duplicate_of}` : ''}`, 'meta'));
    const pair = element('div', undefined, 'pair');
    const source = element('div'); source.append(element('div', 'Preserved source', 'sourceLabel'), sourceImage(a.source, `Original ${a.id}`));
    const conversion = element('div'); conversion.append(element('div', 'Machine-readable representation', 'sourceLabel'));
    if (a.conversion.kind === 'latex') {
      conversion.append(element('pre', a.conversion.latex));
    } else if (['network-scene','vector-scene'].includes(a.conversion.kind)) {
      conversion.append(sourceImage(a.conversion.preview, `Candidate reconstruction of ${a.id}`));
      const link = element('a', 'Open editable scene JSON'); link.href = a.conversion.path; conversion.append(link);
      if (a.conversion.representation_level) conversion.append(element('p', a.conversion.representation_level === 'annotated-math' ? 'Source drawing plus transcribed matrices/formulas.' : 'Recovered drawing primitives; mathematical constraints have not been inferred.', 'meta'));
    } else {
      conversion.append(element('p', `Next representation: ${categories.get(a.classification.category).target}`));
      conversion.append(element('p', categories.get(a.classification.category).review, 'meta'));
    }
    pair.append(source, conversion); card.append(pair);
    if (a.issues?.length) card.append(element('p', a.issues.join(' '), 'meta'));
    const details = element('details'); details.append(element('summary', 'Review classification'));
    const editor = element('div', undefined, 'edit');
    const select = element('select'); select.setAttribute('aria-label', `Category for ${a.id}`);
    for (const c of taxonomy) select.append(option(c.id, c.label));
    select.value = decisions.get(a.id)?.category ?? a.classification.category;
    const notes = element('textarea'); notes.placeholder = 'Evidence, ambiguity, or component split needed'; notes.setAttribute('aria-label', `Review notes for ${a.id}`);
    notes.value = decisions.get(a.id)?.notes ?? a.classification.notes;
    const save = element('button', 'Queue decision');
    save.onclick = () => {
      decisions.set(a.id, {id:a.id, sha256:a.sha256, category:select.value, notes:notes.value});
      $('export').disabled = false;
      $('status').textContent = `${decisions.size} decision(s) queued. Export to keep your changes.`;
    };
    editor.append(select,notes,save); details.append(editor); card.append(details);
    $('cards').append(card);
  }
}
for (const id of ['category','conversion','search']) $(id).addEventListener('input',()=>{page=0;render();});
$('prev').onclick=()=>{page--;render();}; $('next').onclick=()=>{page++;render();};
$('export').onclick=()=>{
  const reviewer=$('reviewer').value.trim();
  if (!reviewer) { $('status').textContent='Enter a reviewer name before exporting.'; $('reviewer').focus(); return; }
  const blob=new Blob([JSON.stringify({document_sha256:catalog.document.sha256,reviewer,assets:[...decisions.values()]},null,2)+'\n'],{type:'application/json'});
  const url=URL.createObjectURL(blob);const link=element('a');link.href=url;link.download='visual-decisions.json';link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  $('status').textContent='Decisions exported. Apply the JSON with pipeline.py apply to update the saved catalog.';
};
render();
