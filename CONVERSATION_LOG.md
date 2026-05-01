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

### 3. "Indberet" checkbox forbedringer
- Rød ramme omkring checkbox (div med border: 2px solid red)
- Popup "Vil du indberette nu?" når checkbox markeres
- Ja/Nej knapper til at bekræfte eller annullere

### 4. Session state håndtering
- `indberet_state`: 'idle', 'confirming', 'confirmed'
- `indberet_cb`: checkbox værdi
- `indberet_confirmed`: om indberetning er bekræftet

## Status
- Koden er opdateret og klar
- SMTP function names verificeret korrekte (MIMEText, MIMEMultipart, smtplib.SMTP, server.quit())
- Mangler: Commit og push til GitHub
- Herefter: Deploy til Streamlit Cloud og konfigurer secrets

## TODO før deployment
1. Push kode til GitHub repo
2. Deploy til Streamlit Cloud (forbind til GitHub repo)
3. Konfigurer secrets i Streamlit Cloud (GITHUB_TOKEN, ADMIN_PASSWORD, APP_URL)
4. Konfigurer GitHub Repository Secrets (SMTP settings bruges kun af GitHub Actions)
5. Tilføj medarbejdere via admin interface
6. Send links til medarbejdere
