import os
import pandas as pd
import json
from datetime import datetime
from github import Github
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

REMINDER_DAY = 18
DEADLINE_DAY = 20

MONTHS_DA = {
    1: 'januar', 2: 'februar', 3: 'marts', 4: 'april',
    5: 'maj', 6: 'juni', 7: 'juli', 8: 'august',
    9: 'september', 10: 'oktober', 11: 'november', 12: 'december'
}

SENDERS = [
    "din digitale påminder",
    "the central scrutinizer",
    "den store EDB-maskine der styrer alting",
    "en ganske automatiseret udsendelsestjeneste",
    "bzzzcrrtping...",
    "den elektroniske brevdue",
    "Robotten fra afdeling 7",
    "Den Digitale Timeregnskabs-Politi",
    "System 32 (ja, det kører stadig)",
    "Den Autonome Påmindelses-Enhed",
    "Overlord 3000 - Påmindelsesmodul",
    "Den mystiske mail-mand",
    "Tidsmaskinen T-800",
    "Den travle administrative algoritme",
    "Kvorums-gnomen",
    "Den digitale klipper",
    "Pakke-Post-Peter",
    "Sir Sender af Camelot",
    "Den flyvende hollandsk rapport",
    "Den uundgåelige notifikation",
]

def send_email(to_email, subject, body, smtp_config):
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_config['username']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        port = int(smtp_config['port'])
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_config['server'], port)
        else:
            server = smtplib.SMTP(smtp_config['server'], port)
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

    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_user(repo_owner).get_repo(repo_name)

    config = {}
    try:
        content = repo.get_contents("config.json")
        import base64
        config = json.loads(base64.b64decode(content.content).decode('utf-8'))
    except Exception as e:
        print(f"Kunne ikke indlæse config.json: {e}")
        return

    # Læs app_url fra config.json (primær) eller env var (fallback)
    app_url = config.get('app_url', '').rstrip('/') or os.getenv("APP_URL", "").rstrip('/')
    if not app_url:
        print("ADVARSEL: app_url er ikke konfigureret i config.json eller APP_URL env var — links i mails vil være ufuldstændige!")
        app_url = ""

    now = datetime.now()
    if now.day != REMINDER_DAY:
        print(f"Ikke påmindelsesdag (i dag er den {now.day}., skal være den {REMINDER_DAY}.)")
        return

    smtp_config = {
        'server': config.get('smtp_server', 'smtp.gmail.com'),
        'port': config.get('smtp_port', 587),
        'username': config.get('smtp_username', ''),
        'password': config.get('smtp_password', ''),
    }
    if not all([smtp_config['username'], smtp_config['password']]):
        print("SMTP config mangler i config.json")
        return

    # Load employees
    content = repo.get_contents("employees.csv")
    import base64
    csv_content = base64.b64decode(content.content).decode('utf-8')
    from io import StringIO
    df = pd.read_csv(StringIO(csv_content))

    # Current period: 21st of last month to 20th of this month (since today is the 18th)
    if now.month > 1:
        prev_month_num = now.month - 1
        prev_month_year = now.year
    else:
        prev_month_num = 12
        prev_month_year = now.year - 1
    period_label = (
        f"21. {MONTHS_DA[prev_month_num]} {prev_month_year} "
        f"– 20. {MONTHS_DA[now.month]} {now.year}"
    )

    # Send reminder to ALL active employees
    for _, emp in df.iterrows():
        if not emp['Active']:
            continue

        sender = random.choice(SENDERS)
        subject = f"Påmindelse: Timeregnskab – {period_label}"
        body = f"""Hej {emp['Name']},

Husk at udfylde dit timeregnskab for perioden {period_label}.
Fristen er den {DEADLINE_DAY}. i måneden.

Du kan udfylde det her:
{app_url}/?token={emp['Token']}

Mange hilsner,
{sender}"""

        if send_email(emp['Email'], subject, body, smtp_config):
            print(f"Påmindelse sendt til {emp['Name']}")
        else:
            print(f"Kunne ikke sende til {emp['Name']}")

if __name__ == "__main__":
    main()
