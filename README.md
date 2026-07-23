# md-html-sivustogeneraattori

Generoi staattisen HTML-sivuston Markdown-tiedostoista. Ei tietokantaa, ei
palvelinpuolen ajonaikaista koodia — build-vaihe tuottaa pelkkiä `.html`- ja
`.css`-tiedostoja, jotka voi tarjoilla millä tahansa staattisella
web-palvelimella. Kaikki linkit ovat sivukohtaisesti suhteellisia, joten
sivusto toimii yhtä lailla verkkotunnuksen juuressa kuin alikansiossa.

Työkalu ei ole sidottu mihinkään tiettyyn sisältötyyppiin (ohjeet,
tiivistelmät, lunttilaput tms.) — sivuston nimi asetetaan `--site-title`
-parametrilla / `site-title`-inputilla jokaista sisältörepoa varten erikseen.

## Käyttö paikallisesti

```bash
pip install markdown
python3 build.py --content polku/sisaltoon --output _site --templates templates \
  --site-title "Oman sivustoni nimi"
```

## Käyttö GitHub Actionina toisesta reposta

```yaml
- uses: <organisaatio>/md-html-sivustogeneraattori@main
  with:
    content-dir: sisalto
    output-dir: _site
    site-title: "Oman sivustoni nimi"
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

Sisältörepo voi viitata joko:
- `@main` — käyttää aina uusinta versiota automaattisesti. Yksinkertaisinta,
  mutta generaattoriin tehty muutos vaikuttaa heti kaikkiin sitä käyttäviin
  sivustoihin seuraavalla julkaisulla.
- `@v1`-tyyppiseen tägättyyn releaseen (`git tag v1 && git push --tags`) —
  pysyy kiinteänä, kunnes joku päättää päivittää version numeron. Suositeltavaa,
  jos generaattoria käyttää useampi sisältörepo ja muutosten leviämistä halutaan
  hallita.
