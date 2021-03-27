function onEdit(e) {
  var sheetName = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getName();
  var range = e.range;
  var row = range.getRow();
  var column = range.getColumn();
  // Check if edited column was the checkbox column
  var columnHeader = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(1, column).getValue().toString();
  // Check if sheet is a translation sheet
  if (
    sheetName == 'Snapshot' ||
    sheetName == 'Italian' ||
    sheetName == 'French' ||
    sheetName == 'German' ||
    sheetName == 'Spanish' ||
    sheetName == 'Polish'
  ) {
    if (columnHeader == 'Updated') {
      // Check if the checkbox was changed to TRUE
      var check = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).getValue();
      if (check == true) {
        // Get current snapshot
        var currentSnapshot = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, getColumnByName('Current Snapshot')).getValue();
        // Copy it over to previous snapshot
        SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, getColumnByName('Last Snapshot')).setValue('=concatenate("' + currentSnapshot.replace(/"/g, '", char(34), "') + '")');
        // Set checkbox to FALSE
        SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).setValue(false);
      }
    }
    else if (columnHeader == 'Diff') {
      var check = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).getValue();
      if (check == true) {
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

  if (e.range.getFormula().toUpperCase() == '=UUID()') {
    e.range.setValue(Utilities.getUuid());
  }

  if (sheetName == 'Card Data' && columnHeader == 'Text') {
    const lineLength = 50; // Average of characters per line
    var text = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, column).getValue();
    var lines = text.split('\n');
    var totalLines = 0;
    for (var line of lines) {
      // Count lines for images
      if (line.includes('Do-Not-Read')) {
        totalLines += 1;
      }
      else if (line.includes('Encounter-Icons')) {
        totalLines += 2;
      }
      else if (line.includes('Header-')) {
        totalLines += 0;
      }
      // Trim tags
      while (line.includes('[')) {
        const start = line.indexOf('[');
        const end = line.indexOf(']');
        line = cut(line, start, end);
      }
      // Count lines for text
      if (line.length == 0) {
        totalLines += 1; // Just a newline character
      }
      else {
        totalLines += Math.ceil(line.length / lineLength)
      }
    }
    var linecountCol;
    if (column < getColumnByName('Side B')) {
      linecountCol = getColumnByName('Side A linecount');
    }
    else {
      linecountCol = getColumnByName('Side B linecount');
    }
    SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(row, linecountCol).setValue(totalLines);
  }
}

function cut(str, cutStart, cutEnd) {
  // Cut the content between two characters
  return str.substr(0, cutStart) + str.substr(cutEnd + 1);
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

function SHEETS() {
  // Print the list of all sheets and their IDs
  var res = new Array();
  var sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();
  for (let i = 0; i < sheets.length; i++) {
    res.push([sheets[i].getName(), sheets[i].getSheetId()]);
  }
  return res;
}
