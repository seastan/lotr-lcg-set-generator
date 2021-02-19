function onEdit(e) {
  var sheetName = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getName();

  // Check if sheet is a translation sheet
  if (
    sheetName == "Snapshot" ||
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
      var check = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).getValue();
      if (check==true) {
        // Get current snapshot
        var currentSnapshot = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, getColumnByName('Current Snapshot')).getValue();
        // Copy it over to previous snapshot
        SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, getColumnByName('Last Snapshot')).setValue('=concatenate("' + currentSnapshot.replace(/"/g, '", char(34), "') + '")');
        // Set checkbox to FALSE
        SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).setValue(false);
      }
    }
    else if(columnHeader == "Diff") {
      var check = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).getValue();
      if (check==true) {
        var currentSnapshot = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, getColumnByName('Current Snapshot')).getValue();
        var lastSnapshot = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, getColumnByName('Last Snapshot')).getValue();
        var diff = differences(lastSnapshot, currentSnapshot);
        if (diff) {
          SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).setNote(diff);
        }
        else {
          SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).clearNote();
        }
        SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).setValue(false);
      }
    }
  }

  if (e.range.getFormula().toUpperCase() == "=UUID()") {
    e.range.setValue(Utilities.getUuid());
  }

}

function uuid() {
  // Return UUID placeholder
  return '';
}

function UUID() {
  // Return UUID placeholder
  return '';
}

function getColumnByName(columnName) {
  // Return column index by its name
  var data = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getDataRange().getValues();
  var col = data[0].indexOf(columnName) + 1;
  return col;
}

function differences(value1, value2) {
  // Display human-readable differences
  var columns = ['Name', 'Traits', 'Keywords', 'Victory Points', 'Text', 'Shadow', 'Flavour',
                 'Side B', 'Traits (Side B)', 'Keywords (Side B)', 'Victory Points (Side B)',
                 'Text (Side B)', 'Shadow (Side B)', 'Flavour (Side B)', 'Adventure (Side B)'];

  if (value1 == value2) {
    return '';
  }

  if (!value1) {
    return 'No previous version of the row yet.';
  }
  
  var valueArr1 = value1.split('|');
  var valueArr2 = value2.split('|');
  if (valueArr1.length != valueArr2.length) {
    return 'ERROR: Incorrect Last Snapshot value.';
  }

  var res = '';
  for (let i = 0; i < valueArr1.length; i++) {
    if (valueArr1[i].trim() == valueArr2[i].trim()) {
      continue;
    }
    res += columns[i] + ':\n';
    let valueSubArr1 = valueArr1[i].split('\n');
    let valueSubArr2 = valueArr2[i].split('\n');
    while (valueSubArr1.length > valueSubArr2.length) {
      valueSubArr2.push('');
    }
    while (valueSubArr2.length > valueSubArr1.length) {
      valueSubArr1.push('');
    }
    for (let j = 0; j < valueSubArr1.length; j++) {
      if (valueSubArr1[j].trim() == valueSubArr2[j].trim()) {
        continue;
      }
      res += 'OLD: ' + valueSubArr1[j].trim() + '\n';
      res += 'NEW: ' + valueSubArr2[j].trim() + '\n';
      res += '\n';
    }
  }

  return res;
}