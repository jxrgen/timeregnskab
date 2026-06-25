import streamlit as st
import pandas as pd
import os
from github import Github
import json
from datetime import datetime
import secrets
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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


# ─────────────────────────────────────────────────────
# CSS + HTML guides
# ─────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif !important;
    }
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }
    .stApp { background-color: #f5f5f7; }
    .main .block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 880px; }
    h1 { font-weight: 700; letter-spacing: -0.6px; color: #1d1d1f; font-size: 2rem; }
    h2 { font-weight: 600; letter-spacing: -0.3px; color: #1d1d1f; }
    h3 { font-weight: 600; letter-spacing: -0.2px; color: #1d1d1f; }
    .stButton > button, .stFormSubmitButton > button {
        background-color: #0071e3 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 980px !important;
        padding: 8px 22px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        letter-spacing: -0.1px !important;
        transition: background-color 0.15s ease !important;
        box-shadow: none !important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background-color: #0077ed !important;
        color: #ffffff !important;
        border: none !important;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInputContainer"] input,
    .stTextArea textarea,
    input[type="password"] {
        border-radius: 8px !important;
        border: 1.5px solid #d2d2d7 !important;
        background-color: #ffffff !important;
        color: #1d1d1f !important;
        font-size: 15px !important;
        padding: 8px 12px !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInputContainer"] input:focus,
    .stTextArea textarea:focus,
    input[type="password"]:focus {
        border-color: #0071e3 !important;
        box-shadow: 0 0 0 3px rgba(0,113,227,0.12) !important;
        outline: none !important;
    }
    [data-baseweb="select"] > div {
        border-radius: 8px !important;
        border: 1.5px solid #d2d2d7 !important;
        background-color: #ffffff !important;
    }
    [data-testid="stAlert"] { border-radius: 12px !important; border: none !important; }
    [data-testid="stExpander"] {
        background-color: #ffffff;
        border: 1px solid #e8e8ed !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #e8e8ed;
        border-radius: 10px;
        padding: 3px;
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        font-size: 13.5px;
        font-weight: 500;
        color: #6e6e73;
        border: none !important;
        padding: 6px 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1d1d1f !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid #e8e8ed !important;
    }
    hr { border-color: #e8e8ed !important; margin: 2rem 0 !important; }
    .stCheckbox label p { font-size: 15px !important; color: #1d1d1f !important; }
    [data-testid="stNumberInputContainer"] button {
        border-radius: 6px !important;
        background-color: #e8e8ed !important;
        color: #1d1d1f !important;
        padding: 4px 10px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        border: none !important;
    }
    [data-testid="stNumberInputContainer"] button:hover { background-color: #d2d2d7 !important; }
    </style>
    """, unsafe_allow_html=True)


def get_admin_guide_html():
    return f"""
<style>
.ag {{
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
    color: #1d1d1f;
    line-height: 1.6;
}}
.ag-hero {{
    background: linear-gradient(135deg, #0071e3 0%, #34aadc 100%);
    color: white;
    padding: 36px 32px;
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 8px 30px rgba(0,113,227,0.28);
}}
.ag-hero h1 {{
    margin: 0 0 8px 0;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: white;
}}
.ag-hero p {{
    margin: 0;
    font-size: 15px;
    color: rgba(255,255,255,0.88);
}}
.ag-section {{
    background: #ffffff;
    border: 1px solid #e8e8ed;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}}
.ag-section h2 {{
    margin: 0 0 14px 0;
    font-size: 1.15rem;
    font-weight: 600;
    color: #1d1d1f;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0f5;
}}
.ag-section h3 {{
    font-size: 0.95rem;
    font-weight: 600;
    color: #1d1d1f;
    margin: 18px 0 8px 0;
}}
.ag-section p, .ag-section li {{
    color: #3a3a3c;
    font-size: 14.5px;
    line-height: 1.65;
    margin: 0 0 6px 0;
}}
.ag-section ul {{ padding-left: 20px; margin: 8px 0; }}
.ag-section li {{ margin-bottom: 6px; }}
.ag-timeline {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 4px 0 16px 0;
}}
.ag-titem {{
    flex: 1;
    min-width: 150px;
    border-radius: 12px;
    padding: 14px 16px;
    border-left: 4px solid #d2d2d7;
    background: #f5f5f7;
}}
.ag-titem.reminder {{ border-left-color: #ff9500; background: #fff8f0; }}
.ag-titem.deadline {{ border-left-color: #ff3b30; background: #fff2f2; }}
.ag-titem.collect  {{ border-left-color: #34c759; background: #f0faf4; }}
.ag-tdate {{ font-size: 19px; font-weight: 700; color: #1d1d1f; margin-bottom: 3px; }}
.ag-ttitle {{ font-size: 13px; font-weight: 600; color: #1d1d1f; margin-bottom: 4px; }}
.ag-tdesc {{ font-size: 12.5px; color: #6e6e73; line-height: 1.5; }}
.ag-steps {{ display: flex; flex-direction: column; gap: 8px; margin: 10px 0 0 0; }}
.ag-step {{
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 12px 16px;
    background: #f5f5f7;
    border-radius: 10px;
}}
.ag-step-num {{
    width: 26px; height: 26px; min-width: 26px;
    background: #0071e3; color: white;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 600;
}}
.ag-step-title {{ font-size: 14px; font-weight: 600; color: #1d1d1f; margin-bottom: 3px; }}
.ag-step-desc {{ font-size: 13px; color: #6e6e73; line-height: 1.5; margin: 0; }}
.ag-callout {{
    border-radius: 10px;
    padding: 12px 16px;
    margin: 12px 0 4px 0;
    font-size: 14px;
    line-height: 1.55;
    display: flex;
    align-items: flex-start;
    gap: 10px;
}}
.ag-callout.info    {{ background: #e8f4ff; border-left: 3px solid #0071e3; color: #0044a3; }}
.ag-callout.warning {{ background: #fff8e6; border-left: 3px solid #ff9500; color: #7a4500; }}
.ag-callout.danger  {{ background: #fff2f2; border-left: 3px solid #ff3b30; color: #8b0000; }}
.ag-callout.success {{ background: #f0faf4; border-left: 3px solid #34c759; color: #1a6b34; }}
.ag-table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; margin: 10px 0; }}
.ag-table th {{
    background: #f5f5f7;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    color: #1d1d1f;
    border-bottom: 1px solid #e8e8ed;
}}
.ag-table td {{
    padding: 10px 14px;
    color: #3a3a3c;
    border-bottom: 1px solid #f0f0f5;
    vertical-align: top;
}}
.ag-table tr:last-child td {{ border-bottom: none; }}
.ag-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 10px 0;
}}
.ag-card {{
    background: #f5f5f7;
    border-radius: 10px;
    padding: 14px 16px;
}}
.ag-card-title {{ font-size: 13.5px; font-weight: 600; color: #1d1d1f; margin-bottom: 5px; }}
.ag-card-desc {{ font-size: 13px; color: #6e6e73; line-height: 1.5; margin: 0; }}
code {{
    background: #f5f5f7;
    padding: 2px 6px;
    border-radius: 5px;
    font-size: 12.5px;
    color: #1d1d1f;
    font-family: "SF Mono", "Fira Code", monospace;
}}
</style>

<div class="ag">

<div class="ag-hero">
  <h1>📋 Vejledning til administratorer</h1>
  <p>Alt du behøver at vide om at administrere Timeregnskab-systemet</p>
</div>

<!-- OVERBLIK -->
<div class="ag-section">
  <h2>🏠 Hvad er Timeregnskab?</h2>
  <p>Timeregnskab er et system til månedlig indsamling af tidsregistreringer fra medarbejdere. Hver medarbejder har et personligt, unikt link — der kræves ingen kode eller login. Du som admin styrer hvem der er i systemet, hvilke felter de skal udfylde, og modtager automatisk en samlet oversigt hver måned.</p>
  <div class="ag-grid">
    <div class="ag-card">
      <div class="ag-card-title">👤 Medarbejdere</div>
      <p class="ag-card-desc">Tilgår systemet via et personligt link med et unikt token. Ingen kode, ingen login — bare linket.</p>
    </div>
    <div class="ag-card">
      <div class="ag-card-title">🔐 Admin</div>
      <p class="ag-card-desc">Tilgår admin-interfacet via <code>?admin=true</code> i URL'en + adgangskode.</p>
    </div>
    <div class="ag-card">
      <div class="ag-card-title">📁 Data</div>
      <p class="ag-card-desc">Alle indberetninger gemmes som JSON-filer i GitHub-repoet med fuld versionshistorik.</p>
    </div>
    <div class="ag-card">
      <div class="ag-card-title">📧 Automatisk email</div>
      <p class="ag-card-desc">Påmindelser d. {REMINDER_DAY}. og månedlig oversigt d. {AGGREGATE_DAY}. sendes automatisk via din SMTP-server.</p>
    </div>
  </div>
</div>

<!-- MÅNEDLIG CYKLUS -->
<div class="ag-section">
  <h2>📅 Månedlig cyklus</h2>
  <p>Registreringsperioden løber fra <strong>d. 21 i én måned til d. 20 i den næste</strong> — den strækker sig altså hen over to kalendermåneder. Herunder ses hvad der sker i løbet af én periode:</p>
  <div class="ag-timeline">
    <div class="ag-titem">
      <div class="ag-tdate">D. 21 ↗</div>
      <div class="ag-ttitle">Perioden åbner</div>
      <div class="ag-tdesc">Fra d. 21 i forrige måned kan medarbejderne begynde at registrere. De kan løbende udfylde, gemme og rette — helt frem til fristen d. {DEADLINE_DAY}. i næste måned.</div>
    </div>
    <div class="ag-titem reminder">
      <div class="ag-tdate">D. {REMINDER_DAY}.</div>
      <div class="ag-ttitle">🔔 Påmindelsesmail</div>
      <div class="ag-tdesc">Systemet sender automatisk en påmindelsesmail til <em>alle</em> aktive medarbejdere — uanset om de allerede har indberettet.</div>
    </div>
    <div class="ag-titem deadline">
      <div class="ag-tdate">D. {DEADLINE_DAY}.</div>
      <div class="ag-ttitle">⏰ Frist</div>
      <div class="ag-tdesc">Seneste indberetningsdato. Timer der ikke er indberettet inden midnat registreres ikke og medtages <strong>ikke</strong> i denne måneds opgørelse.</div>
    </div>
    <div class="ag-titem collect">
      <div class="ag-tdate">D. {AGGREGATE_DAY}.</div>
      <div class="ag-ttitle">📊 Opsamling</div>
      <div class="ag-tdesc">Du modtager automatisk en samlet tabel over alle medarbejderes registreringer. Ny registreringsperiode starter samme dag.</div>
    </div>
  </div>
  <div class="ag-callout info">
    <span>ℹ️</span>
    <div>Datoerne {REMINDER_DAY}, {DEADLINE_DAY} og {AGGREGATE_DAY} er faste og ændres ikke via interfacet — de er kodet direkte i systemet.</div>
  </div>
</div>

<!-- MEDARBEJDERE -->
<div class="ag-section">
  <h2>👥 Administrér medarbejdere</h2>

  <h3>Tilføj en ny medarbejder</h3>
  <div class="ag-steps">
    <div class="ag-step">
      <div class="ag-step-num">1</div>
      <div>
        <div class="ag-step-title">Gå til fanen "Tilføj ny"</div>
        <p class="ag-step-desc">Find den i toppen af admin-interfacet.</p>
      </div>
    </div>
    <div class="ag-step">
      <div class="ag-step-num">2</div>
      <div>
        <div class="ag-step-title">Udfyld navn og email</div>
        <p class="ag-step-desc">Brug medarbejderens fulde navn — det bruges som filnavn i systemet og må ikke ændres bagefter (medmindre du accepterer at historik knyttes til det gamle navn). Emailen bruges til påmindelser.</p>
      </div>
    </div>
    <div class="ag-step">
      <div class="ag-step-num">3</div>
      <div>
        <div class="ag-step-title">Vælg skemafelter</div>
        <p class="ag-step-desc">Marker kun de felter der er relevante for medarbejderen. Umarkerede felter vises slet ikke i medarbejderens formular.</p>
      </div>
    </div>
    <div class="ag-step">
      <div class="ag-step-num">4</div>
      <div>
        <div class="ag-step-title">Klik "Tilføj medarbejder"</div>
        <p class="ag-step-desc">Et unikt personligt link genereres automatisk og vises under fanen "Medarbejdere".</p>
      </div>
    </div>
    <div class="ag-step">
      <div class="ag-step-num">5</div>
      <div>
        <div class="ag-step-title">Send linket til medarbejderen</div>
        <p class="ag-step-desc">Kopiér linket og send det per email eller anden besked. Linket er permanent — medarbejderen kan bogmærke det og bruge det hver måned uden at logge ind.</p>
      </div>
    </div>
  </div>

  <h3>Skemafelter — hvad betyder de?</h3>
  <table class="ag-table">
    <tr><th>Felt</th><th>Hvad registreres</th><th>Typisk for</th></tr>
    <tr><td><strong>Feriedage</strong></td><td>Antal afholdte feriedage i perioden</td><td>Fastansatte</td></tr>
    <tr><td><strong>Feriefridag</strong></td><td>Særlige feriefridage (f.eks. 6. ferieuge)</td><td>Fastansatte</td></tr>
    <tr><td><strong>Sygedage</strong></td><td>Antal sygedage i perioden</td><td>Fastansatte</td></tr>
    <tr><td><strong>Ekstra Hverdag</strong></td><td>Ekstra timer arbejdet på hverdage</td><td>Timelønnet / overarbejde</td></tr>
    <tr><td><strong>Ekstra Lørdag</strong></td><td>Ekstra timer arbejdet på lørdage</td><td>Timelønnet / overarbejde</td></tr>
    <tr><td><strong>Ekstra Søndag</strong></td><td>Ekstra timer arbejdet på søndage</td><td>Timelønnet / overarbejde</td></tr>
    <tr><td><strong>Ekstra Andet</strong></td><td>Andre ekstra timer (helligdage mm.)</td><td>Timelønnet / overarbejde</td></tr>
    <tr><td><strong>Antal timer</strong></td><td>Samlet antal arbejdstimer i perioden</td><td>Timebaseret løn</td></tr>
  </table>

  <h3>Redigér en medarbejder</h3>
  <p>Under fanen <strong>"Medarbejdere"</strong> kan du klikke på en medarbejders ekspander og:</p>
  <ul>
    <li><strong>Gem ændringer</strong> — ret navn, email, aktiv-status eller hvilke felter de ser</li>
    <li><strong>Ny token</strong> — genererer et nyt unikt link. Det gamle link virker ikke længere. Brug dette hvis medarbejderen har mistet sit link eller af sikkerhedshensyn</li>
    <li><strong>Slet</strong> — fjerner medarbejderen fra systemet permanent. Tidligere indberetninger slettes ikke, men de modtager ikke fremtidige påmindelser og vises ikke i oversigter</li>
    <li><strong>Inaktiv</strong> — en mere skånsom løsning end sletning: medarbejderen ses i systemet men modtager ingen påmindelser og tæller ikke med i opsamlingen</li>
  </ul>
  <div class="ag-callout warning">
    <span>⚠️</span>
    <div><strong>"Ny token"</strong> ugyldiggør øjeblikkeligt det gamle link. Send altid det nye link til medarbejderen bagefter — ellers kan de ikke tilgå systemet.</div>
  </div>
</div>

<!-- INDSENDELSER -->
<div class="ag-section">
  <h2>📋 Se indsendelser</h2>
  <p>Under fanen <strong>"Indsendelser"</strong> kan du tjekke hvem der har indberettet for en given periode.</p>
  <ul>
    <li>Vælg perioden (de 3 seneste vises) i dropdownmenuen øverst</li>
    <li><strong style="color: #2e7d32;">✅ Udfyldt</strong> — medarbejderen har sat hak i "Marker her for at indberette" og klikket Indsend</li>
    <li><strong style="color: #c62828;">❌ Mangler</strong> — ingen indberetning er modtaget, eller medarbejderen har gemt tal men ikke afkrydset og indsendt</li>
  </ul>
  <div class="ag-callout info">
    <span>ℹ️</span>
    <div>En medarbejder der har <em>gemt</em> tal men ikke afkrydset "Marker her for at indberette" og trykket <em>Indsend</em> tæller som <strong>Mangler</strong>. Data er gemt men ikke bekræftet.</div>
  </div>
</div>

<!-- FÆLLES BESKED -->
<div class="ag-section">
  <h2>✉️ Send en fælles besked</h2>
  <p>Fanen <strong>"Fælles besked"</strong> giver dig mulighed for at sende en ad hoc-email til udvalgte medarbejdere — f.eks. en ekstra påminding, en rettelse eller en vigtig meddelelse.</p>
  <div class="ag-steps">
    <div class="ag-step">
      <div class="ag-step-num">1</div>
      <div>
        <div class="ag-step-title">Vælg modtagere</div>
        <p class="ag-step-desc">Sæt hak ud for de medarbejdere du vil skrive til. Kun aktive medarbejdere vises.</p>
      </div>
    </div>
    <div class="ag-step">
      <div class="ag-step-num">2</div>
      <div>
        <div class="ag-step-title">Skriv din besked</div>
        <p class="ag-step-desc">Beskeden indsættes i en email med medarbejderens fornavn i hilsenen. Hold beskeden kort og konkret.</p>
      </div>
    </div>
    <div class="ag-step">
      <div class="ag-step-num">3</div>
      <div>
        <div class="ag-step-title">Klik "Send fælles besked"</div>
        <p class="ag-step-desc">Systemet sender en individuel email til hver valgt medarbejder med det samme.</p>
      </div>
    </div>
  </div>
</div>

<!-- SIMULER -->
<div class="ag-section">
  <h2>🧪 Simuler indsendelse</h2>
  <p>Fanen <strong>"Simuler"</strong> lader dig manuelt sende den månedlige opsamlingsemail til admin-emailen — uanset hvilken dato det er i dag.</p>
  <p>Brug det til at:</p>
  <ul>
    <li>Teste at SMTP-opsætningen virker korrekt</li>
    <li>Hente et øjebliksbillede midt i måneden (hvem har indberettet så langt?)</li>
    <li>Manuelt indhente data uden at vente på d. {AGGREGATE_DAY}.</li>
  </ul>
  <p>Du kan se en forhåndsvisning af tabellen direkte i interfacet, inden emailen sendes.</p>
  <div class="ag-callout success">
    <span>✅</span>
    <div>Simulering arkiverer <em>ikke</em> data og sletter <em>ikke</em> indberetninger — det er udelukkende en email til dig.</div>
  </div>
</div>

<!-- SMTP -->
<div class="ag-section">
  <h2>⚙️ SMTP-indstillinger</h2>
  <p>For at systemet kan sende emails, kræves en SMTP-mailserver. Indstillingerne gemmes i systemet og bruges af både det automatiske flow og admin-interfacet.</p>
  <table class="ag-table">
    <tr><th>Felt</th><th>Beskrivelse</th><th>Eksempel (one.com)</th></tr>
    <tr><td><strong>SMTP Server</strong></td><td>Mailserverens adresse</td><td><code>send.one.com</code></td></tr>
    <tr><td><strong>SMTP Port</strong></td><td>587 = STARTTLS &nbsp;|&nbsp; 465 = SSL/TLS</td><td><code>465</code></td></tr>
    <tr><td><strong>SMTP Brugernavn</strong></td><td>Din fulde email-adresse</td><td><code>timereg@firma.dk</code></td></tr>
    <tr><td><strong>SMTP Password</strong></td><td>Adgangskoden til emailkontoen</td><td>—</td></tr>
    <tr><td><strong>Admin Email</strong></td><td>Hvem der modtager den månedlige oversigt</td><td><code>admin@firma.dk</code></td></tr>
  </table>
  <div class="ag-steps">
    <div class="ag-step">
      <div class="ag-step-num">1</div>
      <div>
        <div class="ag-step-title">Udfyld alle felter og klik "Gem SMTP-indstillinger"</div>
        <p class="ag-step-desc">Indstillingerne gemmes i systemets konfigurationsfil på GitHub.</p>
      </div>
    </div>
    <div class="ag-step">
      <div class="ag-step-num">2</div>
      <div>
        <div class="ag-step-title">Klik "Send test-email" og bekræft</div>
        <p class="ag-step-desc">En test-email sendes til admin-emailen. Tjek din indbakke og eventuelt spam-mappen.</p>
      </div>
    </div>
  </div>
  <div class="ag-callout warning">
    <span>⚠️</span>
    <div>Gem altid SMTP-indstillingerne <em>før</em> du sender en test-email, da test-emailen bruger de aktuelle formularværdier — ikke de gemte.</div>
  </div>
</div>

<!-- HVAD MODTAGER ADMIN -->
<div class="ag-section">
  <h2>📬 Den månedlige opsamlingsemail</h2>
  <p>Den {AGGREGATE_DAY}. i måneden modtager du automatisk en email med en samlet tabel over alle aktive medarbejderes registreringer for den netop afsluttede periode. Tabellen indeholder:</p>
  <ul>
    <li>Medarbejderens navn</li>
    <li>Om de har indberettet (<strong>Ja</strong> = afkrydset og indsendt / <strong>Nej</strong> = ingen bekræftet indberetning)</li>
    <li>Alle registrerede værdier: feriedage, sygedage, ekstra timer osv.</li>
    <li>Medarbejdere der ikke har indberettet vises med <strong>Nej</strong> og tomme felter</li>
  </ul>
  <div class="ag-callout danger">
    <span>🚨</span>
    <div>Data fra medarbejdere der <em>ikke</em> har indberettet inden d. {DEADLINE_DAY}. medtages <strong>ikke</strong> i opgørelsen og <strong>overføres ikke</strong> automatisk til næste periode.</div>
  </div>
  <p style="margin-top: 12px;">En kopi af oversigten gemmes også som CSV-fil i GitHub-repoet under <code>summary/YYYY-MM.csv</code>.</p>
</div>

<!-- TIPS -->
<div class="ag-section">
  <h2>💡 Praktiske tips</h2>
  <div class="ag-grid">
    <div class="ag-card">
      <div class="ag-card-title">🔗 Links er permanente</div>
      <p class="ag-card-desc">Medarbejdernes links ændrer sig kun hvis du klikker "Ny token". De kan bogmærke linket og bruge det månedligt.</p>
    </div>
    <div class="ag-card" style="border-left: 3px solid #ff9500;">
      <div class="ag-card-title">⚠️ Ændr ikke token uden besked</div>
      <p class="ag-card-desc">Klikker du "Ny token", <strong>mister medarbejderen adgang via sit gamle link</strong>. Husk altid at sende det nye link til medarbejderen med det samme.</p>
    </div>
    <div class="ag-card" style="border-left: 3px solid #ff9500;">
      <div class="ag-card-title">📬 Tjek spammappen</div>
      <p class="ag-card-desc">Automatiske mails fra systemet kan ende i spam- eller junk-mappen. Bed medarbejderne om at tilføje systemets emailadresse til deres kontakter, og tjek selv at admin-mailen d. {AGGREGATE_DAY}. ikke ender i spam.</p>
    </div>
    <div class="ag-card">
      <div class="ag-card-title">🔄 Kan genindsendes</div>
      <p class="ag-card-desc">Medarbejdere kan rette og genindsende inden d. {DEADLINE_DAY}. Det seneste Indsend overskriver det forrige.</p>
    </div>
    <div class="ag-card">
      <div class="ag-card-title">📱 Mobilvenligt</div>
      <p class="ag-card-desc">Medarbejderformularen virker på alle enheder — telefon, tablet og computer.</p>
    </div>
    <div class="ag-card">
      <div class="ag-card-title">📦 Automatisk arkiv</div>
      <p class="ag-card-desc">Når data opsamles d. {AGGREGATE_DAY}. flyttes indberetningerne automatisk til <code>archive/</code> i GitHub. Historik bevares.</p>
    </div>
    <div class="ag-card">
      <div class="ag-card-title">👁️ Inaktive medarbejdere</div>
      <p class="ag-card-desc">Sæt en medarbejder til "Inaktiv" frem for at slette — de modtager ingen påmindelser, men data og link bevares.</p>
    </div>
    <div class="ag-card">
      <div class="ag-card-title">🧪 Test månedligt flow</div>
      <p class="ag-card-desc">Brug "Simuler"-fanen til at teste hele emailflowet og se hvem der pt. har indberettet.</p>
    </div>
  </div>
</div>

</div>
"""


def get_employee_guide_html(period_label, reminder_day, deadline_day):
    return f"""
<style>
.eg {{
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
    color: #1d1d1f;
    line-height: 1.6;
}}
.eg-section {{
    margin-bottom: 14px;
}}
.eg-section h3 {{
    font-size: 15px;
    font-weight: 600;
    color: #1d1d1f;
    margin: 0 0 6px 0;
}}
.eg-section p, .eg-section li {{
    font-size: 14px;
    color: #3a3a3c;
    line-height: 1.65;
    margin: 0 0 4px 0;
}}
.eg-section ul {{ padding-left: 18px; margin: 6px 0; }}
.eg-section li {{ margin-bottom: 5px; }}
.eg-dates {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 10px 0;
}}
.eg-date {{
    flex: 1;
    min-width: 120px;
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
}}
.eg-date.reminder {{ background: #fff8f0; border: 1.5px solid #ff9500; }}
.eg-date.deadline {{ background: #fff2f2; border: 1.5px solid #ff3b30; }}
.eg-date.collect  {{ background: #f0faf4; border: 1.5px solid #34c759; }}
.eg-date-num {{ font-size: 22px; font-weight: 700; color: #1d1d1f; }}
.eg-date-label {{ font-size: 12px; color: #6e6e73; margin-top: 2px; }}
.eg-callout {{
    border-radius: 9px;
    padding: 10px 14px;
    margin: 10px 0;
    font-size: 13.5px;
    line-height: 1.55;
    border-left: 3px solid;
    display: flex;
    gap: 8px;
    align-items: flex-start;
}}
.eg-callout.info    {{ background: #e8f4ff; border-color: #0071e3; color: #0044a3; }}
.eg-callout.danger  {{ background: #fff2f2; border-color: #ff3b30; color: #8b0000; }}
</style>
<div class="eg">

  <div class="eg-section">
    <h3>Hvad skal jeg gøre?</h3>
    <ul>
      <li>Udfyld felterne med dine registreringer for den aktuelle periode: <strong>{period_label}</strong></li>
      <li>Sæt hak i "Marker her for at indberette" i bunden af siden</li>
      <li>Klik <strong>Indsend</strong> for at sende din registrering</li>
    </ul>
    <div class="eg-callout info">
      <span>💾</span>
      <div>Du kan klikke <strong>Indsend</strong> flere gange — f.eks. hvis du vil rette et tal. Det seneste indsend erstatter det forrige.</div>
    </div>
  </div>

  <div class="eg-section">
    <h3>Vigtige datoer hver måned</h3>
    <div class="eg-dates">
      <div class="eg-date reminder">
        <div class="eg-date-num">D. {reminder_day}.</div>
        <div class="eg-date-label">Du modtager en påmindelsesmail</div>
      </div>
      <div class="eg-date deadline">
        <div class="eg-date-num">D. {deadline_day}.</div>
        <div class="eg-date-label">Seneste frist for indberetning</div>
      </div>
    </div>
    <div class="eg-callout danger">
      <span>⚠️</span>
      <div><strong>Mangler du at indsende inden d. {deadline_day}.?</strong> Dine timer registreres ikke og medtages <strong>ikke</strong> i denne måneds opgørelse. Kontakt din administrator.</div>
    </div>
    <div class="eg-callout info">
      <span>📬</span>
      <div>Modtager du ikke påmindelsesmailen d. {reminder_day}.? <strong>Tjek din spammappe</strong> — mails fra systemet kan nogle gange havne der. Tilføj systemets emailadresse til dine kontakter for at undgå det fremover.</div>
    </div>
  </div>

  <div class="eg-section">
    <h3>Hvad betyder felterne?</h3>
    <ul>
      <li><strong>Feriedage / Feriefridage</strong> — dage du har holdt fri med ferie</li>
      <li><strong>Sygedage</strong> — dage du var sygemeldt</li>
      <li><strong>Ekstra timer</strong> — timer du har arbejdet ud over din normale arbejdstid</li>
      <li><strong>Antal timer</strong> — det samlede antal timer du har arbejdet i perioden</li>
    </ul>
    <p>Du ser kun de felter der er relevante for dig — andre felter vises ikke.</p>
  </div>

</div>
"""


# ─────────────────────────────────────────────────────
# GitHub helpers
# ─────────────────────────────────────────────────────

def get_github_client():
    if 'gh_client' not in st.session_state:
        token = None
        try:
            token = st.secrets["GITHUB_TOKEN"]
        except:
            token = os.getenv("GITHUB_TOKEN")
        if not token:
            st.error("GitHub token ikke konfigureret")
            return None
        st.session_state['gh_client'] = Github(token)
    return st.session_state['gh_client']


def load_employees():
    if 'employees_df' not in st.session_state:
        try:
            g = get_github_client()
            if g:
                repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
                content = repo.get_contents(EMPLOYEES_FILE)
                import base64
                csv_content = base64.b64decode(content.content).decode('utf-8')
                from io import StringIO
                st.session_state['employees_df'] = pd.read_csv(StringIO(csv_content))
            else:
                st.error("Ingen GitHub forbindelse")
                st.session_state['employees_df'] = pd.DataFrame()
        except Exception as e:
            st.error(f"Kunne ikke indlæse medarbejdere: {str(e)}")
            st.session_state['employees_df'] = pd.DataFrame()
    return st.session_state['employees_df']


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
            st.session_state['employees_df'] = df.reset_index(drop=True)
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
        st.error(f"Kunne ikke gemme: {str(e)}")
        return False
    return False


def generate_token():
    return secrets.token_urlsafe(16)


def is_valid_email(email):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email.strip()))


def load_config():
    if 'config_data' not in st.session_state:
        try:
            g = get_github_client()
            if g:
                repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
                content = repo.get_contents("config.json")
                import base64
                st.session_state['config_data'] = json.loads(base64.b64decode(content.content).decode('utf-8'))
        except:
            pass
        if 'config_data' not in st.session_state:
            st.session_state['config_data'] = {}
    return st.session_state['config_data']


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
            st.session_state['config_data'] = config
            return True
    except Exception as e:
        st.error(f"Kunne ikke gemme konfiguration: {str(e)}")
    return False


# ─────────────────────────────────────────────────────
# Date / period helpers
# ─────────────────────────────────────────────────────

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
    Period_key er slutmåneden (B), brugt som mappenavn under submissions/.
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


# ─────────────────────────────────────────────────────
# Email helper
# ─────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────
# Admin interface
# ─────────────────────────────────────────────────────

def admin_interface():
    st.title("Timeregnskab — Admin")

    if not st.session_state.get('admin_ok', False):
        admin_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
        password = st.text_input("Adgangskode", type="password")
        if password == admin_password:
            st.session_state['admin_ok'] = True
            st.rerun()
        elif password:
            st.error("Forkert adgangskode")
        return

    st.success("Logget ind")
    if _toast := st.session_state.pop('_toast', None):
        st.toast(_toast)

    st.markdown(f"""
    <div style="
        background:#ffffff;border:1px solid #e8e8ed;border-radius:14px;
        padding:20px 24px;margin:16px 0 24px 0;
        box-shadow:0 1px 6px rgba(0,0,0,0.05);
        font-size:15px;color:#1d1d1f;line-height:1.75;
    ">
        <strong>Registreringsperiode:</strong> Fra d. 21 til d. 20 i den følgende måned.<br>
        <strong>Påmindelser:</strong> Sendes automatisk d. {REMINDER_DAY}. til alle aktive medarbejdere.<br>
        <strong>Frist:</strong> Den {DEADLINE_DAY}. — timer der ikke er indberettet inden fristen medtages ikke og registreres først i næste måned.<br>
        <strong>Opsamling:</strong> Den {AGGREGATE_DAY}. modtager du en samlet tabel med alle medarbejderes registreringer.
    </div>
    """, unsafe_allow_html=True)

    df = load_employees()
    if df.empty:
        st.warning("Kunne ikke indlæse medarbejdere")
        return

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Medarbejdere", "Tilføj ny", "Indsendelser",
        "Fælles besked", "Systeminfo", "Simuler", "Vejledning"
    ])

    with tab1:
        st.subheader("Eksisterende medarbejdere")
        for idx, row in df.iterrows():
            with st.expander(f"{row['Name']} ({row['Email']})"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name   = st.text_input("Navn",  value=row['Name'],  key=f"name_{idx}")
                    new_email  = st.text_input("Email", value=row['Email'], key=f"email_{idx}")
                    new_active = st.checkbox("Aktiv",   value=row['Active'], key=f"active_{idx}")
                with col2:
                    st.write("**Skema type:**")
                    feriedage     = st.checkbox("Feriedage",    value=row['Feriedage'],    key=f"feriedage_{idx}")
                    feriefridag   = st.checkbox("Feriefridag",  value=row['Feriefridag'],  key=f"feriefridag_{idx}")
                    sygedage      = st.checkbox("Sygedage",     value=row['Sygedage'],     key=f"sygedage_{idx}")
                    ekstra_hverdag = st.checkbox("Ekstra Hverdag", value=row['Ekstra_Hverdag'], key=f"hverdag_{idx}")
                    ekstra_lørdag  = st.checkbox("Ekstra Lørdag",  value=row['Ekstra_Lørdag'],  key=f"lørdag_{idx}")
                    ekstra_søndag  = st.checkbox("Ekstra Søndag",  value=row['Ekstra_Søndag'],  key=f"søndag_{idx}")
                    ekstra_andet   = st.checkbox("Ekstra Andet",   value=row['Ekstra_Andet'],   key=f"andet_{idx}")
                    antal_timer    = st.checkbox("Antal timer",    value=row['Antal_timer'],    key=f"timer_{idx}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Gem ændringer", key=f"save_{idx}"):
                        if not is_valid_email(new_email):
                            st.error("Ugyldig emailadresse")
                        else:
                            updated = df.copy()
                            updated.at[idx, 'Name'] = new_name
                            updated.at[idx, 'Email'] = new_email
                            updated.at[idx, 'Active'] = new_active
                            updated.at[idx, 'Feriedage'] = feriedage
                            updated.at[idx, 'Feriefridag'] = feriefridag
                            updated.at[idx, 'Sygedage'] = sygedage
                            updated.at[idx, 'Ekstra_Hverdag'] = ekstra_hverdag
                            updated.at[idx, 'Ekstra_Lørdag'] = ekstra_lørdag
                            updated.at[idx, 'Ekstra_Søndag'] = ekstra_søndag
                            updated.at[idx, 'Ekstra_Andet'] = ekstra_andet
                            updated.at[idx, 'Antal_timer'] = antal_timer
                            with st.spinner("Gemmer..."):
                                success = save_employees(updated)
                            if success:
                                st.session_state['_toast'] = f"✅ {new_name} gemt"
                                st.rerun()
                with col2:
                    if st.button("Ny token", key=f"token_{idx}"):
                        updated = df.copy()
                        updated.at[idx, 'Token'] = generate_token()
                        with st.spinner("Genererer token..."):
                            success = save_employees(updated)
                        if success:
                            st.session_state['_toast'] = f"✅ Nyt link genereret til {row['Name']}"
                            st.rerun()
                with col3:
                    if st.button("Slet", key=f"delete_{idx}", type="secondary"):
                        st.session_state['_confirm_delete'] = idx
                        st.rerun()

                if st.session_state.get('_confirm_delete') == idx:
                    st.warning(f"Er du sikker på, at du vil slette **{row['Name']}**? Dette kan ikke fortrydes.")
                    cy, cn = st.columns(2)
                    with cy:
                        if st.button("Ja", key=f"confirm_yes_{idx}"):
                            new_df = df.drop(idx).reset_index(drop=True)
                            with st.spinner("Sletter..."):
                                success = save_employees(new_df)
                            st.session_state.pop('_confirm_delete', None)
                            if success:
                                st.session_state['_toast'] = f"✅ {row['Name']} er slettet"
                            st.rerun()
                    with cn:
                        if st.button("Nej", key=f"confirm_no_{idx}"):
                            st.session_state.pop('_confirm_delete', None)
                            st.rerun()

                token = row['Token']
                app_url = st.secrets.get("APP_URL", "https://your-app.streamlit.app")
                st.code(f"{app_url}/?token={token}")

    with tab2:
        st.subheader("Tilføj ny medarbejder")
        form_id = st.session_state.get('_form_id', 0)
        with st.form(f"new_employee_{form_id}"):
            name  = st.text_input("Navn")
            email = st.text_input("Email")
            st.write("**Skema type:**")
            col1, col2 = st.columns(2)
            with col1:
                feriedage   = st.checkbox("Feriedage",   value=True)
                feriefridag = st.checkbox("Feriefridag", value=True)
                sygedage    = st.checkbox("Sygedage",    value=True)
            with col2:
                ekstra_hverdag = st.checkbox("Ekstra Hverdag")
                ekstra_lørdag  = st.checkbox("Ekstra Lørdag")
                ekstra_søndag  = st.checkbox("Ekstra Søndag")
                ekstra_andet   = st.checkbox("Ekstra Andet")
                antal_timer    = st.checkbox("Antal timer")
            submitted = st.form_submit_button("Tilføj medarbejder")
            if submitted:
                if not name or not email:
                    st.warning("Udfyld venligst navn og email")
                elif not is_valid_email(email):
                    st.error("Ugyldig emailadresse — tjek formatet (fx navn@firma.dk)")
                else:
                    new_row = pd.DataFrame([{
                        'Name': name, 'Email': email, 'Active': True,
                        'Feriedage': feriedage, 'Feriefridag': feriefridag, 'Sygedage': sygedage,
                        'Ekstra_Hverdag': ekstra_hverdag, 'Ekstra_Lørdag': ekstra_lørdag,
                        'Ekstra_Søndag': ekstra_søndag, 'Ekstra_Andet': ekstra_andet,
                        'Antal_timer': antal_timer, 'Token': generate_token()
                    }])
                    new_df = pd.concat([df, new_row], ignore_index=True)
                    with st.spinner("Opretter medarbejder..."):
                        success = save_employees(new_df)
                    if success:
                        st.session_state['_form_id'] = form_id + 1
                        st.session_state['_toast'] = f"✅ {name} er tilføjet!"
                        st.rerun()

    with tab3:
        st.subheader("Indsendelser")
        period_key, period_label = get_current_period()
        prev_key      = get_previous_month(period_key)
        prev_prev_key = get_previous_month(prev_key)
        months_options = [period_key, prev_key, prev_prev_key]
        month_labels   = [f"{format_month_danish(m)} (periode slut)" for m in months_options]
        selected_idx   = st.selectbox("Vælg periode", range(len(month_labels)),
                                       format_func=lambda i: month_labels[i])
        month = months_options[selected_idx]
        col_refresh, _ = st.columns([1, 4])
        with col_refresh:
            if st.button("🔄 Opdater", key="refresh_submissions", help="Hent seneste status fra GitHub"):
                st.rerun()
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
                    sent_count = error_count = 0
                    for emp in selected:
                        try:
                            body = f"Hej {emp['Name']},\n\n{message}\n\nVenlig hilsen,\nAdministrationen"
                            send_email_smtp(emp['Email'], "Besked fra Timeregnskab", body, config)
                            sent_count += 1
                        except Exception as e:
                            st.error(f"Kunne ikke sende til {emp['Name']}: {str(e)}")
                            error_count += 1
                    if sent_count:
                        st.success(f"✅ Besked sendt til {sent_count} medarbejder(e)!")
                    if error_count:
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
        pw = config.get('smtp_password', '')
        st.write(f"**SMTP Password:** {'*' * len(pw) if pw else 'Ikke sat'}")
        st.write(f"**Admin Email:** {config.get('admin_email', 'Ikke sat')}")
        st.markdown("### Medarbejdere")
        for _, row in df.iterrows():
            with st.expander(f"{row['Name']} ({'Aktiv' if row['Active'] else 'Inaktiv'})"):
                st.write(f"**Email:** {row['Email']}")
                st.write(f"**Token:** `{row['Token']}`")
                params = [label for col, label in [
                    ('Feriedage','Feriedage'), ('Feriefridag','Feriefridag'),
                    ('Sygedage','Sygedage'), ('Ekstra_Hverdag','Ekstra Hverdag'),
                    ('Ekstra_Lørdag','Ekstra Lørdag'), ('Ekstra_Søndag','Ekstra Søndag'),
                    ('Ekstra_Andet','Ekstra Andet'), ('Antal_timer','Antal timer'),
                ] if row[col]]
                st.write(f"**Parametre:** {', '.join(params) if params else 'Ingen'}")
        st.markdown("### GitHub Actions")
        st.info("Workflows kører dagligt kl. 08:00 UTC og tjekker om dags dato matcher de faste datoer.")

    with tab6:
        st.subheader("Simuler indsendelse")
        period_key, period_label = get_current_period()
        st.info(f"📅 Aktuel periode: **{period_label}**")
        st.write("Klik for at sende en samlet opsummering til administratoren nu — uanset hvilken dato det er.")
        if st.button("Send opsummering til admin nu", type="primary", key="simulate_btn"):
            # Altid hent frisk config fra GitHub — bypass session state cache
            st.session_state.pop('config_data', None)
            config = load_config()
            admin_email = config.get('admin_email', '')
            missing = [k for k in ('smtp_server', 'smtp_username', 'smtp_password') if not config.get(k)]
            if not admin_email:
                st.error("Admin email ikke konfigureret — sæt den under SMTP-indstillinger nedenfor.")
            elif missing:
                st.error(f"SMTP-indstillinger mangler: {', '.join(missing)}")
            else:
                with st.spinner("Indsamler data og sender email..."):
                    summary_df = collect_period_data(df, period_key)
                    submitted_count = (summary_df['Indberettet'] == 'Ja').sum()
                    total_count = len(summary_df)
                    st.write("**Forhåndsvisning:**")
                    st.dataframe(summary_df)
                    subject = f"Timeregnskab – {period_label}"
                    body = (
                        f"Timeregnskab\nPeriode: {period_label}\n\n"
                        f"Indberettet: {submitted_count} ud af {total_count} medarbejdere\n\n"
                        f"{summary_df.to_string(index=False)}"
                    )
                    try:
                        send_email_smtp(admin_email, subject, body, config)
                        st.success(f"✅ Opsummering sendt til {admin_email}!")
                    except Exception as e:
                        st.error(f"❌ Emailfejl: {str(e)}")

    with tab7:
        st.markdown(get_admin_guide_html(), unsafe_allow_html=True)

    st.divider()

    config = load_config()
    st.subheader("SMTP Email-indstillinger")
    st.info("Disse indstillinger bruges til at sende påmindelser og notifikationer.")
    col1, col2 = st.columns(2)
    with col1:
        smtp_server   = st.text_input("SMTP Server",            value=config.get('smtp_server', 'smtp.gmail.com'))
        smtp_port     = st.number_input("SMTP Port",            value=int(config.get('smtp_port', 587)), min_value=1, max_value=65535)
        smtp_username = st.text_input("SMTP Brugernavn (email)", value=config.get('smtp_username', ''))
    with col2:
        smtp_password = st.text_input("SMTP Password", value=config.get('smtp_password', ''), type="password")
        admin_email   = st.text_input("Admin Email (modtager)", value=config.get('admin_email', ''))
        app_url_input = st.text_input("App URL", value=config.get('app_url', ''),
                                      placeholder="https://din-app.streamlit.app",
                                      help="Bruges i påmindelsesmails til medarbejdere")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Gem SMTP-indstillinger"):
            config['smtp_server']   = smtp_server
            config['smtp_port']     = smtp_port
            config['smtp_username'] = smtp_username
            config['smtp_password'] = smtp_password
            config['admin_email']   = admin_email
            config['app_url']       = app_url_input.rstrip('/')
            with st.spinner("Gemmer SMTP-indstillinger..."):
                success = save_config(config)
            if success:
                st.session_state['_toast'] = "✅ Indstillinger gemt!"
                st.rerun()
    with col2:
        if st.button("Send test-email"):
            try:
                send_email_smtp(
                    admin_email, "Test email fra Timeregnskab",
                    "Dette er en test email for at verificere SMTP-indstillingerne.",
                    {'smtp_server': smtp_server, 'smtp_port': smtp_port,
                     'smtp_username': smtp_username, 'smtp_password': smtp_password}
                )
                st.success("✅ Test-email sendt!")
            except Exception as e:
                st.error(f"❌ Fejl: {str(e)}")


# ─────────────────────────────────────────────────────
# Employee form
# ─────────────────────────────────────────────────────

def employee_form():
    token = st.query_params.get("token", "")
    if not token:
        st.title("Timeregnskab")
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #e8e8ed;border-radius:14px;
            padding:24px 28px;margin:20px 0;box-shadow:0 1px 6px rgba(0,0,0,0.05);
            font-size:15px;color:#1d1d1f;line-height:1.7;">
            <strong>Medarbejdere:</strong> Du skal bruge dit personlige link for at tilgå formularen.<br>
            <strong>Admin:</strong> Tilføj <code>?admin=true</code> til URL'en for at logge ind.
        </div>
        """, unsafe_allow_html=True)
        st.caption("Kontakt admin hvis du mangler dit link")
        return

    df = load_employees()
    if df.empty:
        return

    employee = df[df['Token'] == token]
    if employee.empty:
        st.error("Ugyldigt link. Kontakt venligst din administrator.")
        return

    emp = employee.iloc[0]
    period_key, period_label = get_current_period()
    existing = load_submission(emp['Name'], period_key)
    already_submitted = existing.get('udfyldt', False) if existing else False

    st.title("Timeregnskab")
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #e8f4fd 0%, #dceefb 100%);
        border: 1.5px solid #b3d7f5;
        border-radius: 14px;
        padding: 16px 22px;
        margin: 0 0 18px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <span style="font-size:28px;line-height:1;">👤</span>
        <div>
            <div style="font-size:11px;font-weight:600;color:#0071e3;text-transform:uppercase;letter-spacing:0.5px;">Logget ind som</div>
            <div style="font-size:20px;font-weight:700;color:#1d1d1f;margin-top:2px;">{emp['Name']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Info card
    st.markdown(f"""
    <div style="background:#ffffff;border:1px solid #e8e8ed;border-radius:14px;
        padding:20px 24px;margin:16px 0 8px 0;box-shadow:0 1px 6px rgba(0,0,0,0.05);
        font-size:15px;color:#1d1d1f;line-height:1.8;">
        <strong>Periode:</strong> {period_label}<br>
        <strong>Frist:</strong> Den {DEADLINE_DAY}. i måneden kl. 23:59<br>
        <strong>Påmindelse:</strong> Du modtager automatisk en påmindelsesmail d. {REMINDER_DAY}. — 2 dage før fristen<br>
        <strong style="color:#c0392b;">Vigtigt:</strong> Timer der ikke er indberettet inden d. {DEADLINE_DAY}. registreres ikke og medtages <strong>ikke</strong> i denne måneds opgørelse.
    </div>
    """, unsafe_allow_html=True)

    # Collapsible guide
    with st.expander("📖 Vejledning — klik her for hjælp"):
        st.markdown(get_employee_guide_html(period_label, REMINDER_DAY, DEADLINE_DAY),
                    unsafe_allow_html=True)

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

    if already_submitted:
        st.success("✅ Du har allerede indberettet for denne periode. Du kan stadig rette og genindsende.")

    data = {}

    if emp['Feriedage']:
        data['feriedage'] = st.number_input("Feriedage",
            value=existing.get('feriedage', 0) if existing else 0, min_value=0, key="feriedage")
    if emp['Feriefridag']:
        data['feriefridag'] = st.number_input("Feriefridage",
            value=existing.get('feriefridag', 0) if existing else 0, min_value=0, key="feriefridag")
    if emp['Sygedage']:
        data['sygedage'] = st.number_input("Sygedage",
            value=existing.get('sygedage', 0) if existing else 0, min_value=0, key="sygedage")
    if emp['Ekstra_Hverdag']:
        data['ekstra_hverdag'] = st.number_input("Ekstra timer (Hverdag)",
            value=existing.get('ekstra_hverdag', 0) if existing else 0, min_value=0, key="hverdag")
    if emp['Ekstra_Lørdag']:
        data['ekstra_lørdag'] = st.number_input("Ekstra timer (Lørdag)",
            value=existing.get('ekstra_lørdag', 0) if existing else 0, min_value=0, key="lørdag")
    if emp['Ekstra_Søndag']:
        data['ekstra_søndag'] = st.number_input("Ekstra timer (Søndag)",
            value=existing.get('ekstra_søndag', 0) if existing else 0, min_value=0, key="søndag")
    if emp['Ekstra_Andet']:
        data['ekstra_andet'] = st.number_input("Ekstra timer (Andet)",
            value=existing.get('ekstra_andet', 0) if existing else 0, min_value=0, key="andet")
    if emp['Antal_timer']:
        data['antal_timer'] = st.number_input("Antal timer i alt",
            value=existing.get('antal_timer', 0) if existing else 0, min_value=0, key="timer")

    # Indberet section
    st.markdown(f"""
    <div style="background:#f5f5f7;border:1.5px solid #d2d2d7;border-radius:14px;
        padding:20px 24px 12px 24px;margin:28px 0 12px 0;">
        <div style="font-size:18px;font-weight:600;color:#1d1d1f;margin-bottom:6px;">Indberet</div>
        <div style="font-size:14px;color:#6e6e73;line-height:1.5;">
            Marker afkrydsningsfeltet nedenfor og klik <strong>Indsend</strong> for at sende din
            registrering for perioden <strong>{period_label}</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    indberet = st.checkbox("Marker her for at indberette", value=already_submitted, key="indberet")
    data['udfyldt'] = indberet

    if st.button("Indsend", type="primary"):
        data['timestamp'] = datetime.now().isoformat()
        data['employee']  = emp['Name']
        data['month']     = period_key
        if save_submission(emp['Name'], data, period_key):
            if data.get('udfyldt'):
                st.success("✅ Indberettet!")
                st.balloons()
            else:
                st.success("Gemt (ikke markeret som indberettet).")


# ─────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────

def main():
    inject_css()
    if st.query_params.get("admin") == "true":
        admin_interface()
    else:
        employee_form()

if __name__ == "__main__":
    main()
