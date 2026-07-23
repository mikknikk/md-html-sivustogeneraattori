#!/usr/bin/env python3
"""Generoi staattisen HTML-sivuston Markdown-tiedostoista.

Sisältökansion jokainen alikansio muodostaa yhden kategorian navigaatioon.
Jokainen .md-tiedosto voi alkaa valinnaisella front matter -lohkolla:

    ---
    title: Sivun otsikko
    ---

    Loppuosa on tavallista Markdownia.

Kaikki linkit generoidaan sivukohtaisesti suhteellisina, joten sivusto
toimii riippumatta siitä, julkaistaanko se verkkotunnuksen juureen vai
jonkin alikansion alle.
"""
import argparse
import re
import shutil
from pathlib import Path

import markdown

FRONTMATTER_DELIM = "---"


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return {}, text
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            meta = {}
            for line in lines[1:i]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip()
            body = "\n".join(lines[i + 1:])
            return meta, body
    return {}, text


def humanize(name):
    return name.replace("-", " ").replace("_", " ").strip().capitalize()


def path_prefix(href):
    """'../'-etuliite, jolla pääsee href:n sijainnista takaisin sivuston juureen."""
    return "../" * href.count("/")


def render_nav(structure, prefix, current_href):
    parts = ['<ul class="nav">']
    for category, pages in structure.items():
        parts.append("<li>")
        parts.append(f'<span class="nav-category">{category}</span>')
        parts.append("<ul>")
        for title, href in pages:
            # aria-current + .active-luokka: nykyinen sivu ei saa erottua
            # navigaatiossa pelkästä väristä (WCAG 1.4.1).
            attrs = ' class="active" aria-current="page"' if href == current_href else ""
            parts.append(f'<li><a{attrs} href="{prefix}{href}">{title}</a></li>')
        parts.append("</ul></li>")
    parts.append("</ul>")
    return "\n".join(parts)


def wrap_tables(html):
    """Kietoo taulukot vierittyvään kääreeseen kapeita näyttöjä varten.

    Säilyttää natiivin <table>-semantiikan (toisin kuin CSS:n
    table{display:block}-temppu, joka voi rikkoa ruudunlukijoiden
    rivi-/sarakekäsittelyn joissain selaimissa).
    """
    html = re.sub(r"<table>", '<div class="table-scroll">\n<table>', html)
    html = re.sub(r"</table>", "</table>\n</div>", html)
    return html


def render_page(base_template, site_title, title, href, nav_html, content_html):
    prefix = path_prefix(href)
    return (
        base_template.replace("{{ site_title }}", site_title)
        .replace("{{ title }}", title)
        .replace("{{ css_href }}", f"{prefix}style.css")
        .replace("{{ home_href }}", f"{prefix}index.html")
        .replace("{{ nav }}", nav_html)
        .replace("{{ content }}", content_html)
    )


def build(content_dir, output_dir, templates_dir, site_title):
    content_dir = Path(content_dir)
    output_dir = Path(output_dir)
    templates_dir = Path(templates_dir)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    shutil.copy(templates_dir / "style.css", output_dir / "style.css")
    base_template = (templates_dir / "base.html").read_text(encoding="utf-8")

    md_files = sorted(content_dir.rglob("*.md"))
    if not md_files:
        raise SystemExit(f"Sisältöä ei löytynyt kansiosta: {content_dir}")

    # Ensimmäinen ajo: lue metatiedot ja rakenna navigaatio kategorioittain.
    pages = []
    structure = {}
    for md_path in md_files:
        rel = md_path.relative_to(content_dir)
        category = humanize(rel.parts[0]) if len(rel.parts) > 1 else "Yleiset"
        text = md_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        title = meta.get("title", humanize(md_path.stem))
        href = str(rel.with_suffix(".html")).replace("\\", "/")
        pages.append((md_path, href, title, body))
        structure.setdefault(category, []).append((title, href))

    # Toinen ajo: renderöi jokainen sivu, kun koko navigaatio on tiedossa.
    for md_path, href, title, body in pages:
        html_body = wrap_tables(markdown.markdown(body, extensions=["tables", "fenced_code"]))
        prefix = path_prefix(href)
        nav_html = render_nav(structure, prefix, href)
        page_content = f"<h1>{title}</h1>\n{html_body}"
        page_html = render_page(base_template, site_title, title, href, nav_html, page_content)
        out_path = output_dir / Path(href)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page_html, encoding="utf-8")

    # Etusivu listaa kaikki sivut kategorioittain.
    index_body = [f"<h1>{site_title}</h1>"]
    for category, cat_pages in structure.items():
        index_body.append(f"<h2>{category}</h2><ul>")
        for title, href in cat_pages:
            index_body.append(f'<li><a href="{href}">{title}</a></li>')
        index_body.append("</ul>")
    index_html = render_page(
        base_template, site_title, site_title, "index.html",
        render_nav(structure, "", ""), "\n".join(index_body),
    )
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")

    print(f"Generoitu {len(pages)} sivua kansioon {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--templates", required=True)
    parser.add_argument("--site-title", default="Sisältö")
    args = parser.parse_args()
    build(args.content, args.output, args.templates, args.site_title)
