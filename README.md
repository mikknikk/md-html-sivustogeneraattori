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

Alikansion nimi näkyy navigaatiossa kategoriana. Kansioita voi sisäkkäistää
mielivaltaisen syvälle — jokainen taso muodostaa oman, sisennetyn
alikategoriansa sekä navigaatiossa että etusivun listauksessa:

```
sisalto/
  tietokoneet/
    git.md
    editorit/
      vim.md
      vscode.md
  kielet/
    espanja.md
```

Tästä syntyy navigaatioon rakenne "Tietokoneet" > ("Git" ja alikategoria
"Editorit" > "Vim", "VS Code") sekä erikseen "Kielet" > "Espanja". Juuri
`sisalto/`-kansioon suoraan laitetut `.md`-tiedostot (ilman mitään
alikansiota) ryhmitellään "Yleiset"-kategorian alle.

Jokainen `.md`-tiedosto voi alkaa valinnaisella front matterilla:

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

## Saavutettavuus ja mobiilioptimointi

Generoitu sivusto pyrkii WCAG 2.1 AAA -tasoon ilman JavaScriptiä tai uusia
riippuvuuksia:

- **Kontrasti (1.4.6):** väripaletti (vaalea + `prefers-color-scheme: dark`)
  läpäisee 7:1 (teksti) / 4.5:1 (UI) kaikissa yhdistelmissä.
- **Värinvalinta (1.4.8):** tumma/vaalea teema seuraa käyttöjärjestelmän
  asetusta automaattisesti — ei vaadi JS:ää eikä kirjautumista.
- **Ei pelkkää väriä tiedon välittäjänä (1.4.1):** aktiivinen navigaatiolinkki
  merkitään `aria-current="page"`:lla ja ei-väripohjaisella lihavoinnilla/
  reunaviivalla värin lisäksi.
- **Kosketuskohteet (2.5.5):** navigaatiolinkeillä on vähintään 44×44px
  kosketusalue — tämä on samalla tärkein mobiilioptimointikorjaus.
- **Ohituslinkki, otsikkohierarkia, focus-visible:** "Siirry sisältöön"
  -linkki, looginen H1→H2-rakenne jokaisella sivulla, selkeästi näkyvä
  fokusrengas.
- **Mobiili:** navigaatio pinoutuu sisällön yläpuolelle kapealla näytöllä
  (`max-width: 700px`) ilman JS-toteutteista piilotusta/hampurilaisvalikkoa —
  koko navigaatio pysyy aina näkyvissä ja normaalissa dokumenttivirtauksessa.
- **Taulukot ja koodilohkot:** vierittyvät omassa kääreessään kapealla
  näytöllä sen sijaan että pakottaisivat koko sivun vaakavieritykseen.

**Tietoisesti rajattu ulkopuolelle:** kriteerit 3.1.3 (epätavalliset sanat),
3.1.4 (lyhenteiden avaukset) ja 3.1.5 (lukutaso) eivät sovi järkevästi
CLI-komentoihin ja tekniseen sanastoon perustuvaan sisältöön — niiden täysi
toteutus (esim. jokaisen komennon selittäminen tai sisällön yksinkertaistaminen
peruskoulutasolle) heikentäisi sisällön käyttökelpoisuutta kohdeyleisölle
eikä oikeasti palvelisi saavutettavuutta. Muilta osin sivusto pyrkii
AAA-tasoon.

## Versiointi

Sisältörepo voi viitata joko:
- `@main` — käyttää aina uusinta versiota automaattisesti. Yksinkertaisinta,
  mutta generaattoriin tehty muutos vaikuttaa heti kaikkiin sitä käyttäviin
  sivustoihin seuraavalla julkaisulla.
- `@v1`-tyyppiseen tägättyyn releaseen (`git tag v1 && git push --tags`) —
  pysyy kiinteänä, kunnes joku päättää päivittää version numeron. Suositeltavaa,
  jos generaattoria käyttää useampi sisältörepo ja muutosten leviämistä halutaan
  hallita.
