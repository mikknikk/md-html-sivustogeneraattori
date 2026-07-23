# md-html-sivustogeneraattori

Generoi staattisen HTML-sivuston Markdown-tiedostoista. Ei tietokantaa, ei
palvelinpuolen ajonaikaista koodia — build-vaihe tuottaa pelkkiä `.html`- ja
`.css`-tiedostoja, jotka voi tarjoilla millä tahansa staattisella
web-palvelimella.

## Käyttö paikallisesti

```bash
pip install markdown
python3 build.py --content polku/sisaltoon --output _site --templates templates
```

## Käyttö GitHub Actionina toisesta reposta

```yaml
- uses: <organisaatio>/md-html-sivustogeneraattori@v1
  with:
    content-dir: sisalto
    output-dir: _site
```

## Sisältökansion rakenne

```
sisalto/
  ohjelmisto-a/
    pikaohje.md
  ohjelmisto-b/
    lunttilappu.md
```

Alikansion nimi näkyy navigaatiossa kategoriana. Jokainen `.md`-tiedosto voi
alkaa valinnaisella front matterilla:

```
---
title: Sivun otsikko
---

Loppuosa on Markdownia.
```

## Julkaisu

Tämän repon tehtävä on ainoastaan generoida sivusto — se ei sisällä
deploy-logiikkaa eikä sisältöä. Ks. `lunttilaput`-repo esimerkkinä siitä,
miten sisältörepo kutsuu tätä actionia ja vie lopputuloksen palvelimelle.

## Versiointi

Kun teet muutoksia, tägää release (esim. `git tag v1 && git push --tags`),
jotta sisältörepot voivat viitata kiinteään, tunnettuun versioon eivätkä
`main`-haaraan.
