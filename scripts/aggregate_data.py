import os
import pandas as pd
import json
from datetime import datetime
from github import Github
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body, smtp_config):
    """Send email via SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_config['username']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(smtp_config['server'], int(smtp_config['port']))
        server.starttls()
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error for {to_email}: {e}")
        return False

def main():
    repo_owner = os.getenv("REPO_OWNER")
    repo_name = os.getenv("REPO_NAME")
    admin_email = os.getenv("ADMIN_EMAIL")
    app_url = os.getenv("APP_URL", "https://your-app.streamlit.app")
    
    # Optional SMTP for summary email
    smtp_config = None
    if os.getenv("SMTP_USERNAME"):
        smtp_config = {
            'server': os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            'port': os.getenv("SMTP_PORT", "587"),
            'username': os.getenv("SMTP_USERNAME"),
            'password': os.getenv("SMTP_PASSWORD")
        }
    
    # GitHub client
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_user(repo_owner).get_repo(repo_name)
    
    # Load employees
    content = repo.get_contents("employees.csv")
    import base64
    csv_content = base64.b64decode(content.content).decode('utf-8')
    from io import StringIO
    df = pd.read_csv(StringIO(csv_content))
    
    now = datetime.now()
    month_name = f"{now.year}-{now.month:02d}"
    
    # Collect all submissions for current month
    all_data = []
    for _, emp in df.iterrows():
        if not emp['Active']:
            continue
        
        try:
            submission_path = f"submissions/{month_name}/{emp['Name']}.json"
            content = repo.get_contents(submission_path)
            import base64
            submission = json.loads(base64.b64decode(content.content).decode('utf-8'))
            all_data.append({
                'Måned': month_name,
                'Medarbejder': emp['Name'],
                'Email': emp['Email'],
                'Feriedage': submission.get('feriedage', 0),
                'Feriefridage': submission.get('feriefridag', 0),
                'Sygedage': submission.get('sygedage', 0),
                'Ekstra Hverdag': submission.get('ekstra_hverdag', 0),
                'Ekstra Lørdag': submission.get('ekstra_lørdag', 0),
                'Ekstra Søndag': submission.get('ekstra_søndag', 0),
                'Ekstra Andet': submission.get('ekstra_andet', 0),
                'Antal Timer': submission.get('antal_timer', 0),
                'Udfyldt': 'Ja' if submission.get('udfyldt') else 'Nej',
                'Sidst opdateret': submission.get('timestamp', '')
            })
        except:
            all_data.append({
                'Måned': month_name,
                'Medarbejder': emp['Name'],
                'Email': emp['Email'],
                'Feriedage': 0,
                'Feriefridage': 0,
                'Sygedage': 0,
                'Ekstra Hverdag': 0,
                'Ekstra Lørdag': 0,
                'Ekstra Søndag': 0,
                'Ekstra Andet': 0,
                'Antal Timer': 0,
                'Udfyldt': 'Nej',
                'Sidst opdateret': ''
            })
    
    # Save summary as CSV in repo
    summary_df = pd.DataFrame(all_data)
    csv_content = summary_df.to_csv(index=False)
    
    summary_path = f"summary/{month_name}.csv"
    try:
        file = repo.get_contents(summary_path)
        repo.update_file(summary_path, f"Opdateret summary {month_name}", csv_content, file.sha)
    except:
        repo.create_file(summary_path, f"Oprettet summary {month_name}", csv_content)
    
    print(f"Summary gemt: {summary_path}")
    print(summary_df.to_string())
    
    # Send email to admin
    if admin_email and smtp_config:
        subject = f"Timeregnskab opsummering - {month_name}"
        body = f"""Hej Admin,

Data for {month_name} er samlet.

Se oversigten her: {app_url}/?admin=true

Venlig hilsen,
Timeregnskab System"""
        
        if send_email(admin_email, subject, body, smtp_config):
            print(f"Opsummering sendt til {admin_email}")
        else:
            print("Kunne ikke sende opsummering")

if __name__ == "__main__":
    main()
