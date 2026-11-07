'use strict';
const changeItems = [...document.querySelectorAll('.changed-math, .changed-graph')];
const sourceDialog = document.getElementById('source-dialog');
const countLabel = document.getElementById('change-count');
let currentChange = -1;
function track(index) {
  currentChange = index;
  countLabel.textContent = `${index + 1} of ${changeItems.length}`;
}
function nearestChange() {
  const barBottom = document.querySelector('.changes-bar').getBoundingClientRect().bottom;
  let best = 0, distance = Infinity;
  for (let i = 0; i < changeItems.length; i++) {
    const d = Math.abs(changeItems[i].getBoundingClientRect().top - barBottom - 24);
    if (d < distance) { distance = d; best = i; }
  }
  return best;
}
function jump(direction) {
  const start = nearestChange();
  const index = Math.max(0, Math.min(changeItems.length - 1, start + direction));
  const target = changeItems[index];
  track(index);
  history.replaceState(null, '', `#${target.id}`);
  target.scrollIntoView({behavior: 'smooth', block: 'start'});
}
document.getElementById('previous-change').addEventListener('click', () => jump(-1));
document.getElementById('next-change').addEventListener('click', () => jump(1));
for (const [index, item] of changeItems.entries()) {
  if (!item.classList.contains('changed-math')) continue;
  item.addEventListener('click', () => {
    track(index);
    document.getElementById('original-formula').src = item.dataset.source;
    document.getElementById('source-page').textContent = `Reference page ${item.dataset.page} · ${item.dataset.placement}`;
    document.getElementById('converted-formula').replaceChildren(item.firstElementChild.cloneNode(true));
    sourceDialog.showModal();
  });
}
document.getElementById('close-source').addEventListener('click', () => sourceDialog.close());
function followHash() {
  const index = changeItems.findIndex(item => `#${item.id}` === location.hash);
  if (index >= 0) track(index);
}
addEventListener('hashchange', followHash);
followHash();
