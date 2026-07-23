#!/usr/bin/env python3
"""Generoi staattisen HTML-sivuston Markdown-tiedostoista.

Sisältökansion jokainen alikansio muodostaa yhden kategorian navigaatioon.
Jokainen .md-tiedosto voi alkaa valinnaisella front matter -lohkolla:

    ---
    title: Sivun otsikko
    ---

    Loppuosa on tavallista Markdownia.
"""
import argparse
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


def render_nav(structure, current_href):
    parts = ['<ul class="nav">']
    for category, pages in structure.items():
        parts.append("<li>")
        parts.append(f'<span class="nav-category">{category}</span>')
        parts.append("<ul>")
        for title, href in pages:
            css_class = ' class="active"' if href == current_href else ""
            parts.append(f'<li><a{css_class} href="/{href}">{title}</a></li>')
        parts.append("</ul></li>")
    parts.append("</ul>")
    return "\n".join(parts)


def build(content_dir, output_dir, templates_dir):
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
        html_body = markdown.markdown(body, extensions=["tables", "fenced_code"])
        nav_html = render_nav(structure, href)
        page_html = (
            base_template.replace("{{ title }}", title)
            .replace("{{ nav }}", nav_html)
            .replace("{{ content }}", html_body)
        )
        out_path = output_dir / Path(href)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page_html, encoding="utf-8")

    # Etusivu listaa kaikki sivut kategorioittain.
    index_body = ['<h1>Ohjeet ja lunttilaput</h1>']
    for category, cat_pages in structure.items():
        index_body.append(f"<h2>{category}</h2><ul>")
        for title, href in cat_pages:
            index_body.append(f'<li><a href="/{href}">{title}</a></li>')
        index_body.append("</ul>")
    index_html = (
        base_template.replace("{{ title }}", "Etusivu")
        .replace("{{ nav }}", render_nav(structure, ""))
        .replace("{{ content }}", "\n".join(index_body))
    )
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")

    print(f"Generoitu {len(pages)} sivua kansioon {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--templates", required=True)
    args = parser.parse_args()
    build(args.content, args.output, args.templates)
