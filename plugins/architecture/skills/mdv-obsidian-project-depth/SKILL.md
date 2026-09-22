---
name: mdv-obsidian-project-depth
description: 'Fáze 2 hloubkové analýzy projektu do Obsidian vaultu — JAK kritické cesty reálně fungují (sekvence, tok dat, blast radius), ne CO systém umí. Navazuje na fázi 1 (obsidian-project-scope): bere její kotvy, pustí hloubkové agenty na nosné cesty, ověří jejich tvrzení a zapíše toky do vaultu. Použij, když už existuje mapa z fáze 1 a chceš vystopovat konkrétní tok/mechanismus, zjistit skutečný dopad nálezu (co se stane, když vypálí), nebo ověřit, co je reálně nasazené. Spouštěj jako "/mdv-obsidian-project-depth", "fáze 2", "jak to reálně funguje", "vystopuj tok X", "jaký je blast radius toho nálezu", "co je reálně nasazené".'
---

# Obsidian Project Depth — fáze 2: jak to funguje

Vezme mapu z fáze 1 (skill `obsidian-project-scope`) a jde do hloubky na **vybraných nosných cestách**: jak reálně fungují, kudy teče hodnota, a co se stane, když defekt vypálí. **Ne** další mapa schopností — to je fáze 1. Tenhle skill vědomě dělá přesně to, co fáze 1 odmítá.

Fáze 1 řekne, že defekt **existuje**. Fáze 2 řekne, jestli **záleží** a co přesně se stane.

## Kdy použít

- Fáze 1 je hotová (existuje vault s mapou a kotvami) a chceš pochopit *jak* konkrétní věc funguje.
- Před zásahem do rizikové cesty (peníze, bezpečnost, hardware) — potřebuješ vědět blast radius dřív, než sáhneš na kód.
- Nález z fáze 1 potřebuje prioritizaci: je ta vadná věc vůbec nasazená? Co se stane po selhání?
- „Vystopuj mi tok X od začátku do konce.“

## Kdy NEpoužít

- **Bez fáze 1.** Bez mapy a kotev je fáze 2 slepá — nevíš, kam kopat, a skončíš u remapování celého repa. Když vault z fáze 1 neexistuje, pusť nejdřív `obsidian-project-scope`.
- Na celý codebase najednou. Fáze 2 je cílená hloubka na 3–6 kotvách, ne plošná. Plošnou hloubku nikdo nepřečte a stojí majlant.
- Když chceš jen vědět, *co* systém umí → to je fáze 1.

## Vstupy

| Vstup | Default |
|---|---|
| Vault z fáze 1 | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<Projekt>/` |
| Kořen projektu | aktuální working directory |
| Kotvy | sekce `## Kotvy` v notách + `Kotvy pro hloubkovou analýzu` v nálezech |

Když uživatel dá jinou cestu, má přednost.

---

## Fáze A — Výběr kotev (dělá orchestrátor, ne agenti)

Cíl: vybrat **3–6 nosných cest**, které se vyplatí prohloubit. Nedeleguj to — je to levné a rozhoduje, jestli fáze 2 přinese hodnotu, nebo utopí tokeny v nedůležitých místech.

1. Přečti vault z fáze 1: MOC, sekce, a hlavně `Nálezy/` a všechny `## Kotvy`. Fáze 1 ti kotvy naservírovala schválně — použij je.
2. Vyber kotvy podle **ceny selhání**, ne podle zajímavosti. Přednost mají:
   - cesty, kde tečou peníze nebo se rozhoduje o penězích,
   - bezpečnostní cesty (auth, tajemství, přístup),
   - kritické nálezy z fáze 1, u kterých není jasný dopad ani rozsah,
   - „lže o úspěchu“ vzorce (kód hlásí hotovo, aniž to udělal) — u těch je blast radius vždy nejasný.
3. Přidej **jednu kotvu navíc: realitu nasazení.** Skoro vždy se vyplatí zjistit, co je reálně zapnuté v configu — to přeřadí priority ostatních nálezů (vada na nenasazeném zařízení je latentní, ne živá).
4. Formuluj u každé kotvy **konkrétní otázku**, ne téma. Ne „platby“, ale „když zápis do ERP selže, pokračuje výdej zboží? vydá kiosek hodnotu, i když účetnictví o platbě neví?“. Otázka řídí hloubku.

Malý projekt / jedna kotva → jeden agent, nedělej fan-out pro nic.

---

## Fáze B — Fan-out hloubkových agentů

Pusť **jednoho agenta na kotvu, všechny paralelně v jedné zprávě**.

> [!important] `general-purpose`, ne `Explore`
> Fáze 1 používá `Explore` (čte výřezy, hledá). Fáze 2 potřebuje **trasovat volací řetězce a číst celé soubory** — na to je `general-purpose` (subagent_type: `general-purpose`, `run_in_background: false`, ať máš všechny výsledky v jednom kole a můžeš je slepit). `Explore` na hloubku nestačí — vrátí výřezy, ne sekvenci.

Do promptu každého agenta dej:

1. **Zrušení zákazu hloubky, doslova.** Tohle je opak fáze 1, řekni to explicitně:
   > FÁZE 2 (hloubka: JAK to funguje). NENÍ to mapování schopností — chci implementační detail, sekvenci a tok dat, s `soubor:řádek` u každého kroku. Žádné změny kódu, jen čtení a analýza.
2. **Konkrétní otázku z fáze A**, ne téma. A odkaz na relevantní nález z fáze 1, ať agent staví na tom, co už víme, a neremapuje.
3. **Startovní kotvy** (`soubor:řádek` z fáze 1) — odkud začít trasovat. Bez nich agent bloudí.
4. **Výstupní kontrakt** (drž ho napříč agenty, ať jde syntéza slepit) — čtyři věci, které dělají fázi 2 fází 2:
   - **Sekvence** — krok za krokem, s `soubor:řádek`, od vstupu (hub/API/trigger) po konec.
   - **Tok dat** — kde se hodnota transformuje, v jakých jednotkách, kde se ztrácí/zahazuje.
   - **Mechanismus defektu s důkazem** — ne „vypadá to špatně“, ale přesně proč, doražené na kód.
   - **Blast radius** — co se stane PO selhání: pokračuje proces? koroumpuje se stav? nebo je to tichý no-op mimo kritickou cestu? Tohle je nejcennější výstup — mění „existuje bug“ na „tohle se stane, když vypálí“.
5. **Realita nasazení** (u té jedné kotvy): projdi všechny configy (referenční, klientské, vzorky) a sestav matici — co je reálně zapnuté. A rozliš produkční hodnoty od simulátorů/vzorků. Když v repu reálné produkční hodnoty nejsou, je to závěr sám o sobě (produkční realita žije mimo repo → nutno se zeptat týmu).

Jednotný výstupní formát agenta:

```
### Sekvence (kroky s soubor:řádek)
### Tok dat (kde se hodnota mění / ztrácí)
### Mechanismus defektu (s důkazem)
### Blast radius (co se stane po selhání)
### Realita nasazení (pokud relevantní)
### Co nevím jistě (klíčové neznámé pro opravu)
### Kotvy (soubor:řádek, které jsem ověřil)
```

Sekce „Co nevím jistě“ je záměrná: nutí agenta oddělit ověřené od odhadnutého. To, co nejde ověřit z repa (např. co posílá frontend z jiného repozitáře), je klíčové pro opravu a nesmí se zamlčet ani vydávat za fakt.

---

## Fáze C — Ověření (orchestrátor, NEPŘESKAKUJ)

Tohle je disciplína, která odděluje fázi 2 od „agenti něco napsali“. **Agenti chybují, protiřečí si a přehánějí.** Každý **nový nosný claim** ověř sám, než ho zapíšeš do vaultu.

1. **Ověřuj to, co nese váhu.** Nový mechanismus, nový blast radius, nový nález, tvrzení o rozsahu („týká se i driveru Y“), tvrzení o architektuře („dvě generace“, „net8 vs net6“). Neztrácej čas ověřováním toho, co už fáze 1 ověřila.
2. **Grep/read, ne důvěra.** Jeden cílený příkaz obvykle stačí. Když agent tvrdí framework/verzi/rozsah, přečti `.csproj`/config/zdroj — agenti si tyhle věci s oblibou domýšlejí.
3. **Rozpory vyhrává disk.** Když dva agenti tvrdí opak, rozhodni to sám čtením, ne váhou argumentu.
4. **Co neověříš, napiš jako otevřenou otázku**, ne jako fakt. Zvlášť věci mimo repo (frontend, hardware, produkční config) patří do „Co nevím jistě“, ne do popisu mechanismu.

Bez tohohle průchodu fáze 2 šíří sebejisté nesmysly hlouběji než fáze 1 — protože zní autoritativněji (sekvence, `soubor:řádek`).

---

## Fáze D — Zápis do vaultu

Struktura (vedle výstupu fáze 1, ne místo něj):

```
<Vault>/<Projekt>/
├── <Projekt>.md            ← MOC z fáze 1: přidej odkaz na [[_Fáze 2]]
├── Sekce/                  ← z fáze 1, neměň
├── Nálezy/                 ← z fáze 1; přidej nové nálezy z fáze 2, aktualizuj přeřazené
└── Fáze 2/
    ├── _Fáze 2.md          ← index: seznam toků + co fáze 2 změnila na prioritách
    └── Tok <název>.md      ← jedna nota = jeden tok/kotva
```

### Index `Fáze 2/_Fáze 2.md`

- Callout „co je fáze 2“ a že navazuje na fázi 1.
- Rozcestník na noty toků.
- **Tabulka „co fáze 2 změnila na prioritách“** — pro každý dotčený nález: co řekla fáze 1 vs. co upřesnila fáze 2 (typicky: latentní vs. živé, rozšíření rozsahu, blast radius). Tohle je hlavní přidaná hodnota fáze 2 — nese ji index, ne jednotlivé noty.
- Sekce „Co fáze 2 NEzjistí z repa“ — poctivě, co zůstává neznámé a kde se to zjistí (tým, monitoring panel, jiný repo).

### Noty toků `Fáze 2/Tok *.md`

Jedna nota = jeden tok. Frontmatter `tags: [fáze2, tok, <doména>]`, `phase: depth`. Tělo drží výstupní formát agenta (sekvence → tok dat → mechanismus → blast radius → realita → co nevím → kotvy), přepsané do čtivé češtiny. Callouty `> [!danger]` na jádro problému, `> [!warning]` na pasti. Linkuj hojně na sekce a nálezy z fáze 1.

### Nálezy

- **Nové nálezy z fáze 2** dostanou vlastní notu (stejný formát jako fáze 1: co je špatně / jak se projeví / co s tím / hotovo když) a řadu do indexu `Nálezy/_Nálezy.md`. Očísluj je navazující řadou a označ „(fáze 2)“.
- **Přeřazené nálezy** z fáze 1 aktualizuj: doplň zpětný odkaz na notu toku a uprav prioritu, když realita nasazení ukázala latentní vs. živé. Neměň závěr fáze 1 potají — dopiš, co fáze 2 zjistila.
- Cross-linkuj: nález ↔ tok, který ho vysvětluje.

### Pravidla psaní

Stejná jako fáze 1: česky, identifikátory anglicky, `[[wikilink]]` uvnitř vět, konkrétní čísla a `soubor:řádek`, žádné nepodložené tvrzení. Blast radius piš jazykem důsledku, ne kódu — ne „metoda vrací true“, ale „zákazník dostane nefunkční kartu a kiosek to hlásí jako úspěch“.

---

## Fáze E — Kontrola (poslední krok, nepřeskakuj)

Stejný link-check jako fáze 1 — všechny wikilinky musí vést na existující noty (pozor na tabulkový escape `\|`):

```bash
python3 - <<'EOF'
import os, re, glob
ROOT = "<vault>/<Projekt>"
files = glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)
names = {os.path.splitext(os.path.basename(f))[0] for f in files}
broken = [(os.path.basename(f), t)
          for f in files
          for l in re.findall(r'\[\[([^\]|#]+)', open(f, encoding="utf-8").read())
          for t in [l.strip().rstrip('\\').strip()]
          if t not in names]
print(f"not: {len(files)}")
print("ROZBITÉ:", broken or "žádné")
EOF
```

Pak uživateli **řekni, co fáze 2 změnila** — hlavně přeřazení priorit (co bylo kritické a je latentní, co je naopak živé) a nové nálezy. To je to, za co si tenhle běh zaplatil.

## Co tenhle skill vědomě nedělá

- **Neopravuje kód.** Fáze 2 je analýza — vystopuje a zapíše, nesahá na implementaci. Oprava je samostatný krok s vlastním plánem a review.
- **Neremapuje schopnosti.** To je fáze 1. Když zjistíš, že mapa z fáze 1 je děravá, doplň fázi 1, nedělej to tady.
- **Nejde plošně.** Cílená hloubka na nosných kotvách, ne hloubka všude. Plošná hloubka je fáze 1 udělaná draze a špatně.
