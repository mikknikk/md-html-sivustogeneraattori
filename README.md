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

## Kansioiden index-sivut ja `index.md`

Jokainen kansio — myös sisältökansion juuri eli koko sivuston etusivu —
saa automaattisesti oman `index.html`:n, joka listaa kyseisen kansion
suorat sivut ja alikategoriat (linkkeinä niiden omiin index-sivuihin;
listaus ei mene rekursiivisesti syvemmälle, samaan tapaan kuin
tiedostoselaimessa selataan kansio kerrallaan). Navigaatiossa
**kategorian nimi on linkki tähän kansion omaan index-sivuun.**

Navigaation kategoriat ovat lisäksi avattavia/suljettavia natiivilla
HTML:n `<details>`/`<summary>`-elementillä — ei JavaScriptiä, toimii
näppäimistöllä (Enter/Space) ja ruudunlukijalla automaattisesti.
Oletuksena kategoria on kiinni, paitsi jos se sisältää nykyisen sivun
(suoraan tai jonkin alikategorian kautta) — tällöin se ja kaikki sen
sisältävät emokategoriat avautuvat automaattisesti, jotta nykyinen
sijainti ei jää piiloon. Auki/kiinni-tila näkyy kolmiomerkin suunnasta
(▸/▾), ei pelkästä väristä.

Jos kansiossa on tiedosto nimeltä `index.md`, sen front matterin
`title`-arvo (jos annettu) ja sisältö näytetään ennen tuota automaattista
listausta:

```
sisalto/
  tietokoneet/
    index.md
    git.md
```

`index.md` toimii tavallisten sääntöjen mukaan (front matter valinnainen,
loppuosa Markdownia) mutta **ei näy omana rivinään navigaatiossa** —
kategorianimen linkki johtaa jo tähän samaan sivuun, joten erillistä
nav-riviä ei tarvita.

`index.md`:n `title` vaikuttaa myös sivupalkin kategorianimeen, ei
pelkästään kansion omaan sivuun. Tämä on tarpeen, kun kansionimestä
johdettu oletusnimi ei kelpaa sellaisenaan — esim. `humanize()` muuttaisi
kansion `vscode` näyttönimeksi "Vscode", ei "VS Code". Aseta tällöin
`sisalto/tietokoneet/vscode/index.md`:hen `title: VS Code`.

## Sisällön järjestäminen

Kansiot ja tiedostot listataan navigaatiossa sekä etusivulla aakkos-/
polkujärjestyksessä. Jos oletusjärjestys ei kelpaa, nimeä kansio tai
tiedosto numeroetuliitteellä (`NN-nimi`), esim.:

```
sisalto/
  01-tietokoneet/
    01-git.md
    02-editorit/
      01-vscode.md
      02-vim.md
  02-kielet/
    espanja.md
```

Generaattori piilottaa `NN-`-etuliitteen näkyvästä nimestä automaattisesti
— "01-tietokoneet" näkyy navigaatiossa pelkkänä "Tietokoneet". Etuliite
vaikuttaa vain lajittelujärjestykseen. Käytä kaksinumeroista (tai
useampinumeroista) etuliitettä heti alusta, jos kategorioita/tiedostoja voi
myöhemmin tulla kymmenen tai enemmän — muuten "10-..." lajittuu
aakkosjärjestyksessä ennen "2-...":a merkkijonovertailun vuoksi. Kansiot tai
tiedostot ilman numeroetuliitettä toimivat edelleen normaalisti; numerointia
tarvitsee käyttää vain siellä, missä oletusjärjestys ei kelpaa.

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
