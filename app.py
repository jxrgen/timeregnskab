import streamlit as st
import pandas as pd
import os
from github import Github
import json
from datetime import datetime
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
    
    tab1, tab2, tab3 = st.tabs(["Medarbejdere", "Tilføj ny", "Indsendelser"])
    
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
        month = st.selectbox("Vælg måned", [get_month_name(), "2026-03", "2026-02"])
        if not df.empty:
            for idx, row in df.iterrows():
                if row['Active']:
                    submission = load_submission(row['Name'], month)
                    status = "✅ Udfyldt" if submission and submission.get('udfyldt') else "❌ Mangler"
                    st.write(f"{row['Name']}: {status}")
    
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
    st.title(f"Timeregnskab - {emp['Name']}")
    st.write(f"Måned: {get_month_name()}")
    
    existing = load_submission(emp['Name'])
    
    data = {}
    
    if emp['Feriedage']:
        data['feriedage'] = st.number_input("Feriedage", value=existing.get('feriedage', 0) if existing else 0, min_value=0)
    if emp['Feriefridag']:
        data['feriefridag'] = st.number_input("Feriefridage", value=existing.get('feriefridag', 0) if existing else 0, min_value=0)
    if emp['Sygedage']:
        data['sygedage'] = st.number_input("Sygedage", value=existing.get('sygedage', 0) if existing else 0, min_value=0)
    if emp['Ekstra_Hverdag']:
        data['ekstra_hverdag'] = st.number_input("Ekstra timer (Hverdag)", value=existing.get('ekstra_hverdag', 0) if existing else 0, min_value=0)
    if emp['Ekstra_Lørdag']:
        data['ekstra_lørdag'] = st.number_input("Ekstra timer (Lørdag)", value=existing.get('ekstra_lørdag', 0) if existing else 0, min_value=0)
    if emp['Ekstra_Søndag']:
        data['ekstra_søndag'] = st.number_input("Ekstra timer (Søndag)", value=existing.get('ekstra_søndag', 0) if existing else 0, min_value=0)
    if emp['Ekstra_Andet']:
        data['ekstra_andet'] = st.number_input("Ekstra timer (Andet)", value=existing.get('ekstra_andet', 0) if existing else 0, min_value=0)
    if emp['Antal_timer']:
        data['antal_timer'] = st.number_input("Antal timer i alt", value=existing.get('antal_timer', 0) if existing else 0, min_value=0)
    
    st.markdown("---")
    
    if 'indberet_state' not in st.session_state:
        st.session_state.indberet_state = 'idle'
        st.session_state.indberet_cb = existing.get('udfyldt', False) if existing else False
        st.session_state.indberet_confirmed = existing.get('udfyldt', False) if existing else False
    
    # Red border around checkbox
    st.markdown('<div style="border: 2px solid red; padding: 10px; border-radius: 5px; margin: 10px 0;">', unsafe_allow_html=True)
    st.checkbox("Marker for at indberette", value=st.session_state.indberet_cb, key="indberet_cb")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle checkbox state changes
    if st.session_state.indberet_cb and st.session_state.indberet_state == 'idle':
        st.session_state.indberet_state = 'confirming'
        st.rerun()
    
    if not st.session_state.indberet_cb and st.session_state.indberet_confirmed:
        st.session_state.indberet_confirmed = False
        st.session_state.indberet_state = 'idle'
    
    # Confirmation popup
    if st.session_state.indberet_state == 'confirming':
        st.warning("⚠️ Vil du indberette nu?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ja, indberet nu", key="confirm_yes"):
                st.session_state.indberet_confirmed = True
                st.session_state.indberet_state = 'confirmed'
                st.rerun()
        with col2:
            if st.button("Nej, annuller", key="confirm_no"):
                st.session_state.indberet_confirmed = False
                st.session_state.indberet_state = 'idle'
                st.session_state.indberet_cb = False
                st.rerun()
        st.markdown("---")
    
    data['udfyldt'] = st.session_state.get('indberet_confirmed', False)
    
    if st.button("Gem"):
        data['timestamp'] = datetime.now().isoformat()
        data['employee'] = emp['Name']
        data['month'] = get_month_name()
        
        if save_submission(emp['Name'], data):
            if data['udfyldt']:
                st.success("✅ Indberettet!")
                st.balloons()
                st.session_state.indberet_state = 'idle'
            else:
                st.success("Gemt!")

def main():
    if st.query_params.get("admin") == "true":
        admin_interface()
    else:
        employee_form()

if __name__ == "__main__":
    main()
