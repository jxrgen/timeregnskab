# Timeregnskab - Streamlit App

Automatiseret timeregnskab med separat adgang til hver medarbejder via unikke links. Data gemmes i GitHub repo.

## Arkitektur

- **Streamlit Cloud**: Hosting af web-appen (forbundet til GitHub repo)
- **GitHub Repo**: Data lagring (medarbejdere, indsendelser, summaries)
- **Unikke tokens**: Hver medarbejder får et unikt link (`?token=xxx`) - intet login nødvendigt
- **GitHub Actions**: Automatiske påmindelser (den 20.) og dataopsamling (den 25.)

## Features

- Admin interface til at administrere medarbejdere (tilføj, fjern, rediger skemaer)
- Medarbejdere udfylder deres skema via personligt link
- Forskellige skematyper (feriedage, sygedage, ekstra timer mv.)
- Automatiske email-påmindelser til medarbejdere der mangler at udfylde
- Månedlig opsummering sendes til admin
- Data gemmes som JSON filer i GitHub repo (versionshistorik bevares)

## Opsætning

Se `STREAMLIT_SETUP.md` for detaljeret guide.

## Filer

- `app.py` - Streamlit app (admin + medarbejder formularer)
- `employees.csv` - Medarbejdere med tokens
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit konfiguration
- `.github/workflows/reminders.yml` - GitHub Actions (emails + aggregation)
- `scripts/send_reminders.py` - Påmindelser
- `scripts/aggregate_data.py` - Dataopsamling

## Migration fra Google Sheets

Denne løsning erstatter Google Sheets løsningen (Code.gs/Config.gs) fordi:
- Ingen Google Sheets API administration
- Lettere at vedligeholde (ren Python kode)
- Data versionsstyring via GitHub
- Gratis hosting via Streamlit Cloud
