# Samtale Log - Timeregnskab Projekt

Dato: 30. april 2026

## Brugerens ønske
- Automatiseret timeregnskab til 3-8 medarbejdere
- Medarbejdere skal selv kunne indtaste deres timer via webformular
- Registrering af: Ferie/fridage, sygedage og feriedage + ekstra timer (varierer per medarbejder)
- Påmindelser til dem der mangler at udfylde (før bestemt dato)
- Automatisk opsamling af data til administrator
- **Vigtigt:** Medarbejdere må ikke kunne se hinandens data - separate links/tokens

## Valg af teknologi - ÆNDRET

### Oprindelig løsning (Google Sheets + Apps Script)
- Valgt først: Google Sheets + Apps Script
- Begrundelse: Ingen hosting-omkostninger, indbygget automation
- Fravalgt: For meget administration med separate sheets og Drive sharing

### Ny løsning (Streamlit Cloud + GitHub)
- Valgt: Streamlit Cloud app med GitHub repo som datalager
- Begrundelse:
  - Nemmere administration (admin interface i appen)
  - Ingen Google Sheets API kompleksitet
  - Data versionsstyring via GitHub
  - Gratis hosting på Streamlit Cloud
  - Let at tilføje/fjerne medarbejdere via admin interface
  - Unikke links (tokens) i stedet for login

## Arkitektur
- **Streamlit Cloud**: Hosting af web-appen
- **GitHub Repo**: Data lagring (JSON/CSV filer)
- **Unikke tokens**: `?token=xxx` parameter i URL
- **GitHub Actions**: Automatiske emails (den 20. i måneden) og dataopsamling (den 25.)

## Oprettede filer
1. `app.py` - Streamlit app med admin interface og medarbejderformularer
2. `employees.csv` - Medarbejdere med tokens og skema-konfiguration
3. `requirements.txt` - Python dependencies
4. `.streamlit/config.toml` - Streamlit konfiguration
5. `.github/workflows/reminders.yml` - GitHub Actions workflows
6. `scripts/send_reminders.py` - Påmindelser til manglende medarbejdere
7. `scripts/aggregate_data.py` - Månedlig dataopsamling
8. `STREAMLIT_SETUP.md` - Komplet opsætningsguide
9. `README.md` - Projektoversigt (opdateret)
10. `AGENTS.md` - Info til fremtidige agent-sessioner (opdateret)

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

## Status
- Koden er klar og skal pushes til GitHub
- Brugeren skal:
  1. Oprette GitHub repo
  2. Give agent adgang (Personal Access Token)
  3. Push kode til repo
  4. Deploy til Streamlit Cloud
  5. Konfigurere secrets (SMTP, GitHub token, admin password)
  6. Tilføje medarbejdere via admin interface
