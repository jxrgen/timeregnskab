# STREAMLIT_SETUP.md

## Trin 1: Opret GitHub Repository

1. Gå til [github.com](https://github.com) og log ind
2. Klik **New repository**
3. Navn: `timeregnskab` (eller dit valg)
4. Vælg **Public** eller **Private**
5. Klik **Create repository**

## Trin 2: Push koden til GitHub

Kør disse kommandoer i terminalen (i `/home/jxrgen/opencode/timeregnskab`):

```bash
git init
git add .
git commit -m "Initial commit - Streamlit timeregnskab"
git remote add origin https://github.com/DIT-BRUGERNAVN/timeregnskab.git
git push -u origin main
```

*Hvis du har en personlig access token:*
```bash
git remote add origin https://DIT-TOKEN@github.com/DIT-BRUGERNAVN/timeregnskab.git
```

## Trin 3: Deploy til Streamlit Cloud

1. Gå til [share.streamlit.io](https://share.streamlit.io)
2. Log ind med din GitHub konto
3. Klik **New app**
4. Vælg dit repo: `timeregnskab`
5. Branch: `main`
6. Main file path: `app.py`
7. Klik **Deploy**

Appen er nu live på: `https://DIT-APP.streamlit.app`

## Trin 4: Konfigurer Secrets i Streamlit Cloud

I Streamlit Cloud dashboard:
1. Klik på din app → **Settings** → **Secrets**
2. Tilføj følgende (erstat værdierne):

```toml
GITHUB_TOKEN = "ghp_dit-github-token-her"
REPO_OWNER = "dit-brugernavn"
REPO_NAME = "timeregnskab"
ADMIN_PASSWORD = "dit-admin-adgangskode"
APP_URL = "https://dit-app.streamlit.app"

[SMTP]
SERVER = "smtp.gmail.com"
PORT = "587"
USERNAME = "din-email@gmail.com"
PASSWORD = "dit-app-password"
```

## Trin 5: Konfigurer Secrets i GitHub (til GitHub Actions)

I dit GitHub repo:
1. **Settings** → **Secrets and variables** → **Actions**
2. Tilføj disse secrets:

| Secret | Beskrivelse |
|--------|-------------|
| `SMTP_SERVER` | SMTP server (f.eks. smtp.gmail.com) |
| `SMTP_PORT` | Port (587 for TLS) |
| `SMTP_USERNAME` | Din email adresse |
| `SMTP_PASSWORD` | App password eller email password |
| `ADMIN_EMAIL` | Admin email til påmindelser |
| `APP_URL` | URL til din Streamlit app |

## Trin 6: Tilføj medarbejdere

1. Gå til din Streamlit app + `?admin=true`
2. Indtast admin adgangskode
3. Klik "Tilføj ny medarbejder"
4. Udfyld navn, email og vælg skematype
5. Klik "Tilføj medarbejder"
6. Kopiér det genererede link og send til medarbejderen

## Trin 7: Test

1. Log ind som admin: `?admin=true`
2. Udfyld et test-skema som medarbejder: Brug linket med token
3. Check at data gemmes i `submissions/` mappen i repoet

## Sådan virker det

1. **Medarbejdere** modtager deres unikke link via email
2. **Hver måned** udfylder de deres skema og markerer "Udfyldt"
3. **Den 20.** får manglende medarbejdere en påmindelse (GitHub Actions)
4. **Den 25.** samles alle data i en summary CSV i repoet, admin får email
5. **Admin** kan til enhver tid tilføje/fjerne medarbejdere og ændre deres skemaer

## Email opsætning

For at sende emails skal du bruge:
- **Gmail**: Aktivér "Less secure apps" eller brug App Password (anbefales)
- **Outlook**: Brug dit normale password eller app password
- **Anden SMTP**: Indtast server og port i secrets

### Gmail App Password:
1. Gå til Google Account → Security
2. Aktivér 2-Step Verification
3. Search "App passwords" → Generate ny til "Mail"
4. Brug det genererede password i SMTP_PASSWORD
