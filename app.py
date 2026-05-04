import streamlit as st
import pandas as pd
import os
from github import Github
import json
from datetime import datetime, timedelta
import secrets

st.set_page_config(page_title="Timeregnskab", page_icon="📊", layout="wide")

REPO_OWNER = os.getenv("REPO_OWNER", "jxrgen")
REPO_NAME = os.getenv("REPO_NAME", "timeregnskab")
EMPLOYEES_FILE = "employees.csv"
SUBMISSIONS_DIR = "submissions"

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

def get_month_name():
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"

def load_submission(employee_name, month=None):
    if month is None:
        month = get_month_name()
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

def save_submission(employee_name, data, month=None):
    if month is None:
        month = get_month_name()
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
    return {"submission_deadline_day": 20, "admin_notification_day": 25}

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

def admin_interface():
    st.title("⚙️ Admin Interface")
    admin_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
    password = st.text_input("Adgangskode", type="password")
    if password != admin_password:
        if password:
            st.error("Forkert adgangskode")
        return
    
    st.success("Velkommen til admin interface")
    st.markdown("**Funktionalitet:** Her kan du administrere medarbejdere, tilføje nye og se indsendelser. Du kan også ændre generelle indstillinger for tidsfrister og notifikationer.")
    
    df = load_employees()
    
    if df.empty:
        st.warning("Kunne ikke indlæse medarbejdere")
        return
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Medarbejdere", "Tilføj ny", "Indsendelser", "Fælles besked", "Systeminfo"])
    
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
        # Brug de seneste 3 måneder med dansk format
        current = get_month_name()
        months_options = [current, get_previous_month(current), get_previous_month(get_previous_month(current))]
        month_labels = [format_month_danish(m) for m in months_options]
        selected_idx = st.selectbox("Vælg måned", range(len(month_labels)), format_func=lambda i: month_labels[i])
        month = months_options[selected_idx]
        if not df.empty:
            for idx, row in df.iterrows():
                if row['Active']:
                    submission = load_submission(row['Name'], month)
                    status = "✅ Udfyldt" if submission and submission.get('udfyldt') else "❌ Mangler"
                    st.write(f"{row['Name']}: {status}")
    
    with tab4:
        st.subheader("Fælles besked")
        st.write("Vælg medarbejdere og skriv en besked der skal sendes til dem alle.")
        
        # Show all employees with checkboxes
        st.write("**Vælg modtagere:**")
        selected = []
        for idx, row in df.iterrows():
            if row['Active']:
                if st.checkbox(f"{row['Name']} ({row['Email']})", key=f"select_{idx}"):
                    selected.append(row)
        
        # Message text area
        st.write("**Skriv besked:**")
        message = st.text_area("Besked", height=150, key="common_message")
        
        # Send button
        if st.button("Send fælles besked", key="send_common"):
            if not message:
                st.error("Du skal skrive en besked!")
            elif not selected:
                st.error("Du skal vælge mindst en medarbejder!")
            else:
                # Get SMTP config
                config = load_config()
                smtp_server = config.get('smtp_server', '')
                smtp_port = config.get('smtp_port', 587)
                smtp_username = config.get('smtp_username', '')
                smtp_password = config.get('smtp_password', '')
                
                if not all([smtp_server, smtp_username, smtp_password]):
                    st.error("SMTP-indstillinger mangler! Konfigurer dem nederst på siden.")
                else:
                    import smtplib
                    from email.mime.text import MIMEText
                    from email.mime.multipart import MIMEMultipart
                    
                    sent_count = 0
                    error_count = 0
                    
                    for emp in selected:
                        try:
                            msg = MIMEMultipart()
                            msg['From'] = smtp_username
                            msg['To'] = emp['Email']
                            msg['Subject'] = "Besked fra Timeregnskab"
                            
                            body = f"Hej {emp['Name']},\n\n{message}\n\nVenlig hilsen,\nAdministrationen"
                            msg.attach(MIMEText(body, 'plain', 'utf-8'))
                            
                            port = int(smtp_port)
                            if port == 465:
                                server = smtplib.SMTP_SSL(smtp_server, port)
                            else:
                                server = smtplib.SMTP(smtp_server, port)
                                server.starttls()
                            
                            server.login(smtp_username, smtp_password)
                            server.send_message(msg)
                            server.quit()
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
        
        # Repository info
        st.markdown("### Repository")
        st.write(f"**Owner:** {REPO_OWNER}")
        st.write(f"**Repository:** {REPO_NAME}")
        app_url = st.secrets.get("APP_URL", "Ikke konfigureret")
        st.write(f"**App URL:** {app_url}")
        
        # Admin settings
        st.markdown("### Indstillinger")
        st.write(f"**Seneste indberetningsdag:** Den {config.get('submission_deadline_day', 3)}. i måneden")
        st.write(f"**Admin notifikationsdag:** Den {config.get('admin_notification_day', 25)}. i måneden")
        
        # SMTP info
        st.markdown("### SMTP / Email")
        st.write(f"**SMTP Server:** {config.get('smtp_server', 'Ikke sat')}")
        st.write(f"**SMTP Port:** {config.get('smtp_port', 'Ikke sat')}")
        st.write(f"**SMTP Brugernavn:** {config.get('smtp_username', 'Ikke sat')}")
        password = config.get('smtp_password', '')
        if password:
            st.write(f"**SMTP Password:** {'*' * len(password)} (skjult)")
        else:
            st.write("**SMTP Password:** Ikke sat")
        st.write(f"**Admin Email:** {config.get('admin_email', 'Ikke sat')}")
        
        # Employees
        st.markdown("### Medarbejdere")
        if not df.empty:
            for idx, row in df.iterrows():
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
        
        # GitHub Actions info
        st.markdown("### GitHub Actions")
        st.info("Workflows kører dagligt kl. 08:00 UTC og tjekker om dags dato matcher konfigurationen.")
        st.write("**Reminders workflow:** `.github/workflows/reminders.yml`")
        st.write("**Aggregate workflow:** `.github/workflows/aggregate.yml`")
    
    st.divider()
    
    config = load_config()
    
    st.subheader("Instruktioner og overordnede indstillinger")
    st.write(f"Medarbejderne skal indberette deres skema senest d. {config.get('submission_deadline_day', 20)} i hver måned. Hvis en medarbejder ikke har gjort det, vil der automatisk blive sendt en påmindelsesmail til vedkommende. Alle skemaer vil blive sendt til administratoren d. {config.get('admin_notification_day', 25)} i måneden.")
    
    col1, col2 = st.columns(2)
    with col1:
        new_deadline = st.number_input("Seneste indberetningsdag", min_value=1, max_value=31, value=config.get('submission_deadline_day', 20))
    with col2:
        new_notification = st.number_input("Dag for afsendelse til admin", min_value=1, max_value=31, value=config.get('admin_notification_day', 25))
    
    if st.button("Gem indstillinger"):
        config['submission_deadline_day'] = new_deadline
        config['admin_notification_day'] = new_notification
        if save_config(config):
            st.success("Indstillinger gemt!")
            st.rerun()
    
    st.subheader("SMTP Email-indstillinger")
    st.info("Disse indstillinger bruges til at sende påmindelser og notifikationer via GitHub Actions.")
    
    col1, col2 = st.columns(2)
    with col1:
        smtp_server = st.text_input("SMTP Server", value=config.get('smtp_server', 'smtp.gmail.com'))
        smtp_port = st.number_input("SMTP Port", value=int(config.get('smtp_port', 587)), min_value=1, max_value=65535)
        smtp_username = st.text_input("Smtp Brugernavn (email)", value=config.get('smtp_username', ''))
    with col2:
        smtp_password = st.text_input("Smtp Password (app password)", value=config.get('smtp_password', ''), type="password")
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
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg["From"] = smtp_username
            msg["To"] = admin_email
            msg["Subject"] = "Test email fra Timeregnskab"
            
            body = "Dette er en test email for at verificere SMTP-indstillingerne."
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            port = int(smtp_port)
            if port == 465:
                server = smtplib.SMTP_SSL(smtp_server, port)
            else:
                server = smtplib.SMTP(smtp_server, port)
                server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            st.success("✅ Test-email sendt! Tjek din indbakke.")
        except Exception as e:
            st.error(f"❌ Kunne ikke sende test-email: {str(e)}")
 
def get_next_month(month_str):
    """Returnerer næste måned som YYYY-MM"""
    year, month = map(int, month_str.split('-'))
    if month == 12:
        return f"{year + 1}-01"
    return f"{year}-{month + 1:02d}"

def get_previous_month(month_str):
    """Returnerer forrige måned som YYYY-MM"""
    year, month = map(int, month_str.split('-'))
    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{month - 1:02d}"

def format_month_danish(month_str):
    """Konverterer YYYY-MM til dansk månedsformat (f.eks. 'Maj 2026')"""
    months_da = {
        1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April',
        5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'December'
    }
    year, month = map(int, month_str.split('-'))
    return f"{months_da[month]} {year}"

def load_transfer_data(employee_name, from_month):
    """Indlæser overførselsdata fra en måned"""
    try:
        g = get_github_client()
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            file_path = f"{SUBMISSIONS_DIR}/{from_month}/transfer_{employee_name}.json"
            content = repo.get_contents(file_path)
            import base64
            return json.loads(base64.b64decode(content.content).decode('utf-8'))
    except:
        pass
    return None

def save_transfer_data(employee_name, from_month, to_month, data):
    """Gemmer overførselsdata fra en måned til næste"""
    try:
        g = get_github_client()
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            file_path = f"{SUBMISSIONS_DIR}/{from_month}/transfer_{employee_name}.json"
            transfer_data = {
                'from_month': from_month,
                'to_month': to_month,
                'employee': employee_name,
                'timestamp': datetime.now().isoformat(),
                'transferred_data': data
            }
            content = json.dumps(transfer_data, ensure_ascii=False, indent=2)
            try:
                file = repo.get_contents(file_path)
                repo.update_file(file_path, f"Overførsel {from_month} -> {to_month}", content, file.sha)
            except:
                repo.create_file(file_path, f"Overførsel {from_month} -> {to_month}", content)
            return True
    except Exception as e:
        st.error(f"Kunne ikke gemme overførselsdata: {str(e)}")
    return False

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
    
    # Indlæs config til datoer
    config = load_config()
    submission_deadline_day = config.get('submission_deadline_day', 20)
    admin_notification_day = config.get('admin_notification_day', 25)
    
    # Konstruer måneds-liste: current + next
    current_month = get_month_name()
    next_month = get_next_month(current_month)
    
    st.title(f"Timeregnskab - {emp['Name']}")
    
    # Vis info om frister
    st.info(f"📅 Frist for indberetning: Den {submission_deadline_day}. i måneden | Admin modtager data: Den {admin_notification_day}.")
    
    # Vis to måneder side om side
    col1, col2 = st.columns(2)
    
    for i, month in enumerate([current_month, next_month]):
        with col1 if i == 0 else col2:
            st.subheader(f"📆 {format_month_danish(month)}")
            
            # Indlæs eksisterende data
            existing = load_submission(emp['Name'], month)
            
            # For næste måned: vis overført data fra denne måned
            if month == next_month:
                transfer = load_transfer_data(emp['Name'], current_month)
                if transfer and 'transferred_data' in transfer:
                    transferred = transfer['transferred_data']
                    summary = transferred.get('summary', 'Ingen timer')
                    st.success(f"🔄 Overført fra {current_month}: {summary}")
            
            data = {}
            
            # Vis felter
            if emp['Feriedage']:
                data['feriedage'] = st.number_input("Feriedage", value=existing.get('feriedage', 0) if existing else 0, min_value=0, key=f"feriedage_{month}")
            if emp['Feriefridag']:
                data['feriefridag'] = st.number_input("Feriefridage", value=existing.get('feriefridag', 0) if existing else 0, min_value=0, key=f"feriefridag_{month}")
            if emp['Sygedage']:
                data['sygedage'] = st.number_input("Sygedage", value=existing.get('sygedage', 0) if existing else 0, min_value=0, key=f"sygedage_{month}")
            if emp['Ekstra_Hverdag']:
                data['ekstra_hverdag'] = st.number_input("Ekstra timer (Hverdag)", value=existing.get('ekstra_hverdag', 0) if existing else 0, min_value=0, key=f"hverdag_{month}")
            if emp['Ekstra_Lørdag']:
                data['ekstra_lørdag'] = st.number_input("Ekstra timer (Lørdag)", value=existing.get('ekstra_lørdag', 0) if existing else 0, min_value=0, key=f"lørdag_{month}")
            if emp['Ekstra_Søndag']:
                data['ekstra_søndag'] = st.number_input("Ekstra timer (Søndag)", value=existing.get('ekstra_søndag', 0) if existing else 0, min_value=0, key=f"søndag_{month}")
            if emp['Ekstra_Andet']:
                data['ekstra_andet'] = st.number_input("Ekstra timer (Andet)", value=existing.get('ekstra_andet', 0) if existing else 0, min_value=0, key=f"andet_{month}")
            if emp['Antal_timer']:
                data['antal_timer'] = st.number_input("Antal timer i alt", value=existing.get('antal_timer', 0) if existing else 0, min_value=0, key=f"timer_{month}")
            
            st.markdown("---")
            
            # Indberet checkbox (kun for current_month)
            if month == current_month:
                st.error("**Indberet**")
                # Vælg en tilfældig sjov afsender
                import random
                senders = [
                    "til den store EDB-maskine",
                    "til din digitale påminder",
                    "til the central scrutinizer",
                    "til den elektroniske brevdue",
                    "til Robotten fra afdeling 7",
                    "til Den Digitale Timeregnskabs-Politi",
                    "til System 32 (ja, det kører stadig)",
                    "til Den Autonome Påmindelses-Enhed",
                    "til Overlord 3000 - Påmindelsesmodul",
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
                    # 20 nye sjove afsendere
                    "til Den digitale vandmand",
                    "til Systemfejl 404 - ikke fundet",
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
                    "til Den digitale driller"
                ]
                random_sender = random.choice(senders)
                indberet = st.checkbox(f"Marker for at indberette {random_sender}", value=False, key=f"indberet_{month}")
                data['udfyldt'] = indberet
            else:
                data['udfyldt'] = existing.get('udfyldt', False) if existing else False
            
            # Gem knap
            if st.button("Gem", key=f"save_{month}"):
                data['timestamp'] = datetime.now().isoformat()
                data['employee'] = emp['Name']
                data['month'] = month
                
                if save_submission(emp['Name'], data, month):
                    # Hvis det er current_month og den er indberettet, gem overførselsdata
                    if month == current_month and data.get('udfyldt'):
                        # Lav en summary til overførsel
                        summary_parts = []
                        for key in ['feriedage', 'feriefridag', 'sygedage', 'ekstra_hverdag', 'ekstra_lørdag', 'ekstra_søndag', 'ekstra_andet', 'antal_timer']:
                            if key in data and data[key] > 0:
                                summary_parts.append(f"{key}: {data[key]}")
                        data['summary'] = ', '.join(summary_parts) if summary_parts else 'Ingen timer'
                        
                        # Gem overførselsdata til næste måned
                        save_transfer_data(emp['Name'], current_month, next_month, data)
                    
                    if data.get('udfyldt') and month == current_month:
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
