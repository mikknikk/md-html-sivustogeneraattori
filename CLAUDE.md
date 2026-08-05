# md-html-sivustogeneraattori

Geneerinen, uudelleenkäytettävä Markdown → staattinen HTML -sivugeneraattori.
Ei JavaScriptiä, ei tietokantaa, ei muita riippuvuuksia kuin `markdown`-pip-paketti.
Tarkoitettu vietäväksi palvelimelle ja unohdettavaksi mahdollisimman pienellä
pitkän aikavälin ylläpito- ja tietoturvariskillä — tämä periaate ohjaa kaikkia
toteutuspäätöksiä: jos johonkin ominaisuuteen tarvittaisiin JS tai uusi
riippuvuus, etsi ensin pelkällä HTML/CSS:llä tai Pythonin vakiokirjastolla
toteutettava vaihtoehto.

## Arkkitehtuuri (`build.py`)

- Sisältö luetaan kansiopuuna: jokainen kansio muodostaa kategorian, alikansio
  alikategorian — rajaton syvyys. Puu rakennetaan `new_node()`/`get_node()`/
  `insert_page()`-funktioilla.
- `index.md` on erikoistapaus: sen sisältö näytetään ennen kansion
  automaattisesti generoitua sivulistausta, mutta se ei näy omana rivinään
  navigaatiossa. `index.md`:n front matterin `title` ylikirjoittaa myös
  navigaation kategorianimen (`category_title()`-funktio) — tarvitaan, koska
  `humanize()` ei osaa tuottaa esim. "VS Code" tai "Web-kehitys" pelkästä
  kansionimestä (`vscode`, `web-kehitys`).
- Kansion/tiedoston voi nimetä `NN-nimi`-muotoon pakottaakseen
  lajittelujärjestyksen (oletus on aakkos-/polkujärjestys). `humanize()`
  piilottaa `NN-`-etuliitteen näkyvästä nimestä automaattisesti.
- Jokainen kansio (myös sisältökansion juuri) saa oman `index.html`:n, joka
  listaa VAIN suorat sivut/alikategoriat — ei rekursiivisesti syvemmälle.
  Navigaatiossa (sivupalkki) näytetään sen sijaan koko puu rekursiivisesti,
  `<details>`/`<summary>`-elementteinä: kiinni oletuksena, auki jos kategoria
  sisältää nykyisen sivun (`category_contains_active()`).
- Kaikki linkit ovat sivukohtaisesti suhteellisia (`path_prefix()`), joten
  sivusto toimii sekä verkkotunnuksen juuressa että alikansiossa.

## Saavutettavuus ja mobiilioptimointi

Sivusto pyrkii WCAG 2.1 AAA -tasoon (ks. README.md:n "Saavutettavuus"-osio
tarkemmista perusteluista ja tietoisesti rajatuista poikkeuksista 3.1.3/
3.1.4/3.1.5). Keskeistä: kontrastit ≥7:1 sekä vaaleassa että
`prefers-color-scheme: dark` -teemassa, `aria-current`+ei-väripohjainen
korostus aktiiviselle sivulle/kategorialle, 44×44px kosketuskohteet,
skip-link, `prefers-reduced-motion`-tuki, `max-width: 700px` -mobiililayout
ilman JS:ää.

## Testausproseduuri (aja AINA ennen pushia)

```bash
python3 -m venv /tmp/test-venv
/tmp/test-venv/bin/pip install --quiet markdown
/tmp/test-venv/bin/python3 build.py --content <sisältöpolku> --output /tmp/test-output \
  --templates templates --site-title "Testiotsikko"

# Rakenteelliset tarkistukset (grep riittää useimmiten):
# - otsikkohierarkia ei hyppää (h1->h2->h3, ei h1->h3)
# - nav sisältää odotetut linkit ja aria-current oikeassa paikassa

# Selainvarmistus (aina generaattori-/CSS-muutoksille, valinnainen pienille
# sisältölisäyksille): serve /tmp/test-output http.serverillä ja tarkista
# Claude_Browser-työkaluilla.

rm -rf /tmp/test-venv /tmp/test-output   # siivoa aina lopuksi
```

Aja myös regressiona oikeaa `lunttilaput`-sisältöä vasten (toinen repo,
todennäköisesti kloonattuna vierekkäin) ennen build.py-muutosten pushia.

## Julkaisu ja versiointi

Sisältörepot (esim. `lunttilaput`) käyttävät tätä GitHub Actionina:
`uses: <org>/md-html-sivustogeneraattori@main` tai `@vN`-tägiin lukittuna.
`@main` levittää muutokset heti kaikkiin sitä käyttäviin sivustoihin niiden
seuraavalla julkaisulla — tägättyä versiota kannattaa harkita, jos useampi
sisältörepo alkaa käyttää generaattoria.

## Commit-tyyli

Kuvaile mitä muutettiin, miksi, ja mitä testattiin ennen pushia (ks. `git log`
esimerkkeinä). Ei lyhyitä yhden rivin committeja tässä projektissa.
