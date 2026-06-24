import os
import pandas as pd
import json
from datetime import datetime
from github import Github
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

AGGREGATE_DAY = 21

MONTHS_DA = {
    1: 'januar', 2: 'februar', 3: 'marts', 4: 'april',
    5: 'maj', 6: 'juni', 7: 'juli', 8: 'august',
    9: 'september', 10: 'oktober', 11: 'november', 12: 'december'
}

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
    app_url = os.getenv("APP_URL", "https://your-app.streamlit.app")

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

    now = datetime.now()
    if now.day != AGGREGATE_DAY:
        print(f"Ikke opsamlingsdag (i dag er den {now.day}., skal være den {AGGREGATE_DAY}.)")
        return

    smtp_config = {
        'server': config.get('smtp_server', 'smtp.gmail.com'),
        'port': config.get('smtp_port', 587),
        'username': config.get('smtp_username', ''),
        'password': config.get('smtp_password', ''),
    }
    admin_email = config.get('admin_email', '')

    # The period that just ended: 21st of last month to 20th of this month.
    # Submissions are stored under the end month (current calendar month).
    month_key = f"{now.year}-{now.month:02d}"
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

    # Load employees
    content = repo.get_contents("employees.csv")
    import base64
    csv_content = base64.b64decode(content.content).decode('utf-8')
    from io import StringIO
    df = pd.read_csv(StringIO(csv_content))

    # Collect all submissions (submitted and not submitted)
    all_data = []
    for _, emp in df.iterrows():
        if not emp['Active']:
            continue

        submission = None
        try:
            content = repo.get_contents(f"submissions/{month_key}/{emp['Name']}.json")
            submission = json.loads(base64.b64decode(content.content).decode('utf-8'))
        except:
            pass

        submitted = submission.get('udfyldt', False) if submission else False
        all_data.append({
            'Medarbejder': emp['Name'],
            'Email': emp['Email'],
            'Indberettet': 'Ja' if submitted else 'Nej',
            'Feriedage': submission.get('feriedage', 0) if submission else '-',
            'Feriefridage': submission.get('feriefridag', 0) if submission else '-',
            'Sygedage': submission.get('sygedage', 0) if submission else '-',
            'Ekstra hverdag': submission.get('ekstra_hverdag', 0) if submission else '-',
            'Ekstra lørdag': submission.get('ekstra_lørdag', 0) if submission else '-',
            'Ekstra søndag': submission.get('ekstra_søndag', 0) if submission else '-',
            'Ekstra andet': submission.get('ekstra_andet', 0) if submission else '-',
            'Antal timer': submission.get('antal_timer', 0) if submission else '-',
        })

    summary_df = pd.DataFrame(all_data)
    submitted_count = (summary_df['Indberettet'] == 'Ja').sum()
    total_count = len(summary_df)

    print(f"Periode: {period_label}")
    print(f"Indberettet: {submitted_count}/{total_count}")
    print(summary_df.to_string(index=False))

    # Save summary CSV to repo
    summary_path = f"summary/{month_key}.csv"
    csv_content_out = summary_df.to_csv(index=False)
    try:
        file = repo.get_contents(summary_path)
        repo.update_file(summary_path, f"Opdateret summary {month_key}", csv_content_out, file.sha)
    except:
        repo.create_file(summary_path, f"Oprettet summary {month_key}", csv_content_out)
    print(f"Summary gemt: {summary_path}")

    # Archive submissions
    backup_path = f"archive/{month_key}"
    try:
        repo.create_file(f"{backup_path}/.keep", f"Oprettet archive mappe for {month_key}", "")
    except:
        pass

    for _, emp in df.iterrows():
        if not emp['Active']:
            continue
        try:
            submission_path = f"submissions/{month_key}/{emp['Name']}.json"
            content = repo.get_contents(submission_path)
            file_content = base64.b64decode(content.content).decode('utf-8')
            repo.create_file(
                f"{backup_path}/{emp['Name']}.json",
                f"Arkiveret {month_key}/{emp['Name']}",
                file_content
            )
            repo.delete_file(submission_path, f"Slettet efter arkivering {submission_path}", content.sha)
            print(f"Arkiveret: {emp['Name']}")
        except:
            pass

    print(f"Arkivering fuldført for {month_key}")

    # Send ONE email to admin with the full table
    if admin_email and all([smtp_config['username'], smtp_config['password']]):
        subject = f"Timeregnskab – {period_label}"
        body = (
            f"Timeregnskab\n"
            f"Periode: {period_label}\n\n"
            f"Indberettet: {submitted_count} ud af {total_count} medarbejdere\n\n"
            f"{summary_df.drop(columns=['Email']).to_string(index=False)}\n\n"
            f"Se admin-interfacet her: {app_url}/?admin=true"
        )
        if send_email(admin_email, subject, body, smtp_config):
            print(f"Opsummering sendt til {admin_email}")
        else:
            print("Kunne ikke sende opsummering til admin")

if __name__ == "__main__":
    main()
