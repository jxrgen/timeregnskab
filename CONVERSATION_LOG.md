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
