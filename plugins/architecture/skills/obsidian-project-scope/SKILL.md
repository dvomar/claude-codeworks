---
name: obsidian-project-scope
description: Fáze 1 mapování libovolného projektu do Obsidian vaultu — CO systém umí (schopnosti), ne JAK to dělá. Fan-out průzkumných agentů po doménách, syntéza do propojených not. Použij při nástupu na neznámý projekt, při onboardingu, nebo když chybí přehled schopností. Spouštěj jako "/obsidian-project-scope", "zmapuj projekt do vaultu", "co ten systém vlastně umí".
---

# Obsidian Project Scope — fáze 1: mapa území

Zmapuje **libovolný** codebase do Obsidian vaultu na úrovni **schopností**: co systém umí, jaké scénáře pokrývá, čím se to zapíná. **Ne** jak to dělá — implementační hloubka je fáze 2 a tenhle skill ji vědomě nedělá.

## Kdy použít

- Nástup na neznámý projekt (vlastní i cizí).
- Onboarding nového člověka.
- Je potřeba říct produkťákovi/vedení, co ten systém umí — bez toho, aby to znamenalo číst kód.
- Před velkou změnou: „co všechno se toho může dotknout?"

## Kdy NEpoužít

- Když chceš vědět, *jak* něco funguje → to je fáze 2, ne tenhle skill.
- Na jeden modul/soubor → to je normální otázka, ne mapovací flow.

## Vstupy

| Vstup | Default |
|---|---|
| Kořen projektu | aktuální working directory |
| Vault | `/Users/mw/Library/Mobile Documents/iCloud~md~obsidian/Documents` |
| Jméno noty/složky | název kořenového adresáře projektu |

Když uživatel dá jinou cestu k vaultu nebo projektu, má přednost.

---

## Fáze A — Rekognoskace (dělá orchestrátor, ne agenti)

Cíl: zjistit, **na kolik domén projekt rozdělit**. Nedeleguj to — je to levné a určuje to kvalitu celého zbytku.

1. Přečti, co už projekt o sobě říká: `CLAUDE.md`, `README*`, `.claude/knowledge/**`, `docs/**`, `ARCHITECTURE*`.
2. Zjisti rozsah a stack:
   - .NET → `*.sln` (`grep -oE '^Project\("[^"]+"\) = "([^"]+)"'`)
   - JS/TS → `package.json` (workspaces), `nx.json`, `turbo.json`
   - Python → `pyproject.toml`, `setup.py`, adresáře balíčků
   - Go → `go.mod`, `cmd/`, `internal/`
   - jinak → adresáře nejvyšší úrovně + build soubory
3. Najdi **composition root / entry point** (`Program.cs`, `main.*`, `app.*`, `index.*`) — obvykle je v něm switch/registrace, která ti prozradí celou mapu modulů naráz.
4. Najdi **feature flagy / zapínače** (`EnabledDevices`, `features`, env proměnné) — ty říkají, co je volitelné.
5. **Ověř si nesrovnalosti sám.** Když dokumentace mluví o modulu, který není v build souboru, je to nález — ne fakt. Nezapisuj do vaultu nic, co jsi neviděl na disku.

### Rozdělení na domény

Rozděl projekt na **3–6 domén** podle toho, co dělají — **ne** podle adresářů. Domény si nesmí lézt do zelí a dohromady musí pokrýt všechno.

Vodítko: doména ≈ „skupina schopností, které dávají smysl jednomu člověku". Např. u platebního kiosku: *peníze* · *hardware* · *periferie a výstupy* · *integrace* · *platforma*. U SaaS spíš: *doména produktu* · *auth a tenanti* · *billing* · *integrace* · *platforma a data*.

Malý projekt (< 15 modulů) → klidně 1 agent, nedělej fan-out pro nic za nic.

---

## Fáze B — Fan-out průzkumných agentů

Pusť **jednoho agenta na doménu, všechny paralelně v jedné zprávě** (`subagent_type: Explore`, `model: sonnet`, `run_in_background: false`).

Do promptu každého agenta dej:

1. **Tvrdé vymezení domény** — konkrétní projekty/adresáře, ne „něco kolem plateb". Agent nesmí lézt jinam.
2. **Zákaz hloubky, doslova.** Tenhle odstavec dej do promptu vždy:
   > Zajímá mě BIG PICTURE na úrovni SCHOPNOSTÍ — CO systém umí, ne JAK to dělá. Nezajímají mě algoritmy, protokoly, třídy, metody, DI registrace. Piš tak, aby tomu rozuměl produkťák nebo nový vývojář, který ještě nezná kód. Toto je fáze 1 (mapa území), hloubku řešíme příště.
3. **Osu, po které má jít.** Nejlevnější a nejspolehlivější zdroj schopností jsou **interfaces** — `IPayOut`, `IFloat`, `IInvoiceService` ti řeknou, co systém umí, aniž bys četl jedinou implementaci. Dál: hub/controller/route metody (= API pro klienta), entry point switch, config klíče. Řekni agentovi explicitně: *„interfaces = schopnosti, použij je jako osu"*.
4. **Požadavek na nálezy, ne jen popis.** Chtěj po agentovi, ať aktivně hlásí: `NotImplementedException`, no-op stuby, mrtvý/nereferencovaný kód, drift mezi dokumentací a realitou. Tohle je z celého mapování to nejcennější — a agent to najde jen tehdy, když si o to řekneš.
5. **Kotvy pro fázi 2** — max 10 `soubor:řádek` s odůvodněním. Bez nich je fáze 2 slepá.

Jednotný výstupní formát (drž ho napříč agenty, ať jde syntéza slepit):

```
## Doména: <název>
### Co to umí (schopnosti)
### Provozní scénáře
### Architektonické sekce
- **<Sekce>** — 1 věta | projekty: X, Y
### Konfigurovatelné chování
### Nálezy (nedokončené / mrtvé / drift)
### Kotvy pro hloubkovou analýzu
- path:line — proč
```

---

## Fáze C — Ověření (orchestrátor, nepřeskakuj)

Agenti si **protiřečí** a **věří dokumentaci**. Než začneš psát vault:

1. **Křížové rozpory** — když dva agenti tvrdí opak, ověř si to sám jedním grepem. Vyhrává disk, ne dokumentace.
2. **Existuje to vůbec?** Každý modul, který agent zmínil jako funkční, musí být v build souboru. Ověř hromadně.
3. **Nezapisuj nic, co nemáš ověřené.** Když si nejsi jistý, napiš to do noty s nálezy jako otevřenou otázku, ne jako fakt do popisu schopností.

---

## Fáze D — Zápis do vaultu

Struktura (drž ji, ať jsou vaulty napříč projekty stejné):

```
<Vault>/<Projekt>/
├── <Projekt>.md                ← MOC, jediný vstupní bod
├── Sekce/
│   ├── <Schopnost 1>.md
│   └── <Schopnost 2>.md
└── Nálezy/                     ← vždy, i kdyby byl prázdný
    ├── _Nálezy.md              ← index s tabulkou
    └── <PRE>-001 <název>.md    ← jedna nota = jeden defekt
```

### MOC (`<Projekt>.md`)

- Callout na začátku: **tohle je fáze 1, popisuje CO, ne JAK.**
- Odstavec „co to je" — jednou větou k čemu ten systém vůbec je, lidsky.
- Odstavec „co to dělá" — hlavní use case v jedné až dvou větách, jazykem uživatele.
- Rozcestník `[[odkazů]]` na sekce, seskupený tematicky (ne abecedně).
- **Architektonická pravidla, která platí všude** — ta 2–3, o která se každý rozbije (vzájemné vyloučení, jediný vypínač, jediný transport…).
- Tabulka kotev: kde začít číst.

### Sekce (`Sekce/*.md`)

Jedna nota = **jedna schopnost**, ne jeden projekt. Šablona:

```markdown
---
tags: [schopnost, <doména>]
project: <Projekt>
phase: scope
---
# <Název>

<Jedna věta: k čemu to je.>

## Co to umí
- <schopnosti, konkrétně, jazykem uživatele>

## Co to (ještě) neumí
- <jen když je co říct — odkaz na notu s nálezy>

## <Podporovaný hardware / systémy / providery>
| ... | ... | zapíná se klíčem |

## Souvisí
<[[odkazy]] v běžné větě, ne jako seznam>

## Kotvy
- `path:line` — proč
```

### Nálezy — vždy, a vždy jako samostatné noty

Tohle je z celého běhu **nejcennější výstup**. Bez něj je vault nebezpečně optimistický — čtenář uvěří, že systém umí věci, které neumí.

Nestačí nálezy vyjmenovat v jedné narativní notě. **Každý defekt je vlastní nota**, aby se na něj dalo navázat, filtrovat ho a udělat z něj issue, aniž by ho někdo musel znovu hledat v kódu.

Frontmatter (tohle je to, co dělá nálezy adresovatelnými — nešidit):

```yaml
---
tags: [nález, bug]          # bug | gap | drift
id: <PRE>-001               # prefix podle projektu, průběžně číslované
type: bug                   # bug = funguje špatně / lže
                            # gap = chybí, ale nic to nerozbíjí
                            # drift = dokumentace ≠ realita
severity: high              # high | medium | low — podle ceny selhání, ne obtížnosti
status: open                # open | done (+ odkaz na commit)
area: "[[<Sekce, které se to týká>]]"
evidence:
  - "path/to/file.cs:42"    # bez důkazu to není nález, ale dojem
project: <Projekt>
found: <YYYY-MM-DD>
---
```

Tělo vždy ve čtyřech krocích — poslední je ten, kvůli kterému to celé píšeš:

1. **Co je špatně** — fakticky, bez hodnocení.
2. **Jak se to projeví** — v provozu, jazykem důsledku. Ne „metoda vrací null", ale „zákazníkovi se strhnou peníze a nikdo je nestornuje".
3. **Co s tím** — návrh, včetně varianty „smazat to". Když jsou legitimní cesty dvě, nabídni obě a řekni, že je potřeba rozhodnout.
4. **Hotovo, když** — zaškrtávací akceptační kritéria. Z téhle sekce má jít udělat issue bez přemýšlení.

Index `Nálezy/_Nálezy.md`: tabulky po typu (chyby / nedodělky / drift), sloupce ID · nález · závažnost · oblast. Nahoře callout **odkud to je a že to nebyl cílený audit** — nálezy vznikly jako vedlejší produkt mapování, takže seznam není úplný a nesmí se tak tvářit.

**Závažnost podle ceny selhání, ne podle obtížnosti opravy.** Hledej vzorec napříč nálezy — když jich několik sdílí kořen (např. *„systém tvrdí, že něco udělal, i když neudělal"*), napiš to do indexu. To je informace, kterou jednotlivé noty nenesou.

### Pravidla psaní not

- **Česky, identifikátory anglicky.** Názvy projektů, config klíčů, tříd a souborů se nepřekládají.
- **Linkuj hojně** — `[[wikilink]]` uvnitř věty, ne jako seznam „viz také". Graph view je pak k něčemu.
- **Žádné číslování** sekcí, pokud pořadí nenese informaci.
- **Konkrétní čísla a klíče**, ne „několik zařízení". Buď to víš, nebo to tam nepiš.
- Callouty `> [!warning]` na pasti, `> [!danger]` na nálezy, `> [!note]` na překvapení.

---

## Fáze E — Kontrola (poslední krok, nepřeskakuj)

```bash
# všechny wikilinky musí vést na existující noty
python3 - <<'EOF'
import os, re, glob
ROOT = "<vault>/<Projekt>"
files = glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)
names = {os.path.splitext(os.path.basename(f))[0] for f in files}
broken = [(os.path.basename(f), l.strip())
          for f in files
          for l in re.findall(r'\[\[([^\]|#]+)', open(f, encoding="utf-8").read())
          if l.strip() not in names]
print(f"not: {len(files)}")
print("ROZBITÉ:", broken or "žádné")
EOF
```

Pak uživateli **řekni nálezy** — hlavně rozpory mezi dokumentací a realitou. To je to, za co si tenhle běh zaplatil.

## Co tenhle skill vědomě nedělá

Nečte implementace do hloubky. Nekreslí sekvenční diagramy. Nemapuje datové toky. Nedělá závislostní graf. **To je fáze 2** — a ta má smysl teprve tehdy, když existuje tahle mapa.
