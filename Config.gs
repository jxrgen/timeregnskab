// Config.gs
const CONFIG = {
  REMINDER_DAY: 20,
  AGGREGATION_DAY: 25,
  ADMIN_EMAIL: "admin@example.com", // Replace with your admin email
  MASTER_SHEET_NAME: "Master",
  SHEET_NAMES: {
    EMPLOYEES: "Employees",
    SUMMARY: "Summary"
  },
  EMAIL: {
    REMINDER_SUBJECT: "Påmindelse: Udfyld timeregnskab for {month}",
    REMINDER_BODY: "Hej {name},\n\nDu har endnu ikke udfyldt dit timeregnskab for {month}.\nFristen er den {deadline}., så husk at udfylde det her: {sheetUrl}\n\nVenlig hilsen,\nAdministrationen",
    WELCOME_SUBJECT: "Dit timeregnskab er klar",
    WELCOME_BODY: "Hej {name},\n\nDit personlige timeregnskab er oprettet: {sheetUrl}\n\nHer kan du indtaste dine feriedage, sygedage og feriefridage for hver måned.\nNår du har udfyldt en måned, skal du markere 'Udfyldt'.\n\nVenlig hilsen,\nAdministrationen"
  }
};
