// Progressive enhancement: the catalog is rendered by build.py; this only filters it.
const entries = [...document.querySelectorAll('.book-entry')];
const buttons = [...document.querySelectorAll('.tag-button')];
const status = document.querySelector('#filter-status');
const params = new URLSearchParams(location.search);

function applyFilter(category, { announce = true, updateUrl = true } = {}) {
  if (!buttons.some((button) => button.dataset.category === category)) category = 'all';

  let shown = 0;
  entries.forEach((entry) => {
    const match = category === 'all' || entry.dataset.categories.split('|').includes(category);
    entry.hidden = !match;
    if (match) shown += 1;
  });

  buttons.forEach((button) => {
    const active = button.dataset.category === category;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });

  if (announce && status) {
    status.textContent = `${shown} ${shown === 1 ? 'book' : 'books'} shown${category === 'all' ? '' : ` in ${category}`}.`;
  }

  if (updateUrl) {
    const url = new URL(location.href);
    if (category === 'all') url.searchParams.delete('c');
    else url.searchParams.set('c', category);
    history.replaceState(null, '', url);
  }
}

buttons.forEach((button) => {
  button.addEventListener('click', () => applyFilter(button.dataset.category));
});

if (params.has('c')) applyFilter(params.get('c'), { announce: false, updateUrl: false });
