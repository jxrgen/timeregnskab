// Code.gs
function getSpreadsheet() {
  return SpreadsheetApp.getActiveSpreadsheet();
}

function getEmployeesSheet() {
  const ss = getSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.SHEET_NAMES.EMPLOYEES);
  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.SHEET_NAMES.EMPLOYEES);
    sheet.getRange(1, 1, 1, 4).setValues([["Navn", "Email", "Aktiv", "Sheet ID"]]);
    sheet.getRange("C2:C").insertCheckboxes();
  }
  return sheet;
}

function getActiveEmployees() {
  const sheet = getEmployeesSheet();
  const data = sheet.getDataRange().getValues();
  const employees = [];
  for (let i = 1; i < data.length; i++) {
    const [name, email, active, sheetId] = data[i];
    if (active && email) employees.push({ name, email, sheetId, rowIndex: i + 1 });
  }
  return employees;
}

function createEmployeeSheet(employee) {
  const ss = getSpreadsheet();
  const employeesSheet = getEmployeesSheet();

  // Create new spreadsheet for employee
  const newSheet = SpreadsheetApp.create(`Timeregnskab - ${employee.name}`);
  const sheetId = newSheet.getId();

  // Set up initial structure
  const sheet = newSheet.getActiveSheet();
  sheet.setName("Info");
  sheet.getRange(1, 1, 1, 2).setValues([["Medarbejder", employee.name]]);
  sheet.getRange(2, 1, 1, 2).setValues([["Email", employee.email]]);

  // Remove default sheets if any
  const sheets = newSheet.getSheets();
  sheets.forEach(s => {
    if (s.getName() !== "Info") newSheet.deleteSheet(s);
  });

  // Share with employee only
  const file = DriveApp.getFileById(sheetId);
  file.addEditor(employee.email);

  // Update employee sheet with Sheet ID
  const data = employeesSheet.getDataRange().getValues();
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === employee.name) {
      employeesSheet.getRange(i + 1, 4).setValue(sheetId);
      break;
    }
  }

  return sheetId;
}

function ensureEmployeeSheets() {
  const employees = getActiveEmployees();
  employees.forEach(emp => {
    if (!emp.sheetId) {
      createEmployeeSheet(emp);
    }
  });
}

function createMonthlyTabForAll() {
  const employees = getActiveEmployees();
  const now = new Date();
  const monthName = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;

  employees.forEach(emp => {
    if (!emp.sheetId) return;
    try {
      const ss = SpreadsheetApp.openById(emp.sheetId);
      let sheet = ss.getSheetByName(monthName);
      if (sheet) return;

      sheet = ss.insertSheet(monthName);
      const headers = ["Ferie/Fridage", "Sygedage", "Feriedage", "Udfyldt", "Sidst opdateret"];
      sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
      sheet.getRange(2, 4).insertCheckboxes();
    } catch (e) {
      Logger.log(`Error creating monthly tab for ${emp.name}: ${e}`);
    }
  });
}

function sendReminders() {
  const now = new Date();
  if (now.getDate() !== CONFIG.REMINDER_DAY) return;

  const employees = getActiveEmployees();
  const monthName = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;

  employees.forEach(emp => {
    if (!emp.sheetId) return;
    try {
      const ss = SpreadsheetApp.openById(emp.sheetId);
      const sheet = ss.getSheetByName(monthName);
      if (!sheet) return;

      const data = sheet.getDataRange().getValues();
      const filled = data[1] && data[1][3]; // "Udfyldt" column

      if (!filled) {
        const subject = CONFIG.EMAIL.REMINDER_SUBJECT.replace("{month}", monthName);
        const body = CONFIG.EMAIL.REMINDER_BODY
          .replace("{name}", emp.name)
          .replace("{month}", monthName)
          .replace("{deadline}", `${CONFIG.REMINDER_DAY}. ${now.getMonth() + 1}`)
          .replace("{sheetUrl}", `https://docs.google.com/spreadsheets/d/${emp.sheetId}`);
        MailApp.sendEmail(emp.email, subject, body);
      }
    } catch (e) {
      Logger.log(`Error sending reminder to ${emp.name}: ${e}`);
    }
  });
}

function aggregateData() {
  const ss = getSpreadsheet();
  const now = new Date();
  if (now.getDate() !== CONFIG.AGGREGATION_DAY) return;

  let summarySheet = ss.getSheetByName(CONFIG.SHEET_NAMES.SUMMARY);
  if (!summarySheet) {
    summarySheet = ss.insertSheet(CONFIG.SHEET_NAMES.SUMMARY);
    summarySheet.getRange(1, 1, 1, 7).setValues([["Måned", "Medarbejder", "Email", "Ferie/Fridage", "Sygedage", "Feriedage", "Sidst opdateret"]]);
  }

  const employees = getActiveEmployees();
  const allData = [];
  const monthNames = [];

  // Get all monthly tabs from employee sheets
  employees.forEach(emp => {
    if (!emp.sheetId) return;
    try {
      const empSs = SpreadsheetApp.openById(emp.sheetId);
      const sheets = empSs.getSheets();
      sheets.forEach(sheet => {
        if (sheet.getName() !== "Info" && /^\d{4}-\d{2}$/.test(sheet.getName())) {
          monthNames.push(sheet.getName());
          const data = sheet.getDataRange().getValues();
          if (data[1]) {
            allData.push([
              sheet.getName(),
              emp.name,
              emp.email,
              data[1][0] || 0,
              data[1][1] || 0,
              data[1][2] || 0,
              data[1][4] || null
            ]);
          }
        }
      });
    } catch (e) {
      Logger.log(`Error aggregating data for ${emp.name}: ${e}`);
    }
  });

  if (allData.length > 0) {
    summarySheet.getRange(2, 1, summarySheet.getLastRow() - 1, 7).clearContent();
    summarySheet.getRange(2, 1, allData.length, 7).setValues(allData);
  }

  MailApp.sendEmail(
    CONFIG.ADMIN_EMAIL,
    `Timeregnskab opsummering - ${now.getMonth() + 1}/${now.getFullYear()}`,
    `Hej Admin,\n\nData er samlet i Summary fanen: ${ss.getUrl()}\n\nVenlig hilsen,\nTimeregnskab Script`
  );
}

function sendWelcomeEmails() {
  const employees = getActiveEmployees();
  employees.forEach(emp => {
    if (!emp.sheetId) return;
    const subject = CONFIG.EMAIL.WELCOME_SUBJECT;
    const body = CONFIG.EMAIL.WELCOME_BODY
      .replace("{name}", emp.name)
      .replace("{sheetUrl}", `https://docs.google.com/spreadsheets/d/${emp.sheetId}`);
    MailApp.sendEmail(emp.email, subject, body);
  });
}

function setup() {
  getEmployeesSheet();
  ensureEmployeeSheets();
  createMonthlyTabForAll();

  let summarySheet = getSpreadsheet().getSheetByName(CONFIG.SHEET_NAMES.SUMMARY);
  if (!summarySheet) {
    summarySheet = getSpreadsheet().insertSheet(CONFIG.SHEET_NAMES.SUMMARY);
    summarySheet.getRange(1, 1, 1, 7).setValues([["Måned", "Medarbejder", "Email", "Ferie/Fridage", "Sygedage", "Feriedage", "Sidst opdateret"]]);
  }

  Logger.log("Setup complete. Add employees to Employees sheet, then run ensureEmployeeSheets() and createMonthlyTabForAll()");
}
