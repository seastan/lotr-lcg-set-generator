function onEdit(e) {
  var sheetName = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getName();

  // Check if sheet is a translation sheet
  if (
    sheetName == "Template" ||
    sheetName == "Italian" ||
    sheetName == "French" ||
    sheetName == "German" ||
    sheetName == "Spanish" ||
    sheetName == "Polish"
  ) {
    var range = e.range;
    var row = range.getRow();
    var column = range.getColumn();
    // Check if edited column was the checkbox column
    var columnHeader = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(1, column).getValue().toString();
    if(columnHeader == "Updated") {
      // Check if the checkbox was changed to TRUE
      var check = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row,column).getValue();
      if (check==true) {
        // Get current snapshot
        var currentSnapshot = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, getColumnByName('Current Snapshot')).getValue();
        // Copy it over to previous snapshot
        SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, getColumnByName('Last Snapshot')).setValue(currentSnapshot);
        // Set checkbox to FALSE
        SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).setValue(false);
      }
    }
  }
}

function getColumnByName(columnName) {
  // Return column index by its name
  var data = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getDataRange().getValues();
  var col = data[0].indexOf(columnName) + 1;
  return col;
}