import streamlit as st
import pandas as pd
import os
from github import Github
import json
from datetime import datetime
import secrets

# Page config
st.set_page_config(page_title="Timeregnskab", page_icon="📊", layout="wide")

# Constants
REPO_OWNER = os.getenv("REPO_OWNER", "jxrgen")
REPO_NAME = os.getenv("REPO_NAME", "timeregnskab")
EMPLOYEES_FILE = "employees.csv"
SUBMISSIONS_DIR = "submissions"

def get_github_client():
    """Get authenticated GitHub client"""
    token = st.secrets.get("GITHUB_TOKEN", os.getenv("GITHUB_TOKEN"))
    if not token:
        st.error("GitHub token ikke konfigureret")
        return None
    return Github(token)

def load_employees():
    """Load employees from GitHub or local file"""
    try:
        g = get_github_client()
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            content = repo.get_contents(EMPLOYEES_FILE)
            import base64
            csv_content = base64.b64decode(content.content).decode('utf-8')
            from io import StringIO
            df = pd.read_csv(StringIO(csv_content))
        else:
            df = pd.read_csv(EMPLOYEES_FILE)
        return df
    except Exception as e:
        st.error(f"Kunne ikke indlæse medarbejdere: {e}")
        return pd.DataFrame(columns=['Name', 'Email', 'Active', 'Feriedage', 'Feriefridag', 'Sygedage', 
                                      'Ekstra_Hverdag', 'Ekstra_Lørdag', 'Ekstra_Søndag', 'Ekstra_Andet', 
                                      'Antal_timer', 'Token'])

def save_employees(df):
    """Save employees to GitHub or local file"""
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
        else:
            df.to_csv(EMPLOYEES_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Kunne ikke gemme medarbejdere: {e}")
        return False

def get_month_name():
    """Get current month name YYYY-MM"""
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"

def load_submission(employee_name, month=None):
    """Load submission for employee and month"""
    if month is None:
        month = get_month_name()
    try:
        g = get_github_client()
        file_path = f"{SUBMISSIONS_DIR}/{month}/{employee_name}.json"
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            content = repo.get_contents(file_path)
            import base64
            return json.loads(base64.b64decode(content.content).decode('utf-8'))
    except:
        pass
    return None

def save_submission(employee_name, data, month=None):
    """Save submission for employee"""
    if month is None:
        month = get_month_name()
    try:
        g = get_github_client()
        file_path = f"{SUBMISSIONS_DIR}/{month}/{employee_name}.json"
        content = json.dumps(data, ensure_ascii=False, indent=2)
        if g:
            repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
            try:
                file = repo.get_contents(file_path)
                repo.update_file(file_path, f"Opdateret {month}/{employee_name}", content, file.sha)
            except:
                repo.create_file(file_path, f"Oprettet {month}/{employee_name}", content)
        return True
    except Exception as e:
        st.error(f"Kunne ikke gemme submission: {e}")
        return False

def generate_token():
    """Generate unique token for employee"""
    return secrets.token_urlsafe(16)

# Admin interface
def admin_interface():
    st.title("⚙️ Admin Interface")
    
    # Simple password protection
    admin_password = st.secrets.get("ADMIN_PASSWORD", os.getenv("ADMIN_PASSWORD", "admin123"))
    password = st.text_input("Adgangskode", type="password")
    if password != admin_password:
        if password:
            st.error("Forkert adgangskode")
        return
    
    st.success("Velkommen til admin interface")
    
    df = load_employees()
    
    tab1, tab2, tab3 = st.tabs(["Medarbejdere", "Tilføj ny", "Indsendelser"])
    
    with tab1:
        st.subheader("Eksisterende medarbejdere")
        if not df.empty:
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
                            df.loc[idx, 'Name'] = new_name
                            df.loc[idx, 'Email'] = new_email
                            df.loc[idx, 'Active'] = new_active
                            df.loc[idx, 'Feriedage'] = feriedage
                            df.loc[idx, 'Feriefridag'] = feriefridag
                            df.loc[idx, 'Sygedage'] = sygedage
                            df.loc[idx, 'Ekstra_Hverdag'] = ekstra_hverdag
                            df.loc[idx, 'Ekstra_Lørdag'] = ekstra_lørdag
                            df.loc[idx, 'Ekstra_Søndag'] = ekstra_søndag
                            df.loc[idx, 'Ekstra_Andet'] = ekstra_andet
                            df.loc[idx, 'Antal_timer'] = antal_timer
                            if save_employees(df):
                                st.success("Gemt!")
                                st.rerun()
                    
                    with col2:
                        if st.button("Ny token", key=f"token_{idx}"):
                            df.loc[idx, 'Token'] = generate_token()
                            if save_employees(df):
                                st.success(f"Ny token: {df.loc[idx, 'Token']}")
                                st.rerun()
                    
                    with col3:
                        if st.button("Slet", key=f"delete_{idx}"):
                            df = df.drop(idx).reset_index(drop=True)
                            if save_employees(df):
                                st.success("Slettet!")
                                st.rerun()
                    
                    # Show link
                    token = row['Token']
                    link = f"{st.secrets.get('APP_URL', 'https://your-app.streamlit.app')}/?token={token}"
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

# Employee form
def employee_form():
    token = st.query_params.get("token", "")
    
    if not token:
        st.error("Ingen adgang - mangler token")
        return
    
    df = load_employees()
    employee = df[df['Token'] == token]
    
    if employee.empty:
        st.error("Ugyldig token")
        return
    
    emp = employee.iloc[0]
    st.title(f"Timeregnskab - {emp['Name']}")
    st.write(f"Måned: {get_month_name()}")
    
    # Load existing submission
    existing = load_submission(emp['Name'])
    
    with st.form("time_form"):
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
        
        data['udfyldt'] = st.checkbox("Udfyldt (marker når færdig)", value=existing.get('udfyldt', False) if existing else False)
        
        submitted = st.form_submit_button("Gem")
        if submitted:
            data['timestamp'] = datetime.now().isoformat()
            data['employee'] = emp['Name']
            data['month'] = get_month_name()
            if save_submission(emp['Name'], data):
                st.success("Gemt!")
                if data['udfyldt']:
                    st.balloons()

# Main app logic
def main():
    # Check if admin parameter is set
    if st.query_params.get("admin") == "true":
        admin_interface()
    else:
        employee_form()

if __name__ == "__main__":
    main()
