function onEdit(e) {
  var sheetName = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getName();
  var range = e.range;
  var row = range.getRow();
  var column = range.getColumn();
  // Check if edited column was the checkbox column
  var columnHeader = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(1, column).getValue().toString();
  // Check if sheet is a translation sheet
  if (
    sheetName == 'French' ||
    sheetName == 'German' ||
    sheetName == 'Italian' ||
    sheetName == 'Polish' ||
    sheetName == 'Portuguese' ||
    sheetName == 'Spanish'
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

function cellDifferences(oldValue, newValue) {
  // Display human-readable differences for the cells
  var oldLines = oldValue.trim().split('\n').map(function(line) {
    line = line.replace(/^\-/, ' -').replace(/^\+/, ' +');
    return line;
  });
  var newLines = newValue.trim().split('\n').map(function(line) {
    line = line.replace(/^\-/, ' -').replace(/^\+/, ' +');
    return line;
  });

  var matches = 0;
  var left = [];
  var right = [];
  for (let i = 0; i < oldLines.length; i++) {
    let leftLine = oldLines[i];
    if (newLines.includes(leftLine)) {
      while (newLines.length) {
        let rightLine = newLines.shift();
        if (leftLine == rightLine) {
          left.push(leftLine);
          right.push(rightLine);
          matches += 1;
          break;
        }
        right.push('+ ' + rightLine);
      }
    }
    else {
      left.push('- '+ leftLine);
    }
  }

  for (let i = 0; i < newLines.length; i++) {
    right.push('+ ' + newLines[i]);
  }

  var leftValue = left.join('\n').trim();
  if (!leftValue) {
    leftValue = ' ';
  }
  var rightValue = right.join('\n').trim();
  if (!rightValue) {
    rightValue = ' ';
  }

  var oldLines = oldValue.trim().split('\n').map(function(line) {
    line = line.replace(/^\-/, ' -').replace(/^\+/, ' +');
    return line;
  });
  var newLines = newValue.trim().split('\n').map(function(line) {
    line = line.replace(/^\-/, ' -').replace(/^\+/, ' +');
    return line;
  });

  var matchesAlt = 0;
  var leftAlt = [];
  var rightAlt = [];
  for (let i = 0; i < newLines.length; i++) {
    let rightLine = newLines[i];
    if (oldLines.includes(rightLine)) {
      while (oldLines.length) {
        let leftLine = oldLines.shift();
        if (rightLine == leftLine) {
          rightAlt.push(rightLine);
          leftAlt.push(leftLine);
          matchesAlt += 1;
          break;
        }
        leftAlt.push('- ' + leftLine);
      }
    }
    else {
      rightAlt.push('+ ' + rightLine);
    }
  }

  for (let i = 0; i < oldLines.length; i++) {
    leftAlt.push('- ' + oldLines[i]);
  }

  var leftValueAlt = leftAlt.join('\n').trim();
  if (!leftValueAlt) {
    leftValueAlt = ' ';
  }
  var rightValueAlt = rightAlt.join('\n').trim();
  if (!rightValueAlt) {
    rightValueAlt = ' ';
  }

  var res;
  if (matchesAlt > matches) {
    res = [leftValueAlt, rightValueAlt];
  }
  else {
    res = [leftValue, rightValue];
  }
  return res;
}

function differences(value1, value2) {
  // Display human-readable differences for the rows
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
    let diffs = cellDifferences(valueArr1[i], valueArr2[i]);
    res += '  OLD\n' + diffs[0] + '\n  NEW\n' + diffs[1] + '\n\n';
  }
  return res.trim();
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