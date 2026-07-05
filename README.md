# La Borbolla Editorial site

A small static colophon-style site with a dynamically rendered catalog.

Files:

- `index.html` — colophon page
- `catalog.html` — catalog shell
- `catalog.csv` — catalog data
- `catalog.js` — CSV loading, rendering, tag filtering, and sale links
- `styles.css` — shared styling
- `assets/mark.png` — printer's mark copied from Branding
- `assets/covers/*.svg` — placeholder cover files

Because the catalog fetches `catalog.csv`, view through a local server:

```sh
cd "/Users/jpiglesias/Documents/Hub/Ediciones La Borbolla/lbe-site"
python3 -m http.server 8765
```

Then open:

http://127.0.0.1:8765/index.html
