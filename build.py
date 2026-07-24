#!/usr/bin/env python3
"""Generoi staattisen HTML-sivuston Markdown-tiedostoista.

Sisältökansion jokainen alikansio muodostaa kategorian navigaatioon, ja
alikansiot voi sisäkkäistää mielivaltaisen syvälle — jokainen taso näkyy
omana, sisennettynä alikategorianaan. Jokainen .md-tiedosto voi alkaa
valinnaisella front matter -lohkolla:

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


ORDER_PREFIX = re.compile(r"^\d+[-_]")


def humanize(name):
    # Numeroetuliite (esim. "01-editorit" -> "editorit") ohjaa vain
    # aakkosjärjestykseen perustuvaa lajittelua, ei saa näkyä nimessä.
    name = ORDER_PREFIX.sub("", name)
    return name.replace("-", " ").replace("_", " ").strip().capitalize()


def path_prefix(href):
    """'../'-etuliite, jolla pääsee href:n sijainnista takaisin sivuston juureen."""
    return "../" * href.count("/")


def new_node():
    return {"pages": [], "children": {}, "index_meta": None, "index_body": None}


def get_node(tree, folder_parts):
    """Hakee (ja luo tarvittaessa) kansiopolkua vastaavan solmun puusta."""
    node = tree
    for part in folder_parts:
        node = node["children"].setdefault(part, new_node())
    return node


def insert_page(tree, folder_parts, title, href):
    """Sijoittaa sivun puuhun sen kansiopolun (kategoria > alikategoria > ...) mukaan."""
    get_node(tree, folder_parts)["pages"].append((title, href))


def folder_href(folder_parts):
    return "/".join(folder_parts + ("index.html",)) if folder_parts else "index.html"


def render_category_nav(display_name, folder_parts, node, prefix, current_href):
    category_href = folder_href(folder_parts)
    is_active = category_href == current_href
    css_class = "nav-category active" if is_active else "nav-category"
    aria = ' aria-current="page"' if is_active else ""
    parts = [
        "<li>",
        f'<a class="{css_class}"{aria} href="{prefix}{category_href}">{display_name}</a>',
        "<ul>",
    ]
    for title, href in node["pages"]:
        # aria-current + .active-luokka: nykyinen sivu ei saa erottua
        # navigaatiossa pelkästä väristä (WCAG 1.4.1).
        attrs = ' class="active" aria-current="page"' if href == current_href else ""
        parts.append(f'<li><a{attrs} href="{prefix}{href}">{title}</a></li>')
    for name, child in node["children"].items():
        parts.append(render_category_nav(humanize(name), folder_parts + (name,), child, prefix, current_href))
    parts.append("</ul></li>")
    return "\n".join(parts)


def render_nav(tree, prefix, current_href):
    parts = ['<ul class="nav">']
    if tree["pages"]:
        # "Yleiset" kattaa sisältökansion juureen suoraan laitetut sivut —
        # niiden "kansio" on sivuston juuri itse, joten linkki osoittaa
        # etusivulle, jossa ne muutenkin listataan.
        parts.append(render_category_nav("Yleiset", (), {"pages": tree["pages"], "children": {}}, prefix, current_href))
    for name, child in tree["children"].items():
        parts.append(render_category_nav(humanize(name), (name,), child, prefix, current_href))
    parts.append("</ul>")
    return "\n".join(parts)


def render_folder_body(node, folder_parts, prefix):
    """Listaa kansion suorat sivut ja alikategoriat (ei rekursiivisesti syvemmälle —
    alikategorioihin mennään klikkaamalla, kuten tiedostoselaimessa)."""
    parts = []
    if node["pages"]:
        parts.append("<ul>")
        for title, href in node["pages"]:
            parts.append(f'<li><a href="{prefix}{href}">{title}</a></li>')
        parts.append("</ul>")
    if node["children"]:
        parts.append("<ul>")
        for name, child in node["children"].items():
            child_href = folder_href(folder_parts + (name,))
            parts.append(f'<li><a href="{prefix}{child_href}">{humanize(name)}</a></li>')
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

    # Ensimmäinen ajo: lue metatiedot ja rakenna navigaatiopuu kansiorakenteen
    # mukaan (kansio = kategoria, alikansio = alikategoria, jne. mielivaltaisen
    # syvälle). "index.md" on erikoistapaus: se ei näy omana sivunaan
    # navigaatiossa, vaan sen sisältö toimii kyseisen kansion oman,
    # automaattisesti generoitavan index.html:n alkuosana.
    pages = []
    tree = new_node()
    for md_path in md_files:
        rel = md_path.relative_to(content_dir)
        folder_parts = rel.parts[:-1]
        text = md_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)

        if md_path.stem == "index":
            node = get_node(tree, folder_parts)
            node["index_meta"] = meta
            node["index_body"] = body
            continue

        title = meta.get("title", humanize(md_path.stem))
        href = str(rel.with_suffix(".html")).replace("\\", "/")
        pages.append((md_path, href, title, body))
        insert_page(tree, folder_parts, title, href)

    # Toinen ajo: renderöi jokainen sivu, kun koko navigaatio on tiedossa.
    for md_path, href, title, body in pages:
        html_body = wrap_tables(markdown.markdown(body, extensions=["tables", "fenced_code"]))
        prefix = path_prefix(href)
        nav_html = render_nav(tree, prefix, href)
        page_content = f"<h1>{title}</h1>\n{html_body}"
        page_html = render_page(base_template, site_title, title, href, nav_html, page_content)
        out_path = output_dir / Path(href)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page_html, encoding="utf-8")

    # Kolmas ajo: jokainen kansio (juuri mukaan lukien) saa oman
    # index.html:n, joka listaa kansion suorat sivut ja alikategoriat —
    # ja alkaa kansion "index.md":n sisällöllä, jos sellainen on.
    folder_count = 0

    def write_folder_index(node, folder_parts):
        nonlocal folder_count
        folder_count += 1
        href = folder_href(folder_parts)
        prefix = path_prefix(href)
        display_name = site_title if not folder_parts else humanize(folder_parts[-1])
        title = (node["index_meta"] or {}).get("title", display_name)

        body_parts = []
        if node["index_body"]:
            body_parts.append(
                wrap_tables(markdown.markdown(node["index_body"], extensions=["tables", "fenced_code"]))
            )
        body_parts.append(render_folder_body(node, folder_parts, prefix))

        page_content = f"<h1>{title}</h1>\n" + "\n".join(body_parts)
        page_html = render_page(base_template, site_title, title, href, render_nav(tree, prefix, href), page_content)
        out_path = output_dir / Path(href)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page_html, encoding="utf-8")

        for name, child in node["children"].items():
            write_folder_index(child, folder_parts + (name,))

    write_folder_index(tree, ())

    print(f"Generoitu {len(pages)} sivua ja {folder_count} kansioindeksiä kansioon {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--templates", required=True)
    parser.add_argument("--site-title", default="Sisältö")
    args = parser.parse_args()
    build(args.content, args.output, args.templates, args.site_title)
