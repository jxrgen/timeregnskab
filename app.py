import streamlit as st
import pandas as pd
import os
from github import Github
import json
from datetime import datetime
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

st.set_page_config(page_title="Timeregnskab", page_icon="📊", layout="wide")

REPO_OWNER = os.getenv("REPO_OWNER", "jxrgen")
REPO_NAME = os.getenv("REPO_NAME", "timeregnskab")
EMPLOYEES_FILE = "employees.csv"
SUBMISSIONS_DIR = "submissions"

REMINDER_DAY = 18
DEADLINE_DAY = 20
AGGREGATE_DAY = 21

MONTHS_DA = {
    1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April',
    5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August',
    9: 'September', 10: 'Oktober', 11: 'November', 12: 'December'
}

SENDERS = [
    "til den store EDB-maskine",
    "til din digitale påminder",
    "til the central scrutinizer",
    "til den elektroniske brevdue",
    "til Robotten fra afdeling 7",
    "til Den Digitale Timeregnskabs-Politi",
    "til System 32 (ja, det kører stadig)",
    "til Den Autonome Påmindelses-Enhed",
    "til Overlord 3000 – Påmindelsesmodul",
    "til Den mystiske mail-mand",
    "til Tidsmaskinen T-800",
    "til Den travle administrative algoritme",
    "til Kvorums-gnomen",
    "til Den digitale klipper",
    "til Pakke-Post-Peter",
    "til Sir Sender af Camelot",
    "til Den flyvende hollandsk rapport",
    "til Den uundgåelige notifikation",
    "til en ganske automatiseret udsendelsestjeneste",
    "til bzzzcrrtping...",
    "til Den digitale vandmand",
    "til Systemfejl 404 – ikke fundet",
    "til Den elektroniske husassistent",
    "til Kodelinje-Karl",
    "til Algoritme-Aage",
    "til Den automatiske tidsoptæller",
    "til Cyber-Kaj",
    "til Den logiske labyrint",
    "til Datamat-Dennis",
    "til Den virtuelle vicevært",
    "til Terminal-Torben",
    "til Den programmerbare påminder",
    "til Database-Bjarne",
    "til Den digitale dueslag",
    "til Netværks-Niels",
    "til Den elektroniske edb-rotte",
    "til Mega-Computeren 2.0",
    "til Den automatiske arkiver",
    "til Server-Søren",
    "til Den digitale driller",
]

def get_github_client():
    token = None
    try:
        token = st.secrets["GITHUB_TOKEN"]
    except:
        token = os.getenv("GITHUB_TOKEN")
    if not token:
        st.error("GitHub token ikke konfigureret")
        return None
    return Github(token)

def load_employees():
    try:
        g = get_github_client()
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            content = repo.get_contents(EMPLOYEES_FILE)
            import base64
            csv_content = base64.b64decode(content.content).decode('utf-8')
            from io import StringIO
            df = pd.read_csv(StringIO(csv_content))
            return df
        else:
            st.error("Ingen GitHub forbindelse")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Kunne ikke indlæse medarbejdere: {str(e)}")
        return pd.DataFrame()

def save_employees(df):
    try:
        g = get_github_client()
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            content = df.to_csv(index=False)
            try:
                file = repo.get_contents(EMPLOYEES_FILE)
                repo.update_file(EMPLOYEES_FILE, "Opdateret medarbejdere", content, file.sha)
            except:
                repo.create_file(EMPLOYEES_FILE, "Oprettet medarbejdere", content)
            return True
        return False
    except Exception as e:
        st.error(f"Kunne ikke gemme medarbejdere: {str(e)}")
        return False

def load_submission(employee_name, month):
    try:
        g = get_github_client()
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            file_path = f"{SUBMISSIONS_DIR}/{month}/{employee_name}.json"
            content = repo.get_contents(file_path)
            import base64
            return json.loads(base64.b64decode(content.content).decode('utf-8'))
    except:
        pass
    return None

def save_submission(employee_name, data, month):
    try:
        g = get_github_client()
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            file_path = f"{SUBMISSIONS_DIR}/{month}/{employee_name}.json"
            content = json.dumps(data, ensure_ascii=False, indent=2)
            try:
                file = repo.get_contents(file_path)
                repo.update_file(file_path, f"Opdateret {month}/{employee_name}", content, file.sha)
            except:
                repo.create_file(file_path, f"Oprettet {month}/{employee_name}", content)
            return True
    except Exception as e:
        st.error(f"Kunne ikke gemme submission: {str(e)}")
        return False
    return False

def generate_token():
    return secrets.token_urlsafe(16)

def load_config():
    try:
        g = get_github_client()
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            content = repo.get_contents("config.json")
            import base64
            return json.loads(base64.b64decode(content.content).decode('utf-8'))
    except:
        pass
    return {}

def save_config(config):
    try:
        g = get_github_client()
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            content = json.dumps(config, ensure_ascii=False, indent=2)
            try:
                file = repo.get_contents("config.json")
                repo.update_file("config.json", "Opdateret konfiguration", content, file.sha)
            except:
                repo.create_file("config.json", "Oprettet konfiguration", content)
            return True
    except Exception as e:
        st.error(f"Kunne ikke gemme konfiguration: {str(e)}")
    return False

def get_next_month(month_str):
    year, month = map(int, month_str.split('-'))
    if month == 12:
        return f"{year + 1}-01"
    return f"{year}-{month + 1:02d}"

def get_previous_month(month_str):
    year, month = map(int, month_str.split('-'))
    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{month - 1:02d}"

def format_month_danish(month_str):
    year, month = map(int, month_str.split('-'))
    return f"{MONTHS_DA[month]} {year}"

def get_current_period():
    """Returnerer (period_key, period_label).
    Perioden løber fra d. 21 i måned A til d. 20 i måned B.
    Fra og med d. 21 gælder den nye periode (starter i denne måned, slutter næste måned).
    Period_key er slutmåneden (B), brugt som mappenavn i submissions/.
    """
    today = datetime.now()
    current_month = f"{today.year}-{today.month:02d}"
    if today.day >= AGGREGATE_DAY:
        start_month = current_month
        end_month = get_next_month(current_month)
    else:
        start_month = get_previous_month(current_month)
        end_month = current_month
    label = f"21. {format_month_danish(start_month)} – 20. {format_month_danish(end_month)}"
    return end_month, label

def send_email_smtp(to_email, subject, body, config):
    smtp_server = config.get('smtp_server', '')
    smtp_port = int(config.get('smtp_port', 587))
    smtp_username = config.get('smtp_username', '')
    smtp_password = config.get('smtp_password', '')

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    if smtp_port == 465:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    else:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
    server.login(smtp_username, smtp_password)
    server.send_message(msg)
    server.quit()

def collect_period_data(df, period_key):
    """Samler alle aktive medarbejderes indberetninger for en periode."""
    rows = []
    for _, emp in df.iterrows():
        if not emp['Active']:
            continue
        submission = load_submission(emp['Name'], period_key)
        submitted = submission.get('udfyldt', False) if submission else False
        row = {
            'Medarbejder': emp['Name'],
            'Indberettet': 'Ja' if submitted else 'Nej',
            'Feriedage': submission.get('feriedage', 0) if submission else '-',
            'Feriefridage': submission.get('feriefridag', 0) if submission else '-',
            'Sygedage': submission.get('sygedage', 0) if submission else '-',
            'Ekstra hverdag': submission.get('ekstra_hverdag', 0) if submission else '-',
            'Ekstra lørdag': submission.get('ekstra_lørdag', 0) if submission else '-',
            'Ekstra søndag': submission.get('ekstra_søndag', 0) if submission else '-',
            'Ekstra andet': submission.get('ekstra_andet', 0) if submission else '-',
            'Antal timer': submission.get('antal_timer', 0) if submission else '-',
        }
        rows.append(row)
    return pd.DataFrame(rows)

def admin_interface():
    st.title("⚙️ Admin Interface")
    admin_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
    password = st.text_input("Adgangskode", type="password")
    if password != admin_password:
        if password:
            st.error("Forkert adgangskode")
        return

    st.success("Velkommen til admin interface")

    st.info(
        f"**Registreringsperiode:** Fra d. 21 til d. 20 i den følgende måned.  \n"
        f"**Påmindelser:** Sendes automatisk d. {REMINDER_DAY}. til alle aktive medarbejdere.  \n"
        f"**Frist:** Medarbejdere skal indberette senest d. {DEADLINE_DAY}. — timer der ikke er indberettet inden fristen registreres ikke og medtages først i næste måneds opgørelse.  \n"
        f"**Opsamling:** D. {AGGREGATE_DAY}. modtager du en samlet oversigt over alle medarbejderes indberetninger (indberettet og ikke indberettet)."
    )

    df = load_employees()
    if df.empty:
        st.warning("Kunne ikke indlæse medarbejdere")
        return

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Medarbejdere", "Tilføj ny", "Indsendelser", "Fælles besked", "Systeminfo", "Simuler"]
    )

    with tab1:
        st.subheader("Eksisterende medarbejdere")
        for idx, row in df.iterrows():
            with st.expander(f"{row['Name']} ({row['Email']})"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Navn", value=row['Name'], key=f"name_{idx}")
                    new_email = st.text_input("Email", value=row['Email'], key=f"email_{idx}")
                    new_active = st.checkbox("Aktiv", value=row['Active'], key=f"active_{idx}")
                with col2:
                    st.write("**Skema type:**")
                    feriedage = st.checkbox("Feriedage", value=row['Feriedage'], key=f"feriedage_{idx}")
                    feriefridag = st.checkbox("Feriefridag", value=row['Feriefridag'], key=f"feriefridag_{idx}")
                    sygedage = st.checkbox("Sygedage", value=row['Sygedage'], key=f"sygedage_{idx}")
                    ekstra_hverdag = st.checkbox("Ekstra Hverdag", value=row['Ekstra_Hverdag'], key=f"hverdag_{idx}")
                    ekstra_lørdag = st.checkbox("Ekstra Lørdag", value=row['Ekstra_Lørdag'], key=f"lørdag_{idx}")
                    ekstra_søndag = st.checkbox("Ekstra Søndag", value=row['Ekstra_Søndag'], key=f"søndag_{idx}")
                    ekstra_andet = st.checkbox("Ekstra Andet", value=row['Ekstra_Andet'], key=f"andet_{idx}")
                    antal_timer = st.checkbox("Antal timer", value=row['Antal_timer'], key=f"timer_{idx}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Gem ændringer", key=f"save_{idx}"):
                        df.at[idx, 'Name'] = new_name
                        df.at[idx, 'Email'] = new_email
                        df.at[idx, 'Active'] = new_active
                        df.at[idx, 'Feriedage'] = feriedage
                        df.at[idx, 'Feriefridag'] = feriefridag
                        df.at[idx, 'Sygedage'] = sygedage
                        df.at[idx, 'Ekstra_Hverdag'] = ekstra_hverdag
                        df.at[idx, 'Ekstra_Lørdag'] = ekstra_lørdag
                        df.at[idx, 'Ekstra_Søndag'] = ekstra_søndag
                        df.at[idx, 'Ekstra_Andet'] = ekstra_andet
                        df.at[idx, 'Antal_timer'] = antal_timer
                        if save_employees(df):
                            st.success("Gemt!")
                            st.rerun()
                with col2:
                    if st.button("Ny token", key=f"token_{idx}"):
                        df.at[idx, 'Token'] = generate_token()
                        if save_employees(df):
                            st.success("Ny token genereret")
                            st.rerun()
                with col3:
                    if st.button("Slet", key=f"delete_{idx}"):
                        df = df.drop(idx).reset_index(drop=True)
                        if save_employees(df):
                            st.success("Slettet!")
                            st.rerun()

                token = row['Token']
                app_url = st.secrets.get("APP_URL", "https://your-app.streamlit.app")
                link = f"{app_url}/?token={token}"
                st.code(link)

    with tab2:
        st.subheader("Tilføj ny medarbejder")
        with st.form("new_employee"):
            name = st.text_input("Navn")
            email = st.text_input("Email")
            st.write("**Skema type:**")
            col1, col2 = st.columns(2)
            with col1:
                feriedage = st.checkbox("Feriedage", value=True)
                feriefridag = st.checkbox("Feriefridag", value=True)
                sygedage = st.checkbox("Sygedage", value=True)
            with col2:
                ekstra_hverdag = st.checkbox("Ekstra Hverdag")
                ekstra_lørdag = st.checkbox("Ekstra Lørdag")
                ekstra_søndag = st.checkbox("Ekstra Søndag")
                ekstra_andet = st.checkbox("Ekstra Andet")
                antal_timer = st.checkbox("Antal timer")

            submitted = st.form_submit_button("Tilføj medarbejder")
            if submitted and name and email:
                new_row = pd.DataFrame([{
                    'Name': name,
                    'Email': email,
                    'Active': True,
                    'Feriedage': feriedage,
                    'Feriefridag': feriefridag,
                    'Sygedage': sygedage,
                    'Ekstra_Hverdag': ekstra_hverdag,
                    'Ekstra_Lørdag': ekstra_lørdag,
                    'Ekstra_Søndag': ekstra_søndag,
                    'Ekstra_Andet': ekstra_andet,
                    'Antal_timer': antal_timer,
                    'Token': generate_token()
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                if save_employees(df):
                    st.success(f"Tilføjet {name}!")
                    st.rerun()

    with tab3:
        st.subheader("Indsendelser")
        period_key, period_label = get_current_period()
        prev_key = get_previous_month(period_key)
        prev_prev_key = get_previous_month(prev_key)
        months_options = [period_key, prev_key, prev_prev_key]
        month_labels = [
            f"{format_month_danish(m)} (periode slut)" for m in months_options
        ]
        selected_idx = st.selectbox(
            "Vælg periode",
            range(len(month_labels)),
            format_func=lambda i: month_labels[i]
        )
        month = months_options[selected_idx]
        for _, row in df.iterrows():
            if row['Active']:
                submission = load_submission(row['Name'], month)
                status = "✅ Udfyldt" if submission and submission.get('udfyldt') else "❌ Mangler"
                st.write(f"{row['Name']}: {status}")

    with tab4:
        st.subheader("Fælles besked")
        st.write("Vælg medarbejdere og skriv en besked der skal sendes til dem alle.")

        st.write("**Vælg modtagere:**")
        selected = []
        for idx, row in df.iterrows():
            if row['Active']:
                if st.checkbox(f"{row['Name']} ({row['Email']})", key=f"select_{idx}"):
                    selected.append(row)

        st.write("**Skriv besked:**")
        message = st.text_area("Besked", height=150, key="common_message")

        if st.button("Send fælles besked", key="send_common"):
            if not message:
                st.error("Du skal skrive en besked!")
            elif not selected:
                st.error("Du skal vælge mindst en medarbejder!")
            else:
                config = load_config()
                if not all([config.get('smtp_server'), config.get('smtp_username'), config.get('smtp_password')]):
                    st.error("SMTP-indstillinger mangler!")
                else:
                    sent_count = 0
                    error_count = 0
                    for emp in selected:
                        try:
                            body = f"Hej {emp['Name']},\n\n{message}\n\nVenlig hilsen,\nAdministrationen"
                            send_email_smtp(emp['Email'], "Besked fra Timeregnskab", body, config)
                            sent_count += 1
                        except Exception as e:
                            st.error(f"Kunne ikke sende til {emp['Name']}: {str(e)}")
                            error_count += 1
                    if sent_count > 0:
                        st.success(f"✅ Besked sendt til {sent_count} medarbejder(e)!")
                    if error_count > 0:
                        st.warning(f"Kunne ikke sende til {error_count} medarbejder(e)")

    with tab5:
        st.subheader("Systeminfo")
        config = load_config()

        st.markdown("### Repository")
        st.write(f"**Owner:** {REPO_OWNER}")
        st.write(f"**Repository:** {REPO_NAME}")
        app_url = st.secrets.get("APP_URL", "Ikke konfigureret")
        st.write(f"**App URL:** {app_url}")

        st.markdown("### Faste datoer")
        st.write(f"**Påmindelsesdag:** Den {REMINDER_DAY}. i måneden (alle aktive medarbejdere)")
        st.write(f"**Indberetningsfrist:** Den {DEADLINE_DAY}. i måneden")
        st.write(f"**Dataopsamling til admin:** Den {AGGREGATE_DAY}. i måneden")
        period_key, period_label = get_current_period()
        st.write(f"**Aktuel periode:** {period_label}")

        st.markdown("### SMTP / Email")
        st.write(f"**SMTP Server:** {config.get('smtp_server', 'Ikke sat')}")
        st.write(f"**SMTP Port:** {config.get('smtp_port', 'Ikke sat')}")
        st.write(f"**SMTP Brugernavn:** {config.get('smtp_username', 'Ikke sat')}")
        password_val = config.get('smtp_password', '')
        if password_val:
            st.write(f"**SMTP Password:** {'*' * len(password_val)} (skjult)")
        else:
            st.write("**SMTP Password:** Ikke sat")
        st.write(f"**Admin Email:** {config.get('admin_email', 'Ikke sat')}")

        st.markdown("### Medarbejdere")
        for _, row in df.iterrows():
            with st.expander(f"{row['Name']} ({'Aktiv' if row['Active'] else 'Inaktiv'})"):
                st.write(f"**Email:** {row['Email']}")
                st.write(f"**Token:** `{row['Token']}`")
                params = []
                if row['Feriedage']: params.append("Feriedage")
                if row['Feriefridag']: params.append("Feriefridag")
                if row['Sygedage']: params.append("Sygedage")
                if row['Ekstra_Hverdag']: params.append("Ekstra Hverdag")
                if row['Ekstra_Lørdag']: params.append("Ekstra Lørdag")
                if row['Ekstra_Søndag']: params.append("Ekstra Søndag")
                if row['Ekstra_Andet']: params.append("Ekstra Andet")
                if row['Antal_timer']: params.append("Antal timer")
                st.write(f"**Parametre:** {', '.join(params) if params else 'Ingen'}")

        st.markdown("### GitHub Actions")
        st.info("Workflows kører dagligt kl. 08:00 UTC og tjekker om dags dato matcher de faste datoer.")
        st.write("**Reminders workflow:** `.github/workflows/reminders.yml`")
        st.write("**Aggregate workflow:** `.github/workflows/aggregate.yml`")

    with tab6:
        st.subheader("Simuler indsendelse")
        period_key, period_label = get_current_period()
        st.info(f"📅 Aktuel periode: **{period_label}**")
        st.write(
            "Klik for at sende en samlet opsummering af alle medarbejderes registreringer "
            "til administratoren nu – uanset hvilken dato det er i dag."
        )

        if st.button("Send opsummering til admin nu", type="primary", key="simulate_btn"):
            config = load_config()
            admin_email = config.get('admin_email', '')
            if not admin_email:
                st.error("Admin email ikke konfigureret i SMTP-indstillingerne!")
            elif not all([config.get('smtp_server'), config.get('smtp_username'), config.get('smtp_password')]):
                st.error("SMTP-indstillinger mangler!")
            else:
                with st.spinner("Indsamler data og sender email..."):
                    summary_df = collect_period_data(df, period_key)
                    submitted_count = (summary_df['Indberettet'] == 'Ja').sum()
                    total_count = len(summary_df)

                    st.write("**Forhåndsvisning:**")
                    st.dataframe(summary_df)

                    subject = f"Timeregnskab – {period_label}"
                    body = (
                        f"Timeregnskab\n"
                        f"Periode: {period_label}\n\n"
                        f"Indberettet: {submitted_count} ud af {total_count} medarbejdere\n\n"
                        f"{summary_df.to_string(index=False)}"
                    )
                    try:
                        send_email_smtp(admin_email, subject, body, config)
                        st.success(f"✅ Opsummering sendt til {admin_email}!")
                    except Exception as e:
                        st.error(f"Kunne ikke sende email: {str(e)}")

    st.divider()

    config = load_config()

    st.subheader("SMTP Email-indstillinger")
    st.info("Disse indstillinger bruges til at sende påmindelser og notifikationer.")

    col1, col2 = st.columns(2)
    with col1:
        smtp_server = st.text_input("SMTP Server", value=config.get('smtp_server', 'smtp.gmail.com'))
        smtp_port = st.number_input("SMTP Port", value=int(config.get('smtp_port', 587)), min_value=1, max_value=65535)
        smtp_username = st.text_input("SMTP Brugernavn (email)", value=config.get('smtp_username', ''))
    with col2:
        smtp_password = st.text_input("SMTP Password (app password)", value=config.get('smtp_password', ''), type="password")
        admin_email = st.text_input("Admin Email (modtager)", value=config.get('admin_email', ''))

    if st.button("Gem SMTP-indstillinger"):
        config['smtp_server'] = smtp_server
        config['smtp_port'] = smtp_port
        config['smtp_username'] = smtp_username
        config['smtp_password'] = smtp_password
        config['admin_email'] = admin_email
        if save_config(config):
            st.success("SMTP-indstillinger gemt!")
            st.rerun()

    if st.button("Send test-email"):
        try:
            send_email_smtp(
                admin_email,
                "Test email fra Timeregnskab",
                "Dette er en test email for at verificere SMTP-indstillingerne.",
                {'smtp_server': smtp_server, 'smtp_port': smtp_port,
                 'smtp_username': smtp_username, 'smtp_password': smtp_password}
            )
            st.success("✅ Test-email sendt! Tjek din indbakke.")
        except Exception as e:
            st.error(f"❌ Kunne ikke sende test-email: {str(e)}")


def employee_form():
    token = st.query_params.get("token", "")
    if not token:
        st.title("⏰ Timeregnskab")
        st.markdown("---")
        st.info("**Medarbejdere:** Du skal bruge det personlige link du har modtaget")
        st.info("**Admin:** Tilføj `?admin=true` til URL'en for at logge ind")
        st.markdown("---")
        st.caption("Kontakt admin hvis du mangler dit link")
        return

    df = load_employees()
    if df.empty:
        return

    employee = df[df['Token'] == token]
    if employee.empty:
        st.error("Ugyldig token")
        return

    emp = employee.iloc[0]
    period_key, period_label = get_current_period()
    existing = load_submission(emp['Name'], period_key)
    already_submitted = existing.get('udfyldt', False) if existing else False

    st.title(f"Timeregnskab – {emp['Name']}")
    st.info(f"📅 Periode: **{period_label}** | Frist: Den {DEADLINE_DAY}. i måneden")
    st.warning(
        f"Husk: Timer skal indberettes senest d. {DEADLINE_DAY}. i måneden. "
        f"Indberetninger der mangler efter fristen registreres ikke og medtages først i næste måneds opgørelse."
    )

    if already_submitted:
        st.success("✅ Du har allerede indberettet for denne periode.")

    data = {}

    if emp['Feriedage']:
        data['feriedage'] = st.number_input(
            "Feriedage",
            value=existing.get('feriedage', 0) if existing else 0,
            min_value=0, key="feriedage"
        )
    if emp['Feriefridag']:
        data['feriefridag'] = st.number_input(
            "Feriefridage",
            value=existing.get('feriefridag', 0) if existing else 0,
            min_value=0, key="feriefridag"
        )
    if emp['Sygedage']:
        data['sygedage'] = st.number_input(
            "Sygedage",
            value=existing.get('sygedage', 0) if existing else 0,
            min_value=0, key="sygedage"
        )
    if emp['Ekstra_Hverdag']:
        data['ekstra_hverdag'] = st.number_input(
            "Ekstra timer (Hverdag)",
            value=existing.get('ekstra_hverdag', 0) if existing else 0,
            min_value=0, key="hverdag"
        )
    if emp['Ekstra_Lørdag']:
        data['ekstra_lørdag'] = st.number_input(
            "Ekstra timer (Lørdag)",
            value=existing.get('ekstra_lørdag', 0) if existing else 0,
            min_value=0, key="lørdag"
        )
    if emp['Ekstra_Søndag']:
        data['ekstra_søndag'] = st.number_input(
            "Ekstra timer (Søndag)",
            value=existing.get('ekstra_søndag', 0) if existing else 0,
            min_value=0, key="søndag"
        )
    if emp['Ekstra_Andet']:
        data['ekstra_andet'] = st.number_input(
            "Ekstra timer (Andet)",
            value=existing.get('ekstra_andet', 0) if existing else 0,
            min_value=0, key="andet"
        )
    if emp['Antal_timer']:
        data['antal_timer'] = st.number_input(
            "Antal timer i alt",
            value=existing.get('antal_timer', 0) if existing else 0,
            min_value=0, key="timer"
        )

    st.markdown("---")
    st.error("**Indberet**")
    random_sender = random.choice(SENDERS)
    indberet = st.checkbox(
        f"Marker for at indberette {random_sender}",
        value=already_submitted,
        key="indberet"
    )
    data['udfyldt'] = indberet

    if st.button("Gem"):
        data['timestamp'] = datetime.now().isoformat()
        data['employee'] = emp['Name']
        data['month'] = period_key
        if save_submission(emp['Name'], data, period_key):
            if data.get('udfyldt'):
                st.success("✅ Indberettet!")
                st.balloons()
            else:
                st.success("Gemt!")


def main():
    if st.query_params.get("admin") == "true":
        admin_interface()
    else:
        employee_form()

if __name__ == "__main__":
    main()
