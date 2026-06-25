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

def build_summary_html(period_label, summary_df, app_url=''):
    submitted_count = (summary_df['Indberettet'] == 'Ja').sum()
    total_count = len(summary_df)
    df = summary_df.drop(columns=['Email'], errors='ignore')
    cols = [c for c in df.columns if c not in ('Medarbejder', 'Indberettet')]
    header_cells = ''.join(f'<th style="padding:10px 12px;text-align:center;">{c}</th>' for c in cols)
    rows_html = ''
    for _, row in df.iterrows():
        submitted = row['Indberettet'] == 'Ja'
        badge = '<span style="color:#34c759;font-size:15px;">✔</span> Ja' if submitted else '<span style="color:#ff3b30;font-size:15px;">✘</span> Nej'
        bg = '#ffffff' if submitted else '#fff8f8'
        data_cells = ''.join(f'<td style="text-align:center;padding:9px 12px;">{row[c]}</td>' for c in cols)
        rows_html += f'''
        <tr style="background:{bg};border-bottom:1px solid #e8e8ed;">
            <td style="font-weight:600;padding:9px 12px;">{row["Medarbejder"]}</td>
            <td style="text-align:center;padding:9px 12px;">{badge}</td>
            {data_cells}
        </tr>'''
    admin_link = f'<p style="text-align:center;margin-top:16px;"><a href="{app_url}/?admin=true" style="color:#0071e3;">Åbn admin-interfacet</a></p>' if app_url else ''
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f5f7;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f7;padding:32px 0;">
<tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%;">

  <tr><td style="background:linear-gradient(135deg,#0071e3,#34aadc);border-radius:16px 16px 0 0;padding:28px 32px;">
    <div style="font-size:22px;font-weight:700;color:#fff;margin-bottom:4px;">📊 Timeregnskab</div>
    <div style="font-size:14px;color:rgba(255,255,255,0.85);">Periode: {period_label}</div>
  </td></tr>

  <tr><td style="background:#fff;padding:20px 32px 16px;">
    <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td width="50%" style="padding:12px 16px;background:#f0faf4;border-radius:10px;text-align:center;">
        <div style="font-size:30px;font-weight:700;color:#34c759;">{submitted_count}</div>
        <div style="font-size:12px;color:#6e6e73;margin-top:2px;">Har indberettet</div>
      </td>
      <td width="8px"></td>
      <td width="50%" style="padding:12px 16px;background:#fff8f8;border-radius:10px;text-align:center;">
        <div style="font-size:30px;font-weight:700;color:#ff3b30;">{total_count - submitted_count}</div>
        <div style="font-size:12px;color:#6e6e73;margin-top:2px;">Har ikke indberettet</div>
      </td>
    </tr>
    </table>
  </td></tr>

  <tr><td style="background:#fff;padding:0 32px 28px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:13px;border:1px solid #e8e8ed;border-radius:10px;overflow:hidden;">
      <thead>
        <tr style="background:#0071e3;color:#fff;">
          <th style="text-align:left;padding:10px 12px;">Medarbejder</th>
          <th style="text-align:center;padding:10px 12px;">Status</th>
          {header_cells}
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    {admin_link}
  </td></tr>

  <tr><td style="background:#f5f5f7;border-radius:0 0 16px 16px;padding:14px 32px;text-align:center;">
    <div style="font-size:11px;color:#6e6e73;">Automatisk genereret af Timeregnskab · {period_label}</div>
  </td></tr>

</table>
</td></tr></table>
</body></html>'''


def send_email(to_email, subject, plain_body, smtp_config, html_body=None):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_config['username']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(plain_body, 'plain', 'utf-8'))
        if html_body:
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        port = int(smtp_config['port'])
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_config['server'], port)
            server.ehlo()
        else:
            server = smtplib.SMTP(smtp_config['server'], port)
            server.ehlo()
            server.starttls()
            server.ehlo()
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)
        try:
            server.quit()
        except Exception:
            pass
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

    app_url = config.get('app_url', '').rstrip('/') or os.getenv("APP_URL", "").rstrip('/')

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

    content = repo.get_contents("employees.csv")
    import base64
    csv_content = base64.b64decode(content.content).decode('utf-8')
    from io import StringIO
    df = pd.read_csv(StringIO(csv_content))

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

    summary_path = f"summary/{month_key}.csv"
    csv_content_out = summary_df.to_csv(index=False)
    try:
        file = repo.get_contents(summary_path)
        repo.update_file(summary_path, f"Opdateret summary {month_key}", csv_content_out, file.sha)
    except:
        repo.create_file(summary_path, f"Oprettet summary {month_key}", csv_content_out)
    print(f"Summary gemt: {summary_path}")

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
            repo.create_file(f"{backup_path}/{emp['Name']}.json", f"Arkiveret {month_key}/{emp['Name']}", file_content)
            repo.delete_file(submission_path, f"Slettet efter arkivering {submission_path}", content.sha)
            print(f"Arkiveret: {emp['Name']}")
        except:
            pass
    print(f"Arkivering fuldført for {month_key}")

    if admin_email and all([smtp_config['username'], smtp_config['password']]):
        subject = f"Timeregnskab – {period_label}"
        plain = (
            f"Timeregnskab — Periode: {period_label}\n"
            f"Indberettet: {submitted_count} ud af {total_count}\n\n"
            f"{summary_df.drop(columns=['Email'], errors='ignore').to_string(index=False)}"
        )
        html = build_summary_html(period_label, summary_df, app_url)
        if send_email(admin_email, subject, plain, smtp_config, html_body=html):
            print(f"Opsummering sendt til {admin_email}")
        else:
            print("Kunne ikke sende opsummering til admin")

if __name__ == "__main__":
    main()
