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
    # Config
    repo_owner = os.getenv("REPO_OWNER")
    repo_name = os.getenv("REPO_NAME")
    app_url = os.getenv("APP_URL", "https://your-app.streamlit.app")
    
    smtp_config = {
        'server': os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        'port': os.getenv("SMTP_PORT", "587"),
        'username': os.getenv("SMTP_USERNAME"),
        'password': os.getenv("SMTP_PASSWORD")
    }
    
    if not all(smtp_config.values()):
        print("SMTP config mangler")
        return
    
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
    
    # Check each employee
    for _, emp in df.iterrows():
        if not emp['Active']:
            continue
        
        token = emp['Token']
        employee_name = emp['Name']
        email = emp['Email']
        
        # Check if already submitted
        try:
            submission_path = f"submissions/{month_name}/{employee_name}.json"
            repo.get_contents(submission_path)
            print(f"{employee_name}: Allerede indsendt")
            continue
        except:
            pass
        
        # Send reminder
        subject = f"Påmindelse: Timeregnskab for {month_name}"
        body = f"""Hej {employee_name},

Du har endnu ikke udfyldt dit timeregnskab for {month_name}.
Fristen er den 25. i måneden.

Du kan udfylde det her:
{app_url}/?token={token}

Venlig hilsen,
Administrationen"""
        
        if send_email(email, subject, body, smtp_config):
            print(f"Påmindelse sendt til {employee_name}")
        else:
            print(f"Kunne ikke sende til {employee_name}")

if __name__ == "__main__":
    main()
