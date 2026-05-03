# AGENTS.md

Streamlit Cloud app for automated time tracking with individual employee access via unique tokens.

## Structure
- `app.py` - Main Streamlit app: admin interface + employee forms
- `employees.csv` - Employee list with tokens and schema configuration
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `.github/workflows/reminders.yml` - GitHub Actions for emails and aggregation
- `scripts/send_reminders.py` - Monthly reminders (runs 20th)
- `scripts/aggregate_data.py` - Data aggregation (runs 25th)

## Before editing
- This is a Python/Streamlit project (NOT Apps Script/Node.js)
- Code runs on Streamlit Cloud, connected to GitHub repository
- Data stored as JSON/CSV files in GitHub repo (not a database)
- User provides GitHub token for repo access

## Key behavior
- Each employee gets a UNIQUE URL with token parameter (`?token=xxx`)
- No login required - token-based access
- Admin interface at `?admin=true` (password protected)
- Different form schemas per employee (configured in employees.csv)
- Monthly submissions stored in `submissions/YYYY-MM/employee.json`
- GitHub Actions handle automated emails and data aggregation

## Email configuration
- SMTP configured via Streamlit secrets or GitHub Actions secrets
- Uses smtplib (Python standard library)
- Works with Gmail, Outlook, or any SMTP server

## Admin capabilities
- Add/remove employees
- Modify employee schemas (which fields they see)
- Generate new tokens (invalidates old links)
- View all submissions across months
- All changes saved to GitHub repo

## Setup order
1. Create GitHub repo and push code
2. Deploy to Streamlit Cloud (connect to GitHub repo)
3. Configure secrets (GitHub token, SMTP, admin password)
4. Configure GitHub Actions secrets (SMTP, admin email)
5. Add employees via admin interface
6. Send links to employees

## Data storage
- `employees.csv` - Employee list
- `submissions/YYYY-MM/` - JSON files per employee per month
- `summary/YYYY-MM.csv` - Aggregated data per month

## Startup instruction
Always read `CONVERSATION_LOG.md` at the start of each session to understand recent work and continue from where we left off.
