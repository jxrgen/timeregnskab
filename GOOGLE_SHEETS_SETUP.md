# Opsætning i Google Sheets

## Trin 1: Opret Master Sheet
- Gå til [sheets.google.com](https://sheets.google.com) og opret et nyt regneark
- Giv det navnet "Timeregnskab - Master"
- Dette bliver administratorens oversigt

## Trin 2: Åbn Apps Script
- I Master Sheet: **Extensions** → **Apps Script**
- Script editoren åbner i en ny fane

## Trin 3: Indsæt kode
- Slet standardkoden (`function myFunction() {}`)
- Opret to filer i Apps Script:
  - `Code.gs` - kopier fra `/home/jxrgen/opencode/timeregnskab/Code.gs`
  - `Config.gs` - kopier fra `/home/jxrgen/opencode/timeregnskab/Config.gs`

## Trin 4: Ret konfiguration
I `Config.gs`:
- Erstat `admin@example.com` med din egen email

## Trin 5: Gem og kør første opsætning
- Klik **Gem** (disk-ikon)
- Vælg funktionen `setup` i dropdown øverst
- Klik **Kør** (play-ikon)
- Godkend tilladelserne når Google spørger (der skal godkendes adgang til Drive og Sheets)

## Trin 6: Tilføj medarbejdere
- Gå tilbage til Master Sheet
- Find fanen **Employees** (oprettet af setup)
- Tilføj dine medarbejdere:
  - Kolonne A: Navn
  - Kolonne B: Email (deres Google email)
  - Kolonne C: Tjek "Aktiv" for dem der skal med
  - Kolonne D: Sheet ID (udfyldes automatisk)

## Trin 7: Opret medarbejdernes individuelle sheets
- I Apps Script vælg funktionen `ensureEmployeeSheets` og kør den
- Der oprettes nu et separat Google Sheet til hver medarbejder
- Hver medarbejder får automatisk adgang til kun deres eget sheet
- Sheet ID'et gemmes i Employees fanen

## Trin 8: Opret måneds-fane for alle
- I Apps Script vælg funktionen `createMonthlyTabForAll` og kør den
- Der oprettes en fane med nuværende måned (f.eks. "2026-04") i hver medarbejders sheet

## Trin 9: Send velkomst-emails (valgfrit)
- I Apps Script vælg funktionen `sendWelcomeEmails` og kør den
- Hver medarbejder får en email med link til deres personlige timeregnskab

## Trin 10: Opsæt automatiske triggere
I Apps Script editoren:
1. Klik på **Triggers** (klokke-ikon) til venstre
2. Klik **+ Add Trigger** og opsæt tre triggere:

**Trigger 1 - Ny måned (opret måneds-fane til alle):**
- Funktion: `createMonthlyTabForAll`
- Udløses ved: Time-driven
- Vælg type: Month timer
- Vælg dag: 1st of month

**Trigger 2 - Påmindelser:**
- Funktion: `sendReminders`
- Udløses ved: Time-driven
- Vælg type: Day timer
- Vælg tidspunkt: f.eks. 8am to 9am

**Trigger 3 - Opsummering:**
- Funktion: `aggregateData`
- Udløses ved: Time-driven
- Vælg type: Day timer
- Vælg tidspunkt: f.eks. 9am to 10am

## Sådan virker det

1. **Hver medarbejder** har deres eget separate Google Sheet med kun deres data
2. **Medarbejderne** kan ikke se hinandens timeregnskaber (de har kun adgang til deres eget sheet)
3. **Den 1. i måneden** oprettes en ny fane automatisk i hver medarbejders sheet
4. **Den 20.** får manglende medarbejdere en påmindelse (tjekker om "Udfyldt" er markeret)
5. **Den 25.** samles alle data i Master Sheetets **Summary** fane og admin får besked
6. **Medarbejderne** markerer selv "Udfyldt" i deres sheet når de er færdige

## Sikkerhed
- Hver medarbejder har kun adgang til deres eget sheet
- Master Sheetet (med Summary) er kun for administratoren
- Data samles automatisk uden at medarbejdere kan se hinandens data
