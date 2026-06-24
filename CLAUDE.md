# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Session protocol

At session start, read `CONVERSATION_LOG.md` to catch up on recent work. When the user says "farvel" (goodbye), update `CONVERSATION_LOG.md` with the session's changes and confirm it's saved.

## Running the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

Requires a `.streamlit/secrets.toml` file (use `secrets_clean.toml` as template) with `GITHUB_TOKEN`, `REPO_OWNER`, `REPO_NAME`, `ADMIN_PASSWORD`, and `APP_URL`.

To manually test the GitHub Actions scripts (requires env vars):
```bash
GITHUB_TOKEN=... REPO_OWNER=jxrgen REPO_NAME=timeregnskab APP_URL=... python scripts/send_reminders.py
python scripts/aggregate_data.py
```

## Architecture

**GitHub as database.** There is no traditional database. All persistent state lives as files in this GitHub repo, accessed via the PyGithub API from both the Streamlit app and the GitHub Actions scripts.

**Two URL-based views in `app.py`:**
- `?token=<token>` — employee form (token matched against `employees.csv`)
- `?admin=true` — admin interface (password from Streamlit secrets)
- No params — landing page with instructions

**Employee schema is per-row in `employees.csv`.** Boolean columns (`Feriedage`, `Feriefridag`, `Sygedage`, `Ekstra_Hverdag`, `Ekstra_Lørdag`, `Ekstra_Søndag`, `Ekstra_Andet`, `Antal_timer`) control which form fields each employee sees. Adding a new field type requires updating this CSV schema, the employee form in `app.py`, and the aggregation script.

**Data flow:**
1. Employees submit → `submissions/YYYY-MM/EmployeeName.json`
2. Optionally, transfer data to next month → `submissions/YYYY-MM/transfer_EmployeeName.json`
3. On `admin_notification_day`: `aggregate_data.py` collects all submissions → `summary/YYYY-MM.csv`, then archives raw submissions to `archive/YYYY-MM/` and deletes from `submissions/`

**GitHub Actions** (`reminders.yml`, `aggregate.yml`) both run daily at 08:00 UTC. Each script checks `config.json` to see if today matches the configured day (`submission_deadline_day` for reminders, `admin_notification_day` for aggregation) and exits early if not.

## Configuration

`config.json` (stored in the repo) holds operational config: deadline days, and SMTP credentials. This file is committed — SMTP credentials live here, not in Streamlit secrets. Changes via the admin UI write back to GitHub.

Streamlit secrets (`.streamlit/secrets.toml` locally, Streamlit Cloud dashboard in prod) hold: `GITHUB_TOKEN`, `ADMIN_PASSWORD`, `APP_URL`.

GitHub Actions secrets needed: `APP_URL` (workflow files use `secrets.GITHUB_TOKEN` automatically).

## Key constraints

- Every read/write to employees, submissions, and config goes through GitHub API — no local filesystem caching. This means every page load makes GitHub API calls.
- Token generation uses `secrets.token_urlsafe(16)` — regenerating a token immediately invalidates the employee's existing link.
- Month format throughout is `YYYY-MM` (e.g. `2026-05`). Danish display names are formatted via `format_month_danish()` in `app.py`.
- The employee form shows current month and next month side by side. "Indberet" (submit) checkbox only appears for the current month.
