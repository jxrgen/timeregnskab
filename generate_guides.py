"""
Genererer to vejlednings-PDF'er til Timeregnskab-systemet:
  - Timeregnskab_Administratorvejledning.pdf
  - Timeregnskab_Medarbejdervejledning.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os

# ── Farver ──────────────────────────────────────────────────────────
BLUE       = colors.HexColor("#0071e3")
BLUE_DARK  = colors.HexColor("#004fa3")
BLUE_LIGHT = colors.HexColor("#e8f1fc")
GRAY_BG    = colors.HexColor("#f5f5f7")
GRAY_LINE  = colors.HexColor("#d2d2d7")
GRAY_MID   = colors.HexColor("#6e6e73")
BLACK      = colors.HexColor("#1d1d1f")
WHITE      = colors.white
GREEN      = colors.HexColor("#34c759")
ORANGE     = colors.HexColor("#ff9500")
RED        = colors.HexColor("#ff3b30")

W, H = A4   # 595.27 x 841.89 pt
MARGIN = 22 * mm


# ── Custom flowables ────────────────────────────────────────────────

class CoverHeader(Flowable):
    """Enkel blå header til forsiden."""
    def __init__(self, title, subtitle, width):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self._w = width
        self._h = 25 * mm

    def wrap(self, aw, ah):
        return self._w, self._h

    def draw(self):
        c = self.canv
        w, h = self._w, self._h

        c.setFillColor(BLUE)
        c.roundRect(0, 0, w, h, 3 * mm, fill=1, stroke=0)

        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(6 * mm, 10 * mm, self.title)

        c.setFont("Helvetica", 9)
        c.setFillColorRGB(1, 1, 1, 0.8)
        c.drawString(6 * mm, 4 * mm, self.subtitle)


class SectionHeader(Flowable):
    """Blå sektionsoverskrift med bundlinje."""
    def __init__(self, text, width, color=BLUE):
        super().__init__()
        self.text = text
        self._w = width
        self.color = color

    def wrap(self, aw, ah):
        return self._w, 14 * mm

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.rect(0, 8*mm, self._w, 0.6*mm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(BLACK)
        c.drawString(0, 9.5*mm, self.text)


class TimelineBox(Flowable):
    """Tidslinje med tre milepæle."""
    def __init__(self, width):
        super().__init__()
        self._w = width
        self._h = 42 * mm

    def wrap(self, aw, ah):
        return self._w, self._h

    def draw(self):
        c = self.canv
        w, h = self._w, self._h
        items = [
            ("D. 18", "Påminding", "Alle modtager en\npåmindelsesmail", ORANGE),
            ("D. 20", "Frist",     "Sidste dag for\nindberetning",      RED),
            ("D. 21", "Opsamling", "Admin modtager\nsamlet tabel",       GREEN),
        ]
        box_w = (w - 4*mm) / 3
        for i, (date, title, desc, col) in enumerate(items):
            x = i * (box_w + 2*mm)
            # Kort
            c.setFillColor(GRAY_BG)
            c.roundRect(x, 0, box_w, h - 4*mm, 3*mm, fill=1, stroke=0)
            # Farvet topcirkel
            c.setFillColor(col)
            c.roundRect(x, h - 14*mm, box_w, 10*mm, 3*mm, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(x + box_w/2, h - 9*mm, date)
            # Titel
            c.setFillColor(BLACK)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(x + box_w/2, h - 18*mm, title)
            # Beskrivelse
            c.setFillColor(GRAY_MID)
            c.setFont("Helvetica", 9)
            for j, line in enumerate(desc.split("\n")):
                c.drawCentredString(x + box_w/2, h - 26*mm - j*4*mm, line)


class InfoBox(Flowable):
    """Lys blå infobox med ikon og tekst."""
    def __init__(self, lines, width, icon="ℹ"):
        super().__init__()
        self.lines = lines
        self._w = width
        self.icon = icon
        self._h = (len(lines) * 5.5 + 10) * mm

    def wrap(self, aw, ah):
        return self._w, self._h

    def draw(self):
        c = self.canv
        w, h = self._w, self._h
        c.setFillColor(BLUE_LIGHT)
        c.roundRect(0, 0, w, h, 3*mm, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(4*mm, h - 7*mm, self.icon)
        c.setFont("Helvetica", 10)
        c.setFillColor(BLACK)
        for i, line in enumerate(self.lines):
            c.drawString(11*mm, h - 7*mm - i * 5.5*mm, line)


# ── Styles ──────────────────────────────────────────────────────────

def make_styles():
    body  = ParagraphStyle("body",  fontName="Helvetica",      fontSize=10,  leading=15,  textColor=BLACK,     spaceAfter=4)
    bold  = ParagraphStyle("bold",  fontName="Helvetica-Bold", fontSize=10,  leading=15,  textColor=BLACK,     spaceAfter=4)
    h2    = ParagraphStyle("h2",    fontName="Helvetica-Bold", fontSize=12,  leading=17,  textColor=BLACK,     spaceAfter=6, spaceBefore=10)
    h3    = ParagraphStyle("h3",    fontName="Helvetica-Bold", fontSize=10,  leading=14,  textColor=BLUE,      spaceAfter=4, spaceBefore=8)
    small = ParagraphStyle("small", fontName="Helvetica",      fontSize=9,   leading=13,  textColor=GRAY_MID,  spaceAfter=3)
    tip   = ParagraphStyle("tip",   fontName="Helvetica-Oblique", fontSize=9, leading=13, textColor=GRAY_MID,  spaceAfter=3)
    bullet = ParagraphStyle("bullet", fontName="Helvetica", fontSize=10, leading=14, textColor=BLACK, leftIndent=10, spaceAfter=3, bulletIndent=2)
    return dict(body=body, bold=bold, h2=h2, h3=h3, small=small, tip=tip, bullet=bullet)


def bullet_item(text, s):
    return Paragraph(f"<bullet>•</bullet> {text}", s["bullet"])


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY_MID)
    canvas.drawString(MARGIN, 12*mm, "Timeregnskab")
    canvas.drawRightString(W - MARGIN, 12*mm, f"Side {doc.page}")
    canvas.setStrokeColor(GRAY_LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 16*mm, W - MARGIN, 16*mm)
    canvas.restoreState()


def card_table(rows, col_widths, s, header_row=True):
    """Laver en tabel med Apple-stil."""
    t = Table(rows, colWidths=col_widths)
    style = [
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("LEADING",     (0, 0), (-1, -1), 14),
        ("TEXTCOLOR",   (0, 0), (-1, -1), BLACK),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, GRAY_BG]),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1),  5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("LINEBELOW",   (0, 0), (-1, -1), 0.5, GRAY_LINE),
        ("ROUNDEDCORNERS", [3]),
    ]
    if header_row:
        style += [
            ("BACKGROUND",  (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_BG]),
        ]
    t.setStyle(TableStyle(style))
    return t


# ════════════════════════════════════════════════════════════════════
# ADMIN PDF
# ════════════════════════════════════════════════════════════════════

def build_admin_pdf(path):
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22*mm,
    )
    cw = W - 2 * MARGIN   # tekstbredde
    s  = make_styles()
    story = []

    # ── Forside ─────────────────────────────────────────────────────
    story.append(CoverHeader(
        "Administratorvejledning",
        "Timeregnskab · Digital tidsregistrering for dit team",
        cw
    ))
    story.append(Spacer(1, 8*mm))
    story.append(InfoBox([
        "Denne vejledning beskriver, hvordan du som administrator bruger",
        "Timeregnskab-systemet. Her finder du alt hvad du behøver at vide:",
        "opsætning, daglig brug, automatiske handlinger og tips.",
    ], cw, "📋"))
    story.append(Spacer(1, 6*mm))

    # Indholdsfortegnelse
    story.append(SectionHeader("Indhold", cw))
    story.append(Spacer(1, 3*mm))
    toc_data = [
        ["1.", "Systemoverblik",                "s. 1"],
        ["2.", "Login og adgang",               "s. 1"],
        ["3.", "Automatisk månedlig cyklus",     "s. 2"],
        ["4.", "Administrer medarbejdere",       "s. 2"],
        ["5.", "Se og eksportere indsendelser",  "s. 3"],
        ["6.", "Send fælles besked",             "s. 3"],
        ["7.", "Simuler og test",                "s. 3"],
        ["8.", "SMTP email-indstillinger",       "s. 4"],
        ["9.", "Hyppige spørgsmål",             "s. 4"],
    ]
    for row in toc_data:
        story.append(Table(
            [row],
            colWidths=[8*mm, cw - 30*mm, 22*mm],
            style=TableStyle([
                ("FONTNAME",  (0,0),(-1,-1),"Helvetica"),
                ("FONTSIZE",  (0,0),(-1,-1), 10),
                ("LEADING",   (0,0),(-1,-1), 16),
                ("TEXTCOLOR", (0,0),(0,-1),  BLUE),
                ("FONTNAME",  (0,0),(0,-1),  "Helvetica-Bold"),
                ("TEXTCOLOR", (2,0),(2,-1),  GRAY_MID),
                ("ALIGN",     (2,0),(2,-1),  "RIGHT"),
                ("TOPPADDING",(0,0),(-1,-1), 1),
                ("BOTTOMPADDING",(0,0),(-1,-1), 1),
            ])
        ))
    story.append(Spacer(1, 8*mm))

    # ── 1. Systemoverblik ────────────────────────────────────────────
    story.append(SectionHeader("1. Systemoverblik", cw))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Timeregnskab er et webbaseret system, hvor medarbejdere registrerer deres timer, "
        "ferie- og sygedage via et personligt link. Der er ingen apps at installere — "
        "det kræver kun en browser. Du som administrator styrer alt via admin-interfacet.",
        s["body"]
    ))
    story.append(Spacer(1, 3*mm))
    overview = [
        ["Komponent", "Hvad det er"],
        ["Webformular", "Medarbejdernes personlige side med unikke links (tokens)"],
        ["Admin-panel", "Din kontrol-side til at administrere alt i systemet"],
        ["GitHub repo", "Systemets database — alle data gemmes som filer her"],
        ["SMTP email", "Bruges til automatiske påmindelser og opsamlingsrapporter"],
        ["GitHub Actions", "Automatisk: sender mails d. 18 og d. 21 hver måned"],
    ]
    story.append(card_table(overview, [45*mm, cw - 45*mm], s))
    story.append(Spacer(1, 6*mm))

    # ── 2. Login ─────────────────────────────────────────────────────
    story.append(SectionHeader("2. Login og adgang", cw))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Admin-interfacet tilgås via URL'en med parameteren <b>?admin=true</b>. "
        "Eksempel:", s["body"]
    ))
    story.append(Paragraph("https://din-app.streamlit.app/?admin=true", s["h3"]))
    story.append(Spacer(1, 2*mm))
    story.append(InfoBox([
        "Adgangskoden sættes under Streamlit Cloud → App Settings → Secrets",
        "som: ADMIN_PASSWORD = \"dinadgangskode\"",
        "Hold adgangskoden hemmelig — alle med koden har fuld adgang.",
    ], cw, "🔒"))
    story.append(Spacer(1, 6*mm))

    # ── 3. Månedlig cyklus ───────────────────────────────────────────
    story.append(SectionHeader("3. Automatisk månedlig cyklus", cw))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Systemet kører automatisk hver måned. Registreringsperioden løber altid fra "
        "<b>d. 21 i én måned til d. 20 i den næste</b>. Der sker tre ting automatisk:",
        s["body"]
    ))
    story.append(Spacer(1, 4*mm))
    story.append(TimelineBox(cw))
    story.append(Spacer(1, 5*mm))
    cycle = [
        ["Dato", "Handling", "Hvem"],
        ["D. 21 (forrige)", "Ny registreringsperiode åbner", "Alle medarbejdere"],
        ["D. 18", "Påmindelsesmail sendes automatisk til alle", "Alle aktive medarbejdere"],
        ["D. 20", "Indberetningsfrist — ikke indberettede timer medtages ikke", "Medarbejdere"],
        ["D. 21", "Du modtager samlet tabel med alle registreringer", "Administrator"],
        ["D. 21", "Ny periode åbner automatisk for næste måned", "System"],
    ]
    story.append(card_table(cycle, [28*mm, cw - 60*mm, 32*mm], s))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "💡 Tip: Du kan til enhver tid sende tabellen manuelt via fanebladet <b>Simuler</b>.",
        s["tip"]
    ))
    story.append(Spacer(1, 3*mm))
    story.append(InfoBox([
        "Tjek spammappen: Automatiske mails fra systemet kan havne i spam- eller junk-mappen.",
        "Bed medarbejderne om at tilføje systemets emailadresse til deres kontakter, og tjek",
        "at din egen admin-mail (d. 21) ikke ender i spam.",
    ], cw, "📬"))

    # ── 4. Administrer medarbejdere ──────────────────────────────────
    story.append(PageBreak())
    story.append(SectionHeader("4. Administrer medarbejdere", cw))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("Tilføj ny medarbejder", s["h3"]))
    story.append(Paragraph("Gå til fanebladet <b>Tilføj ny</b> og udfyld:", s["body"]))
    for item in [
        "Navn og emailadresse (obligatorisk — systemet validerer emailformatet)",
        "Hvilke felter medarbejderen skal se (ferie, sygedage, ekstra timer osv.)",
        "Klik <b>Tilføj medarbejder</b> — et unikt link genereres automatisk",
    ]:
        story.append(bullet_item(item, s))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("Send linket til medarbejderen", s["h3"]))
    story.append(Paragraph(
        "Under <b>Medarbejdere</b> → åbn medarbejderen → kopiér det personlige link "
        "nederst i boksen. Send det via email eller chat. Linket ændres aldrig medmindre "
        "du klikker <b>Ny token</b>.", s["body"]
    ))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("Rediger medarbejder", s["h3"]))
    for item in [
        "Åbn medarbejderen under fanebladet <b>Medarbejdere</b>",
        "Ret navn, email, aktivstatus eller skematype og klik <b>Gem ændringer</b>",
        "Klik <b>Ny token</b> for at generere et nyt personligt link (invaliderer det gamle)",
    ]:
        story.append(bullet_item(item, s))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("Slet medarbejder", s["h3"]))
    story.append(Paragraph(
        "Klik <b>Slet</b> → systemet spørger <i>\"Er du sikker?\"</i> → klik <b>Ja</b>. "
        "Sletning kan ikke fortrydes. Tidligere indsendelser fra medarbejderen bevares i arkivet.",
        s["body"]
    ))
    story.append(Spacer(1, 3*mm))
    story.append(InfoBox([
        "Vigtigt: Klikker du 'Ny token', mister medarbejderen adgang via sit gamle link.",
        "Send altid det nye link til medarbejderen med det samme — ellers kan de",
        "ikke logge ind og indberette deres timer.",
    ], cw, "⚠️"))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("Skemafelter — hvad vises for hvem", s["h3"]))
    fields = [
        ["Felt", "Hvad det registrerer"],
        ["Feriedage", "Antal brugte feriedage i perioden"],
        ["Feriefridag", "Særlige fridage (f.eks. feriefridage fra overenskomst)"],
        ["Sygedage", "Sygedage inkl. første sygedag og raskmelding"],
        ["Ekstra Hverdag", "Ekstra arbejdstimer på hverdage ud over normal tid"],
        ["Ekstra Lørdag", "Ekstra arbejdstimer om lørdagen"],
        ["Ekstra Søndag", "Ekstra arbejdstimer om søndagen"],
        ["Ekstra Andet", "Andre ekstra timer (specificeres i kommentarfelt)"],
        ["Antal timer", "Samlet antal arbejdstimer i perioden"],
    ]
    story.append(card_table(fields, [42*mm, cw - 42*mm], s))
    story.append(Spacer(1, 6*mm))

    # ── 5. Indsendelser ──────────────────────────────────────────────
    story.append(KeepTogether([
        SectionHeader("5. Se indsendelser", cw),
        Spacer(1, 3*mm),
        Paragraph(
            "Under fanebladet <b>Indsendelser</b> kan du se status for alle aktive "
            "medarbejdere for en given periode. Vælg periode i dropdown-menuen. "
            "✅ = indberettet, ❌ = mangler.", s["body"]
        ),
        Spacer(1, 3*mm),
        InfoBox([
            "Opsamlingstabellen (d. 21) samler data fra ALLE medarbejdere, også dem der",
            "ikke har indberettet — disse markeres tydeligt med 'Ikke indberettet'.",
        ], cw, "📊"),
        Spacer(1, 3*mm),
        InfoBox([
            "Modtager du ikke admin-mailen d. 21? Tjek din spammappe.",
            "Tilfoej systemets afsenderadresse til dine kontakter for at undgaa det fremover.",
        ], cw, "📬"),
        Spacer(1, 6*mm),
    ]))

    # ── 6. Fælles besked ─────────────────────────────────────────────
    story.append(KeepTogether([
        SectionHeader("6. Send fælles besked", cw),
        Spacer(1, 3*mm),
        Paragraph(
            "Under <b>Fælles besked</b> kan du sende en frifromateret email til udvalgte "
            "medarbejdere. Nyttigt til ad hoc-beskeder, ændringer i frister eller "
            "andet der ikke er en del af den automatiske flow.", s["body"]
        ),
        Spacer(1, 3*mm),
    ]))
    for item in [
        "Sæt flueben ved de medarbejdere der skal modtage beskeden",
        "Skriv en emnelinj og beskedtekst",
        "Klik <b>Send besked</b> — systemet bruger SMTP-indstillingerne fra Systeminfo",
    ]:
        story.append(bullet_item(item, s))
    story.append(Spacer(1, 6*mm))

    # ── 7. Simuler ───────────────────────────────────────────────────
    story.append(KeepTogether([
        SectionHeader("7. Simuler og test", cw),
        Spacer(1, 3*mm),
        Paragraph(
            "Under <b>Simuler</b> kan du manuelt sende den automatiske opsamlingstabel "
            "til dig selv — uanset hvad datoen er. Dette er nyttigt til:", s["body"]
        ),
        Spacer(1, 2*mm),
    ]))
    for item in [
        "At teste at SMTP-opsætningen virker korrekt",
        "At få et overblik over aktuelle indsendelser midt i en periode",
        "At sende tabellen igen, hvis den automatiske mail fejlede",
    ]:
        story.append(bullet_item(item, s))
    story.append(Spacer(1, 6*mm))

    # ── 8. SMTP ─────────────────────────────────────────────────────
    story.append(SectionHeader("8. SMTP email-indstillinger", cw))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Indstillingerne sættes i bunden af admin-siden. De bruges af både webappen "
        "og de automatiske GitHub Actions-scripts.", s["body"]
    ))
    story.append(Spacer(1, 3*mm))
    smtp = [
        ["Felt", "Eksempel / forklaring"],
        ["SMTP Server", "send.one.com  (one.com), smtp.gmail.com  (Gmail)"],
        ["SMTP Port", "465 = SSL/TLS · 587 = STARTTLS"],
        ["Brugernavn", "Din emailadresse som systemet sender fra"],
        ["Password", "Adgangskode eller app-specifik adgangskode"],
        ["Admin Email", "Din email — modtager opsamlingstabellen d. 21"],
    ]
    story.append(card_table(smtp, [40*mm, cw - 40*mm], s))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "Brug knappen <b>Send test-email</b> for at verificere at indstillingerne virker "
        "inden du gemmer.", s["tip"]
    ))
    story.append(Spacer(1, 6*mm))

    # ── 9. FAQ ──────────────────────────────────────────────────────
    story.append(SectionHeader("9. Hyppige spørgsmål", cw))
    story.append(Spacer(1, 3*mm))
    faqs = [
        ("En medarbejder har mistet sit link — hvad gør jeg?",
         "Gå til Medarbejdere → åbn medarbejderen → kopiér linket og send det igen. "
         "Linket ændres ikke af sig selv. Klik kun 'Ny token' hvis du tror linket er kompromitteret."),
        ("Hvad sker der med data der ikke indberettes inden d. 20?",
         "Data medtages ikke i opsamlingstabellen for den pågældende periode og "
         "registreres dermed ikke. Medarbejderen kan stadig registrere for næste periode."),
        ("Kan jeg ændre hvilke felter en medarbejder ser?",
         "Ja — åbn medarbejderen og sæt/fjern flueben ved felttyperne og klik 'Gem ændringer'. "
         "Ændringen træder i kraft næste gang medarbejderen åbner sit link."),
        ("Systemet sender ikke mails — hvad er galt?",
         "Tjek SMTP-indstillingerne med 'Send test-email'. Husk at Gmail kræver "
         "en app-specifik adgangskode (ikke din normale Gmail-adgangskode)."),
        ("Appen er langsom eller 'sov' ind?",
         "Streamlit Cloud sætter appen i dvale efter 7 dages inaktivitet. "
         "Systemet har en automatisk 'keep-alive'-ping to gange i døgnet som forhindrer dette."),
    ]
    for q, a in faqs:
        story.append(KeepTogether([
            Paragraph(f"<b>Q: {q}</b>", s["body"]),
            Paragraph(f"A: {a}", s["body"]),
            Spacer(1, 3*mm),
        ]))

    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    print(f"✅ Gemt: {path}")


# ════════════════════════════════════════════════════════════════════
# MEDARBEJDER PDF
# ════════════════════════════════════════════════════════════════════

def build_employee_pdf(path):
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=22*mm,
    )
    cw = W - 2 * MARGIN
    s  = make_styles()
    story = []

    # ── Forside ─────────────────────────────────────────────────────
    story.append(CoverHeader(
        "Medarbejdervejledning",
        "Timeregnskab · Sådan registrerer du dine timer",
        cw
    ))
    story.append(Spacer(1, 8*mm))
    story.append(InfoBox([
        "Denne vejledning viser dig, hvordan du bruger Timeregnskab.",
        "Det tager kun 2 minutter at registrere dine timer — og du behøver",
        "hverken at installere noget eller huske en adgangskode.",
    ], cw, "👋"))
    story.append(Spacer(1, 6*mm))

    # ── 1. Dit personlige link ───────────────────────────────────────
    story.append(SectionHeader("1. Dit personlige link", cw))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Du har modtaget et personligt link fra din administrator. Linket ser sådan ud:",
        s["body"]
    ))
    story.append(Paragraph("https://din-app.streamlit.app/?token=AbCdEfGh...", s["h3"]))
    story.append(Spacer(1, 3*mm))
    for item in [
        "Gem linket i dine favoritter eller bogmærker — du bruger det hver måned",
        "Linket er <b>kun dit</b> — del det ikke med andre",
        "Du behøver ingen adgangskode — linket er din nøgle",
        "Har du mistet linket? Kontakt din administrator som kan sende det igen",
    ]:
        story.append(bullet_item(item, s))
    story.append(Spacer(1, 6*mm))

    # ── 2. Vigtige datoer ────────────────────────────────────────────
    story.append(SectionHeader("2. Vigtige datoer hver måned", cw))
    story.append(Spacer(1, 4*mm))
    story.append(TimelineBox(cw))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "Registreringsperioden løber altid fra <b>d. 21 i én måned til d. 20 i den næste</b>. "
        "Du kan udfylde og rette din registrering løbende hele perioden — "
        "men husk at klikke <b>Indsend</b> senest d. 20.",
        s["body"]
    ))
    story.append(Spacer(1, 3*mm))
    story.append(InfoBox([
        "Har du ikke indberettet inden d. 20, medtages din registrering ikke",
        "i opsamlingen for den måned. Du kan stadig registrere for den næste periode.",
    ], cw, "⚠️"))
    story.append(Spacer(1, 6*mm))

    # ── 3. Trin-for-trin ─────────────────────────────────────────────
    story.append(SectionHeader("3. Sådan udfylder du din registrering", cw))
    story.append(Spacer(1, 3*mm))

    steps = [
        ("Åbn dit personlige link",
         "Klik på dit personlige link i browseren. Du ser en formular med de "
         "felter der er relevante for netop dig."),
        ("Læs vejledningskortet",
         "Øverst på siden er der et infokort med den aktuelle periode og fristdato. "
         "Fold guiden ud for at se yderligere hjælp."),
        ("Udfyld dine felter",
         "Angiv antal dage eller timer i hvert felt. Du kan gemme undervejs "
         "og vende tilbage og rette, så mange gange du vil inden fristen."),
        ("Marker 'Indberet' og klik Indsend",
         "Når du er færdig, sætter du hak i boksen 'Marker her for at indberette' "
         "og klikker på den blå <b>Indsend</b>-knap. Du modtager en bekræftelse på skærmen."),
        ("Klar! Du er færdig for denne måned",
         "Du kan altid gå ind igen og rette dine tal og genindsende inden d. 20. "
         "Den seneste indsendelse er altid den gældende."),
    ]
    for i, (title, desc) in enumerate(steps, 1):
        story.append(KeepTogether([
            Table(
                [[
                    Paragraph(str(i), ParagraphStyle(
                        "stepnum", fontName="Helvetica-Bold", fontSize=14,
                        textColor=WHITE, alignment=TA_CENTER
                    )),
                    Paragraph(f"<b>{title}</b><br/>{desc}", s["body"]),
                ]],
                colWidths=[9*mm, cw - 9*mm],
                style=TableStyle([
                    ("BACKGROUND",     (0,0),(0,0), BLUE),
                    ("VALIGN",         (0,0),(-1,-1), "MIDDLE"),
                    ("TOPPADDING",     (0,0),(-1,-1), 6),
                    ("BOTTOMPADDING",  (0,0),(-1,-1), 6),
                    ("LEFTPADDING",    (0,0),(0,0), 2),
                    ("RIGHTPADDING",   (0,0),(0,0), 2),
                    ("LEFTPADDING",    (1,0),(1,0), 8),
                    ("LINEBELOW",      (0,0),(-1,-1), 0.5, GRAY_LINE),
                    ("ROWBACKGROUNDS", (0,0),(-1,-1), [GRAY_BG]),
                ])
            ),
            Spacer(1, 2*mm),
        ]))
    story.append(Spacer(1, 6*mm))

    # ── 4. Felter ───────────────────────────────────────────────────
    story.append(SectionHeader("4. Hvad betyder felterne?", cw))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Du ser kun de felter som er relevante for dig — din administrator har valgt dem. "
        "Her er en forklaring på alle mulige felter:", s["body"]
    ))
    story.append(Spacer(1, 3*mm))
    fields = [
        ["Felt", "Hvad du skal skrive"],
        ["Feriedage", "Antal feriedage du har holdt i perioden (hele dage)"],
        ["Feriefridag", "Særlige fridage fra din overenskomst — spørg din leder hvis du er i tvivl"],
        ["Sygedage", "Antal sygedage, inkl. første sygedag og raskmelding"],
        ["Ekstra Hverdag", "Ekstra arbejdstimer på hverdage ud over normal arbejdstid"],
        ["Ekstra Lørdag", "Ekstra timer du har arbejdet om lørdagen"],
        ["Ekstra Søndag", "Ekstra timer du har arbejdet om søndagen"],
        ["Ekstra Andet", "Andre ekstra timer — beskriv gerne i kommentarfeltet"],
        ["Antal timer", "Samlet antal arbejdstimer du har haft i perioden"],
    ]
    story.append(card_table(fields, [42*mm, cw - 42*mm], s))
    story.append(Spacer(1, 6*mm))

    # ── 5. Påmindelsesmail ───────────────────────────────────────────
    story.append(KeepTogether([
        SectionHeader("5. Automatisk påmindelsesmail", cw),
        Spacer(1, 3*mm),
        Paragraph(
            "D. 18 hver måned modtager du en automatisk påmindelsesmail med dit personlige "
            "link. Mailen sendes til den emailadresse, du er registreret med. "
            "Du behøver ikke afvente mailen — du kan gå ind og udfylde din registrering "
            "når som helst i perioden.",
            s["body"]
        ),
        Spacer(1, 3*mm),
        InfoBox([
            "Tjek din spammappe, hvis du ikke modtager påmindelsesmailen d. 18.",
            "Kontakt din administrator hvis du aldrig har modtaget dit personlige link.",
        ], cw, "📧"),
        Spacer(1, 6*mm),
    ]))

    # ── 6. Spørgsmål ─────────────────────────────────────────────────
    story.append(SectionHeader("6. Spørgsmål og svar", cw))
    story.append(Spacer(1, 3*mm))
    faqs = [
        ("Hvad hvis jeg har glemt at indberette til fristen?",
         "Kontakt din administrator. Dine timer for den måned medtages desværre ikke automatisk, "
         "men din leder kan måske hjælpe med at håndtere det manuelt."),
        ("Kan jeg rette mine tal efter jeg har klikket Indsend?",
         "Ja! Du kan gå ind og ændre tallene og klikke Indsend igen så mange gange "
         "du vil, indtil fristen d. 20. Den seneste indsendelse er altid den gældende."),
        ("Hvad hvis et felt ikke passer til mit arbejde?",
         "Kontakt din administrator — vedkommende kan ændre hvilke felter du ser."),
        ("Er mine data private?",
         "Ja. Kun du og din administrator kan se dine registreringer. "
         "Andre medarbejdere kan ikke se dit link eller dine data."),
        ("Hvad sker der med mine data?",
         "Data gemmes sikkert i systemets database og bruges til at lave en månedlig "
         "oversigt til administratoren. De bruges udelukkende til intern tidsregistrering."),
    ]
    for q, a in faqs:
        story.append(KeepTogether([
            Paragraph(f"<b>Q: {q}</b>", s["body"]),
            Paragraph(f"A: {a}", s["body"]),
            Spacer(1, 3*mm),
        ]))

    # ── Afslutning ───────────────────────────────────────────────────
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width=cw, color=GRAY_LINE))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "Har du spørgsmål til systemet? Kontakt din administrator.",
        ParagraphStyle("center", fontName="Helvetica", fontSize=10,
                       textColor=GRAY_MID, alignment=TA_CENTER)
    ))

    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    print(f"✅ Gemt: {path}")


# ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    build_admin_pdf(os.path.join(base, "Timeregnskab_Administratorvejledning.pdf"))
    build_employee_pdf(os.path.join(base, "Timeregnskab_Medarbejdervejledning.pdf"))
