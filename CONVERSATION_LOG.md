# Samtale Log - Timeregnskab Projekt

Dato: 30. april 2026 (opdateret 1. maj 2026)

## Brugerens ønske
- Automatiseret timeregnskab til 3-8 medarbejdere
- Medarbejdere skal selv kunne indtaste deres timer via webformular
- Registrering af: Ferie/fridage, sygedage og feriedage + ekstra timer (varierer per medarbejder)
- Påmindelser til dem der mangler at udfylde (før bestemt dato)
- Automatisk opsamling af data til administrator
- **Vigtigt:** Medarbejdere må ikke kunne se hinandens data - separate links/tokens

## Valg af teknologi

### Løsning: Streamlit Cloud + GitHub
- Streamlit Cloud app med GitHub repo som datalager
- Unikke links (tokens) i stedet for login
- Admin interface i appen til at administrere medarbejdere
- GitHub Actions til automatiske emails og dataopsamling

## Arkitektur
- **Streamlit Cloud**: Hosting af web-appen
- **GitHub Repo**: Data lagring (JSON/CSV filer)
- **Unikke tokens**: `?token=xxx` parameter i URL
- **GitHub Actions**: Automatiske emails (den 20. i måneden) og dataopsamling (den 25.)
- **SMTP config**: Kun i Streamlit admin (config.json), bruges af både Streamlit og GitHub Actions

## Oprettede filer
1. `app.py` - Streamlit app med admin interface og medarbejderformularer
2. `employees.csv` - Medarbejdere med tokens og skema-konfiguration
3. `requirements.txt` - Python dependencies
4. `.streamlit/config.toml` - Streamlit konfiguration
5. `.github/workflows/reminders.yml` - GitHub Actions workflows
6. `scripts/send_reminders.py` - Påmindelser til manglende medarbejdere
7. `scripts/aggregate_data.py` - Månedlig dataopsamling
8. `config.json` - SMTP og app indstillinger (oprettes automatisk)
9. `STREAMLIT_SETUP.md` - Opsætningsguide
10. `README.md` - Projektoversigt
11. `AGENTS.md` - Info til fremtidige agent-sessioner

## Medarbejdere (fra ansatte_oversigt.csv)
1. Kasper sangill Elgaard - Fuldt skema (ferie, syg, ekstra timer alle dage)
2. Jonas Strunge Christiansen - Fuldt skema
3. Amalie Winther Hansen - Kun ferie/fridage/sygedage
4. Gitte Simonsen - Kun ferie/fridage/sygedage
5. Gitte Friis - Kun basis (ingen ekstra felter)
6. Vitus - Kun antal timer
7. Benjamin - Kun antal timer
8. Mille Rask Steiner - Kun antal timer

## Arbejdsflow
1. Admin tilføjer medarbejdere via admin interface (`?admin=true`)
2. Hver medarbejder får et unikt link (token-genereret)
3. Medarbejdere udfylder deres månedlige skema og markerer "Udfyldt"
4. Den 20.: Påmindelser sendes til dem der mangler (GitHub Actions)
5. Den 25.: Data samles i summary CSV, admin får email (GitHub Actions)

## Gennemførte ændringer (1. maj 2026)

### 1. Admin interface reorganiseret
- Medarbejdere vises først (tab1: "Medarbejdere", tab2: "Tilføj ny", tab3: "Indsendelser")
- Indstillinger (instruktioner + SMTP) flyttet til bunden af admin-siden

### 2. SMTP indstillinger
- Flyttet til config.json (load_config/save_config funktioner tilføjet)
- Læses af både Streamlit app og GitHub Actions scripts
- "Send test-email" knap tilføjet i admin SMTP sektion
- SMTP port 465 (SSL) understøttet til one.com og lignende
- **Testet og virker med one.com** (send.one.com, port 465)

### 3. "Indberet" checkbox
- Simpel checkbox med rød tekst "Indberet" (st.error)
- Når medarbejder markerer "Marker for at indberette" og trykker "Gem"
- Så gemmes `udfyldt: true` i JSON filen
- Admin > "Indsendelser" viser "✅ Udfyldt" for den medarbejder

### 4. Nyt faneblad "Fælles besked"
- Tilføjet som tab4 i admin interface
- Viser alle aktive medarbejdere med checkbox ud for hver
- Tekstfelt til at skrive en fælles besked
- "Send fælles besked" knap sender email til alle valgte medarbejdere
- Bruger SMTP indstillinger fra config.json

## Status (1. maj 2026 - AFLSUTTET)
- ✅ Koden er opdateret og pushet til GitHub (seneste commit `5af52b6`)
- ✅ SMTP virker med one.com (test-email sendes succesfuldt)
- ✅ Nyt faneblad "Fælles besked" er tilføjet og testet - virker perfekt
- ✅ Medarbejdere kan markere "Indberet" og det vises i admin
- ✅ Admin interface reorganiseret (medarbejdere først, indstillinger til sidst)
- ✅ "Send test-email" knap virker i admin SMTP sektion

## Næste skridt (for bruger)
1. Deploy til Streamlit Cloud (forbind til GitHub repo)
2. Konfigurer secrets i Streamlit Cloud (GITHUB_TOKEN, ADMIN_PASSWORD, APP_URL)
3. Konfigurer GitHub Repository Secrets (SMTP settings)
4. Tilføj medarbejdere via admin interface (`?admin=true`)
5. Send links til medarbejdere

## Session 3. maj 2026
- Bruger spurgte om status på seneste ændringer (læst CONVERSATION_LOG.md)
- Bruger spurgte om tidspunkt for automatiske mails (påmindelser og dataopsamling)
- Oplyst at mails sendes den 20. i måneden kl. 08:00 UTC (09:00 CET / 10:00 CEST)
- Bruger oplyste at have rettet workflow for dataopsamling den 25. som test
- Ingen kodeændringer i denne session

## Session 3. maj 2026 (senere)
- Tilføjet startup instruks til AGENTS.md (auto-læs CONVERSATION_LOG.md)
- Fjernet `get_employee_month()` fra app.py (viste næste måned efter d. 25.)
- Tilføjet dropdown menu til månedsvælgelse i medarbejderformular
- Måned huskes via query parameter `?month=YYYY-MM`
- Beholdt arkivering i `aggregate_data.py` (flytter til `archive/YYYY-MM/`)
- Backup taget: `backup/2026-05-03_18-47-08/` (før push)
- **Backup procedure**: Tag altid backup til `backup/YYYY-MM-DD_HH-MM-SS/` før push

### Ændrede filer
- `app.py` - Dropdown til månedsvælgelse, fjernet auto-måned skift
- `scripts/aggregate_data.py` - Arkivering af submissions efter aggregation
- `AGENTS.md` - Startup instruks til auto-læsning af log
- `CONVERSATION_LOG.md` - Denne log

## Session 4. maj 2026
- Bruger rapporterede at påmindelser ikke blev sendt den 3. maj
- **Fejl fundet**: `.github/workflows/reminders.yml` havde stadig cron sat til den 20. (`0 8 20 * *`)
- **Fejl fundet**: `send_reminders.py` kræver `PyGithub`, men workflow installerede kun `pandas requests`
- **Fejl fundet**: Både `send-reminders` og `aggregate-data` jobs var i samme workflow fil
- **Løsning**: Rettet cron til `0 8 3 * *`, tilføjet `PyGithub` dependency, splittet workflows
- Oprettet ny fil `.github/workflows/aggregate.yml` med cron `0 8 25 * *`
- Push til GitHub: commit `Ret cron til den 3. i måneden + split workflows`
- Backup taget før push

### Ændrede filer
- `.github/workflows/reminders.yml` - Cron rettet, PyGithub tilføjet, fjernet aggregate job
- `.github/workflows/aggregate.yml` - Ny fil til dataopsamling den 25. i måneden

## Session 4. maj 2026 (senere)
- Bruger spurgte om cron er dynamisk (ændres fra interface)
- **Ændring**: Workflows nu sat til at køre hver dag (`0 8 * * *`)
- Scripts tjekker `submission_deadline_day` og `admin_notification_day` fra config.json
- Når du ændrer dato i interfacet, virker det automatisk uden at ændre cron
- Push: commit `Workflows kører dagligt - scripts tjekker dato fra config`

### Ændrede filer
- `.github/workflows/reminders.yml` - Cron ændret til dagligt
- `.github/workflows/aggregate.yml` - Cron ændret til dagligt
- `scripts/send_reminders.py` - Tjekker `submission_deadline_day` fra config
- `scripts/aggregate_data.py` - Tjekker `admin_notification_day` fra config

## Session 4. maj 2026 (Systeminfo)
- Bruger ønskede et nyt faneblad "Systeminfo" med systemoplysninger
- Tilføjet tab5 i admin interface med:
  - Repository info (owner, repo, app URL)
  - Indstillinger (indberetningsdag, notifikationsdag)
  - SMTP info (server, port, brugernavn, password skjult, admin email)
  - Medarbejdere med parametre de skal indsende
  - GitHub Actions info (workflow filer, kørselsinfo)
- Push til GitHub: commit `Tilføjet Systeminfo faneblad med systemoplysninger`

### Ændrede filer
- `app.py` - Tilføjet tab5 "Systeminfo" med relevante systemoplysninger

## Session 4. maj 2026 (Påmindelsesmail rettelser)
- Bruger testede manuel kørsel af workflow (gh workflow run reminders.yml)
- Påmindelsesmail havde flere fejl:
  1. Viste "2026-05" i stedet for "Maj 2026"
  2. Fristen stod fast som "den 25." (skal bruge variabel)
  3. URL manglede (kun "/?token=..." uden domæne)
  4. Afsender var for upersonlig ("Administrationen")
- **Løsning i send_reminders.py**:
  - Månedsnavn nu med `now.strftime("%B %Y")` (f.eks. "Maj 2026")
  - Fristen bruger `deadline_day` variabel fra config
  - URL bruger `app_url` korrekt og fjerner trailing slash
  - Tilføjet 20 sjove afsendernavne (vælges tilfældigt per mail):
    - din digitale påminder
    - the central scrutinizer
    - den store EDB-maskine der styrer alting
    - en ganske automatiseret udsendelsestjeneste
    - bzzzcrrtping...
    - den elektroniske brevdue
    - Robotten fra afdeling 7
    - Den Digitale Timeregnskabs-Politi
    - System 32 (ja, det kører stadig)
    - Den Autonome Påmindelses-Enhed
    - Overlord 3000 - Påmindelsesmodul
    - Den mystiske mail-mand
    - Tidsmaskinen T-800
    - Den travle administrative algoritme
    - Kvorums-gnomen
    - Den digitale klipper
    - Pakke-Post-Peter
    - Sir Sender af Camelot
    - Den flyvende hollandsk rapport
    - Den uundgåelige notifikation
- Push: commit `Rettet påmindelsesmail: månedsnavn, dynamisk frist, komplet URL, sjove afsendere`

### Ændrede filer
- `scripts/send_reminders.py` - Rettet mail-formatering og tilføjet sjove afsendere

## Næste gang
- **Husk at fikse noget med de måneder, der skal registreres** (bruger vil uddybe næste session)

## Session afsluttet 4. maj 2026

## Session 4. maj 2026 (2 måneders skemaer)
- Bruger ønskede implementering af 2 måneders skemaer ad gangen
- Formål: Medarbejderen skal kunne udfylde timer for sidste dage i måneden og overføre til næste måned
- **Flow**:
  - Medarbejder ser indeværende måned + næste måned side om side
  - Når indeværende måned indberettes, overføres data til næste måned
  - Overførselsdata gemmes i `transfer_employee.json` filer
  - Fristdatoer (indberetning og admin-notifikation) bruger variabler fra config
- **Backup taget**: `backup af funktionelt system/` (før ændringer)
- **Nye filer**: `tidsregistrerings-flow.txt` (dokumentation af det nye flow)
- **Ændrede filer**:
  - `app.py` - Implementeret 2 måneders visning, overførselsdata, fjernet gammel månedsvælger
  - `tidsregistrerings-flow.txt` - Ny fil med forklaring på det nye flow
  - `CONVERSATION_LOG.md` - Denne log

### Implementeringsdetaljer
- `get_next_month()` og `get_previous_month()` funktioner tilføjet
- `load_transfer_data()` og `save_transfer_data()` til håndtering af overførsel
- Medarbejderformular viser nu to kolonner (indeværende + næste måned)
- Overført data vises som "🔄 Overført fra [måned]" i næste måneds kolonne
- Indberet-knap kun synlig for indeværende måned
- Datoer for frister hentes dynamisk fra config.json (submission_deadline_day, admin_notification_day)

### Tilbage-rulning
Hvis den nye implementering ikke virker, kan du rulle tilbage ved at kopiere filer fra `backup af funktionelt system/` mappen.

## Session 4. maj 2026 (Dansk månedsformat)
- Ændret visning af måneder til dansk format (f.eks. "Maj 2026" i stedet for "2026-05")
- Tilføjet `format_month_danish()` funktion der konverterer YYYY-MM til dansk
- Opdateret medarbejderformular til at vise "📆 Maj 2026" i overskriften
- Opdateret admin interface (tab3 "Indsendelser") til at bruge dansk månedsformat i dropdown
- **Ændrede filer**:
  - `app.py` - Tilføjet `format_month_danish()`, opdateret visning af måneder

## Session 4. maj 2026 (Sjove afsendere på indberet)
- Tilføjet 20 nye sjove afsendere til "Marker for at indberette" checkboxen (nu 40 i alt)
- Checkboxen viser nu en tilfældig afsender hver gang (f.eks. "Marker for at indberette til den store EDB-maskine")
- Checkbox er nu `value=False` som default (ikke aktiv som standard)
- Rettet alle afsendere til at bruge "til" i stedet for "fra/af"
- **Ændrede filer**:
  - `app.py` - Opdateret indberet checkbox med `random.choice()`, `value=False`, og "til" i alle afsendere
  - `AGENTS.md` - Tilføjet shutdown instruks ved "farvel"
- **Push til GitHub**: 
  - Commit `850e804` - "Dansk månedsformat + sjove afsendere på indberet checkbox"
  - Commit `0fe73ff` - "Ret afsendere til 'til' i stedet for 'fra/af'"

## Session 4. maj 2026 (Rettelse: afsendere til 'til')
- Rettet alle afsendere i indberet checkbox til at bruge "til" i stedet for "fra/af"
- Eksempel: "Marker for at indberette til den store EDB-maskine"
- **Ændrede filer**:
  - `app.py` - 40 afsendere rettet til "til"
  - `AGENTS.md` - Tilføjet shutdown instruks ved "farvel"
- **Push til GitHub**: Commit `0fe73ff` - "Ret afsendere til 'til' i stedet for 'fra/af'"

## Session afsluttet 4. maj 2026 (seneste - fortsæt herfra næste gang)
- Alle ændringer er pushet til GitHub
- Logfilen (CONVERSATION_LOG.md) ligger lokalt i mappen
- Shutdown instruks tilføjet AGENTS.md (gem log + push ved "farvel")

---

## Session 25. juni 2026 — Større redesign og nye funktioner

### Hvad der blev lavet

#### 1. Faste datoer og ny periode-logik
- Fjernet konfigurerbare datoer — datoerne er nu faste konstanter i koden:
  - `REMINDER_DAY = 18` (påmindelsesmail til alle medarbejdere)
  - `DEADLINE_DAY = 20` (indberetningsfrist)
  - `AGGREGATE_DAY = 21` (opsamling til admin + ny periode starter)
- Registreringsperiode følger 21.–20.-modellen via `get_current_period()`
- Medarbejderformular viser nu én periode ad gangen (fjernet gammel to-kolonne layout)

#### 2. Apple-inspireret design
- CSS injiceret via `inject_css()`: Apple-blå knapper (#0071e3), pill-radius, lys grå baggrund (#f5f5f7)
- `config.toml` opdateret med Apple-farver
- Inputfelter med blå fokus-ring, runde tabs og expanders

#### 3. Medarbejderformular
- Infobox øverst med periode, frist, påmindelsesdato og konsekvens ved manglende indberetning
- "Indberet"-sektionen er nu et afsnit (ikke en rød knap)
- Checkbox: "Marker her for at indberette" (fjernet sjov tekst)
- Knap: "Gem" → "Indsend"
- Sammenfoldelig vejledning tilføjet

#### 4. Admin-interface
- Styled infobox øverst med systemoversigt
- Ny "Simuler"-fane: send admin-mail manuelt uanset dato
- Admin-mail er nu én samlet tabel (ikke individuelle mails)
- `scripts/send_reminders.py`: sender til ALLE aktive medarbejdere d. 18 (ikke kun dem der mangler)
- `scripts/aggregate_data.py`: sender én samlet tabel-email til admin d. 21

#### 5. Detaljerede HTML-vejledninger
- Admin: nyt faneblad "Vejledning" med månedlig tidslinje, trin-for-trin guides, felttabel, SMTP-guide
- Medarbejder: sammenfoldelig vejledning med datooversigt og feltforklaringer

#### 6. Keep-alive workflow
- `.github/workflows/keep_alive.yml`: Playwright headless browser pinger appen kl. 07:00 og 19:00 UTC
- Forhindrer Streamlit Cloud i at sætte appen i dvale (7-dages grænse)

#### 7. Rettelser i denne session (25. juni 2026)
- Guide-tekst: "D. 1–17 Løbende registrering" rettet til "D. 21 ↗ Perioden åbner" — reflekterer korrekt at perioden starter d. 21 i forrige måned
- Admin login: bruger nu `st.session_state['admin_ok']` så login ikke mistes ved `st.rerun()`
- Slet-knap: tilføjet `st.spinner("Sletter...")` og fjernet overflødigt success-banner, så knappen ikke hænger visuelt

### Ændrede filer (25. juni 2026)
- `app.py` — alle ovenstående ændringer
- `scripts/send_reminders.py` — faste datoer, sender til alle
- `scripts/aggregate_data.py` — faste datoer, én tabel-email
- `.streamlit/config.toml` — Apple-farver
- `.github/workflows/keep_alive.yml` — ny fil, Playwright ping
- `CLAUDE.md` — ny fil, codebase-dokumentation til fremtidige sessioner

### Status
- ✅ Alt pushet til GitHub (seneste commit se `git log`)
- Systemet er færdigt og i produktion på Streamlit Cloud

---

## Session 25. juni 2026 (fortsættelse) — Performance og UX-rettelser

### Problemer der blev løst

#### 1. Greying out / træg UI
- **Årsag**: `load_employees()` og `load_config()` lavede GitHub API-kald ved **hvert** eneste rerender
- **Løsning**: GitHub-klient, medarbejderliste og config caches nu i `st.session_state`
  - Første sideload henter fra GitHub (langsomt)
  - Alle efterfølgende reruns bruger cache (næsten øjeblikkeligt)
  - Efter `save_employees()` / `save_config()` opdateres cachen direkte — ingen re-fetch nødvendigt
- `get_github_client()` cacher også `Github()`-objektet i session state

#### 2. Slet hænger
- Knap viser `st.spinner("Sletter...")` under GitHub API-kaldet
- Rerun efter sletning er nu hurtig (bruger cache)
- Viser `st.toast()` bekræftelse i hjørnet efter handling

#### 3. Formular ryddes ikke efter "Tilføj ny"
- Løst med dynamisk form-key (`new_employee_0`, `new_employee_1` osv.)
- `st.session_state['_form_id']` tælles op ved succesfuld oprettelse → Streamlit opretter frisk tom formular

#### 4. Bekræftelsesnotifikationer
- Alle muterende handlinger (gem, slet, ny token, tilføj medarbejder, gem SMTP) viser nu `st.toast()` i hjørnet
- Toast-besked sættes i `st.session_state['_toast']` og vises efter rerun

#### 5. Emailvalidering
- `is_valid_email()` med regex `r'^[^@\s]+@[^@\s]+\.[^@\s]+$'`
- Valideres i "Tilføj ny"-formularen og ved gem af eksisterende medarbejder
- Fejlbesked: "Ugyldig emailadresse — tjek formatet (fx navn@firma.dk)"

#### 6. Slettebekræftelse
- "Slet"-knap viser nu en advarsel med spørgsmål og **Ja** / **Nej** knapper
- To-trins flow via `st.session_state['_confirm_delete']`
- Knaplabels rettet fra "Ja, slet"/"Annuller" til "Ja"/"Nej" på brugerens ønske

### Ændrede filer
- `app.py` — alle ovenstående ændringer

### Commits
- `752a485` — Ret træg UI: cache data i session state, toast-bekræftelser, ryd formular
- `56c646b` — Emailvalidering og slettebekræftelse
- `53783a4` — Ret slettebekræftelse: 'Ja'/'Nej' i stedet for 'Ja, slet'/'Annuller'

---

## Session 25. juni 2026 (del 2) — PDF-vejledninger, UX-forbedringer, mailfix

### Hvad der blev lavet

#### 1. To PDF-vejledninger genereret
- `Timeregnskab_Administratorvejledning.pdf` — Apple-design, tidslinje, tab-gennemgang, SMTP-guide, FAQ
- `Timeregnskab_Medarbejdervejledning.pdf` — trin-for-trin, feltforklaringer, FAQ
- `generate_guides.py` — script til at genskabe PDF'erne (kør med `python3 generate_guides.py`)
- Bruger `reportlab` (allerede installeret)

#### 2. Medarbejderside: navneboks
- Medarbejderens navn vises nu i en blå gradient-ramme øverst ("Logget ind som X")

#### 3. Admin Indsendelser: Opdater-knap
- `🔄 Opdater`-knap henter seneste status fra GitHub uden at refreshe hele siden

#### 4. Emailvalidering + slettebekræftelse (fra del 1, nu komplet)
- `is_valid_email()` med regex — valideres ved tilføj og gem
- Slet-knap: Ja/Nej bekræftelsesdialog via session state

#### 5. App URL i config
- Nyt felt "App URL" under SMTP-indstillinger — gemmes i `config.json`
- `send_reminders.py` og `aggregate_data.py` læser URL herfra (ikke env var)
- Løser problemet med `/?token=...` uden domæne i påmindelsesmails

#### 6. SMTP password-bug rettet
- Passwordfeltet vises intentionelt tomt (browser-sikkerhed)
- Ved gem bevares eksisterende password hvis feltet er tomt (`if smtp_password:`)
- Advarsel vises øverst i SMTP-sektionen hvis password ikke er gemt
- Test-email bruger gemt password som fallback hvis feltet er tomt
- **Rodårsag til mailstop:** Da admin-email blev ændret fra timereg@vimby.dk til digitalt@vimby.dk, blev det tomme passwordfelt gemt og overskrev det rigtige password

#### 7. SMTP EHLO-fix
- `ehlo()` tilføjet før og efter `starttls()` — fikser `501 AUTH mechanism`-fejl på mange SMTP-servere
- `server.quit()` pakket i try/except

#### 8. HTML-formateret opsamlingsmail
- Ny `build_summary_html()` funktion: gradient-header, statistikbokse (grøn/rød), pæn tabel
- Grønt ✔ ved indberettede, rødt ✘ ved manglende
- Sendes som multipart/alternative (HTML + plain-text fallback)
- Opdateret i både `app.py` (Simuler) og `scripts/aggregate_data.py`

#### 9. Spam-advarsel + token-advarsel i alle guides
- Spam-advarsel: HTML-guides (admin + medarbejder) og begge PDF'er
- Token-advarsel: admin HTML-guide og admin PDF — "Ny token invaliderer medarbejderens link, husk at sende det nye"

#### 10. Simuler-fane forbedret
- Force-reload af config fra GitHub ved hvert klik (bypass session state cache)
- Præcis fejlbesked ved manglende SMTP-felter
- Success/error vises nu uden for `st.spinner()` — var usynlig før

### Udestående / næste gang
- **Performance:** Systemet er 10–15 sek. langsomt pga. GitHub-API-arkitektur. Løsning er migration til Supabase (PostgreSQL). Bruger har valgt at vente med dette.
- Supabase-plan: beholde Streamlit Cloud, erstatte GitHub-filstorage med Supabase-tabeller (employees, submissions, config). Alle API-kald: 20–100 ms i stedet for 1–3 sek.
- Husk: App URL skal sættes i admin → SMTP-indstillinger for at påmindelsesmails får komplet link

---

## Session 10. juli 2026 — Gennemgang af vejledninger

### Gennemført
- Gennemgået begge HTML-vejledninger (admin + medarbejder) linje for linje mod aktuel app.py-kode
- **Fundet én fejl:** Admin-vejledningens SMTP-tabel manglede "App URL"-feltet (bruges i påmindelsesmails)
- **Rettet:** Tilføjet App URL-række til SMTP-tabellen i `get_admin_guide_html()`
- Medarbejdervejledningen var fuldt opdateret — ingen ændringer nødvendige
- **Commit:** `63cbdf6` — "Admin guide: Tilføjet App URL til SMTP-tabellen"

### Tjekket og verificeret som korrekt
- Alle 7 admin-faner stemmer overens med vejledningen
- "Inaktiv" beskrivelse (ingen påmindelser, ikke med i opsamling) matcher koden
- "Automatisk arkiv" tip matcher `aggregate_data.py`
- Indsendelser-dropdown viser 3 perioder (nuværende + 2 forrige)
- Periode-modellen (21.–20.) er konsistent i begge guides
- SMTP-felter, Simuler, Fælles besked korrekt beskrevet
