#!/usr/bin/env python3
"""Render catalog.csv into index.html, catalog.html, sitemap.xml and JSON-LD.

Run after editing catalog.csv:  python3 build.py
"""
import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITE_URL = "https://la-borbolla-editorial.github.io/lbe-site/"
FILTER_MIN_BOOKS = 8  # category filter stays hidden below this many titles
E = html.escape


def load_books():
    with open(ROOT / "catalog.csv", newline="", encoding="utf-8") as f:
        return [{k: (v or "").strip() for k, v in row.items() if k} for row in csv.DictReader(f)]


def categories(book):
    return [c.strip() for c in book["category"].split(";") if c.strip()]


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def cover_img(book, extra=""):
    return (f'<img class="book-cover" src="assets/covers/{E(book["cover_file"])}" '
            f'alt="Cover of {E(book["title"])}" width="324" height="500" loading="lazy"{extra}>')


def render_entry(book):
    forthcoming = book["status"] == "forthcoming"
    cats = categories(book)
    if book["sale_url"]:
        action = (f'<a class="book-buy" href="{E(book["sale_url"])}" target="_blank" rel="noopener noreferrer">'
                  f'Buy <span class="visually-hidden">{E(book["title"])} </span>on Amazon <span aria-hidden="true">↗</span></a>')
    else:
        action = ""
    badge = '<span class="book-badge">Forthcoming</span>' if forthcoming else ""
    parts = [
        f'<p class="book-kicker">{E(" · ".join(cats))}{badge}</p>',
        f'<h2>{E(book["title"])}</h2>',
        f'<p class="book-authors">{E(book["authors"])}</p>',
    ]
    if book["contributors"]:
        parts.append(f'<p class="book-contributors">{E(book["contributors"])}</p>')
    if book["description"]:
        parts.append(f'<p class="book-blurb">{E(book["description"])}</p>')
    parts.append(action)
    cls = "book-entry" + (" forthcoming" if forthcoming else "")
    body = "\n".join("          " + p for p in parts if p)
    return (f'      <article class="{cls}" data-categories="{E("|".join(cats))}">\n'
            f'        {cover_img(book)}\n'
            f'        <div class="book-copy">\n{body}\n        </div>\n      </article>')


def render_filters(books):
    counts = {}
    for b in books:
        for c in categories(b):
            counts[c] = counts.get(c, 0) + 1
    buttons = [f'<button type="button" class="tag-button active" data-category="all" aria-pressed="true">All ({len(books)})</button>']
    for c in sorted(counts):
        buttons.append(f'<button type="button" class="tag-button" data-category="{E(c)}" aria-pressed="false">{E(c)} ({counts[c]})</button>')
    hidden = " hidden" if len(books) < FILTER_MIN_BOOKS else ""
    inner = "\n".join("          " + b for b in buttons)
    return (f'      <section class="catalog-tags" aria-labelledby="catalog-tags-title"{hidden}>\n'
            f'        <h2 id="catalog-tags-title">Filter by category</h2>\n'
            f'        <div id="category-tags" class="tag-list">\n{inner}\n        </div>\n'
            f'        <p id="filter-status" class="visually-hidden" role="status" aria-live="polite"></p>\n'
            f'      </section>')


def render_shelf(books):
    items = []
    for b in books:
        items.append(f'      <li><a href="catalog.html#{slug(b["title"])}">{cover_img(b)}'
                     f'<span class="visually-hidden">{E(b["title"])}</span></a></li>')
    return '    <ul class="shelf">\n' + "\n".join(items) + "\n    </ul>"


def json_ld(books):
    data = [{"@context": "https://schema.org", "@type": "Organization", "name": "La Borbolla Editorial",
             "url": SITE_URL, "logo": SITE_URL + "assets/mark.png"}]
    for b in books:
        book = {"@context": "https://schema.org", "@type": "Book", "name": b["title"],
                "author": {"@type": "Person", "name": b["authors"]},
                "publisher": {"@type": "Organization", "name": "La Borbolla Editorial"},
                "image": SITE_URL + "assets/covers/" + b["cover_file"]}
        if b["description"]:
            book["description"] = b["description"]
        if b["sale_url"]:
            book["url"] = b["sale_url"]
        data.append(book)
    return '<script type="application/ld+json">\n' + json.dumps(data, indent=2, ensure_ascii=False).replace("</", "<\\/") + "\n  </script>"


def inject(path, name, content):
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"(<!-- BUILD:{name} -->).*?(<!-- /BUILD:{name} -->)", re.S)
    if not pattern.search(text):
        raise SystemExit(f"{path.name}: missing BUILD:{name} markers")
    path.write_text(pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(2)}", text), encoding="utf-8")


def main():
    books = load_books()
    entries = []
    for b in books:
        entry = render_entry(b).replace('<article ', f'<article id="{slug(b["title"])}" ', 1)
        entries.append(entry)
    inject(ROOT / "catalog.html", "list", "\n".join(entries))
    inject(ROOT / "catalog.html", "filters", render_filters(books))
    inject(ROOT / "catalog.html", "jsonld", "  " + json_ld(books))
    inject(ROOT / "index.html", "shelf", render_shelf(books))
    inject(ROOT / "index.html", "jsonld", "  " + json_ld(books[:0]))
    urls = "".join(f"  <url><loc>{SITE_URL}{p}</loc></url>\n" for p in ("", "catalog.html"))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n",
        encoding="utf-8")
    print(f"Built {len(books)} books.")


if __name__ == "__main__":
    main()
