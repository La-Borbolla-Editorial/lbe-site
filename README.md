# La Borbolla Editorial site

A small static colophon-style site. The catalog is pre-rendered from `catalog.csv`, so it works without JavaScript or a local server.

## Files

- `index.html` — colophon page (with a "Now in print" shelf)
- `catalog.html` — catalog page
- `catalog.csv` — catalog data (`title, authors, contributors, category, status, cover_file, sale_url, description`)
- `build.py` — renders the CSV into `index.html`, `catalog.html` (including JSON-LD) and `sitemap.xml`
- `catalog.js` — category filtering only (progressive enhancement)
- `styles.css` — shared styling, including self-hosted `@font-face` rules
- `assets/mark.png` — printer's mark; `assets/covers/` — cover images; `assets/fonts/` — Cormorant Garamond and IM Fell English
- `404.html`, `robots.txt`, `sitemap.xml`

## Adding a book

1. Put the cover in `assets/covers/` (about 2:3, e.g. 324×500 or larger).
2. Add a row to `catalog.csv`. Use `status` = `available` or `forthcoming`; separate multiple categories with `;`.
3. Commit. A pre-commit hook runs `python3 build.py` and stages the regenerated files (you can also run it by hand).

After a fresh clone, enable the hook once with `git config core.hooksPath .githooks`.

The category filter appears automatically once the catalog has 8 titles (`FILTER_MIN_BOOKS` in `build.py`). If the domain changes, update `SITE_URL` in `build.py` and the canonical/OG URLs in the page heads (currently `https://laborbollaeditorial.com/`).

## Preview

```sh
python3 -m http.server 8765
```

Then open http://127.0.0.1:8765/index.html
