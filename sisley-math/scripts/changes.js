'use strict';
const allChanges = [...document.querySelectorAll('.changed-math, .changed-graph')];
const filter = document.getElementById('change-filter');
let changeItems = allChanges.filter(item => item.classList.contains('changed-graph'));
const sourceDialog = document.getElementById('source-dialog');
const countLabel = document.getElementById('change-count');
function track(index) {
  countLabel.textContent = `${index + 1} of ${changeItems.length}`;
}
function jump(direction) {
  // Compare to each target's intended scroll position so the first Next click
  // finds the first offscreen change, and later clicks move past the current one.
  const distances = changeItems.map(item => item.getBoundingClientRect().top - parseFloat(getComputedStyle(item).scrollMarginTop));
  let index = direction > 0 ? distances.findIndex(d => d > 4) : distances.findLastIndex(d => d < -4);
  if (index < 0) index = direction > 0 ? changeItems.length - 1 : 0;
  const target = changeItems[index];
  track(index);
  history.replaceState(null, '', `#${target.id}`);
  target.scrollIntoView({behavior: 'smooth', block: 'start'});
}
document.getElementById('previous-change').addEventListener('click', () => jump(-1));
document.getElementById('next-change').addEventListener('click', () => jump(1));
for (const item of allChanges) {
  if (!item.classList.contains('changed-math')) continue;
  item.addEventListener('click', () => {
    document.getElementById('original-formula').src = item.dataset.source;
    document.getElementById('source-page').textContent = `Reference page ${item.dataset.page} · ${item.dataset.placement}`;
    document.getElementById('converted-formula').replaceChildren(item.firstElementChild.cloneNode(true));
    sourceDialog.showModal();
  });
}
for (const button of document.querySelectorAll('.toggle-diagram-math')) {
  button.addEventListener('click', () => {
    const content = document.getElementById(button.getAttribute('aria-controls'));
    content.hidden = !content.hidden;
    button.setAttribute('aria-expanded', String(!content.hidden));
    button.textContent = content.hidden ? 'Show readable formulas' : 'Hide readable formulas';
  });
}
filter.addEventListener('change', () => {
  changeItems = filter.value === 'all' ? allChanges : allChanges.filter(item => item.classList.contains('changed-graph'));
  countLabel.textContent = `${changeItems.length} ${filter.value === 'all' ? 'changes' : 'diagrams'}`;
  followHash();
});
document.getElementById('close-source').addEventListener('click', () => sourceDialog.close());
function followHash() {
  const index = changeItems.findIndex(item => `#${item.id}` === location.hash);
  if (index >= 0) track(index);
}
addEventListener('hashchange', followHash);
followHash();
