const catalogList = document.querySelector('#catalog-list');
const categoryTags = document.querySelector('#category-tags');

let allBooks = [];
let activeCategory = 'all';

function parseCSV(text) {
  const rows = [];
  let row = [];
  let field = '';
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];

    if (char === '"') {
      if (inQuotes && next === '"') {
        field += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === ',' && !inQuotes) {
      row.push(field.trim());
      field = '';
      continue;
    }

    if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && next === '\n') i += 1;
      row.push(field.trim());
      if (row.some(Boolean)) rows.push(row);
      row = [];
      field = '';
      continue;
    }

    field += char;
  }

  if (field || row.length) {
    row.push(field.trim());
    if (row.some(Boolean)) rows.push(row);
  }

  return rows;
}

function rowsToBooks(csvText) {
  const rows = parseCSV(csvText);
  const headers = rows.shift().map((header) => header.trim());

  return rows.map((row) => Object.fromEntries(
    headers.map((header, index) => [header, row[index] || ''])
  ));
}

function getCategories(book) {
  return book.category
    .split(';')
    .map((category) => category.trim())
    .filter(Boolean);
}

function makeTextElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

function renderBook(book) {
  const entry = document.createElement('a');
  entry.className = `book-entry${book.status === 'forthcoming' ? ' forthcoming' : ''}`;
  entry.href = book.sale_url || '';
  entry.setAttribute('aria-label', `${book.title} sales page`);

  if (book.sale_url) {
    entry.target = '_blank';
    entry.rel = 'noopener noreferrer';
  }

  const cover = document.createElement('img');
  cover.className = 'book-cover';
  cover.src = `assets/covers/${book.cover_file}`;
  cover.alt = `${book.title} cover`;
  cover.loading = 'lazy';

  const copy = document.createElement('div');
  copy.className = 'book-copy';
  copy.appendChild(makeTextElement('p', 'book-kicker', getCategories(book).join(' · ')));
  copy.appendChild(makeTextElement('h2', '', book.title));
  copy.appendChild(makeTextElement('p', 'book-authors', book.authors));

  if (book.contributors) {
    copy.appendChild(makeTextElement('p', 'book-contributors', book.contributors));
  }

  entry.append(cover, copy);
  return entry;
}

function renderCatalog() {
  const books = activeCategory === 'all'
    ? allBooks
    : allBooks.filter((book) => getCategories(book).includes(activeCategory));

  catalogList.replaceChildren(...books.map(renderBook));
  catalogList.classList.remove('catalog-list-settled');
  requestAnimationFrame(() => {
    catalogList.classList.add('catalog-list-settled');
  });
}

function renderTagControls() {
  const counts = new Map();

  allBooks.forEach((book) => {
    getCategories(book).forEach((category) => {
      counts.set(category, (counts.get(category) || 0) + 1);
    });
  });

  const categories = [...counts.keys()].sort((a, b) => a.localeCompare(b));
  const controls = [makeTagButton('all', `All (${allBooks.length})`)];

  categories.forEach((category) => {
    controls.push(makeTagButton(category, `${category} (${counts.get(category)})`));
  });

  categoryTags.replaceChildren(...controls);
}

function makeTagButton(category, label) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = `tag-button${category === activeCategory ? ' active' : ''}`;
  button.textContent = label;
  button.setAttribute('aria-pressed', String(category === activeCategory));
  button.addEventListener('click', () => {
    activeCategory = category;
    renderCatalog();
    renderTagControls();
  });
  return button;
}

async function loadCatalog() {
  try {
    const response = await fetch('catalog.csv');
    if (!response.ok) throw new Error(`Could not load catalog.csv (${response.status})`);

    allBooks = rowsToBooks(await response.text());
    renderCatalog();
    renderTagControls();
  } catch (error) {
    catalogList.replaceChildren(makeTextElement(
      'p',
      'catalog-loading',
      'Catalog could not be loaded. If you opened this page directly from the file system, run it through a small local web server so JavaScript can fetch catalog.csv.'
    ));
    categoryTags.replaceChildren();
    console.error(error);
  }
}

loadCatalog();
