function TableEditor(tbody) {
  // Allocate an array big enough to hold all rows.
  this.tbody = tbody;
  this.table = Array(tbody.rows.length);

  // Count the number of columns.
  var n_cols = 0;
  var cells  = tbody.rows[0].cells;
  for (var i = 0; i < cells.length; i++) {
    var colspan = cells[i].getAttribute('colspan');
    colspan     = colspan ? colspan : 1;
    n_cols      = n_cols + colspan;
  }

  // Allocate space for all cells.
  for (var i = 0; i < tbody.rows.length; i++)
    this.table[i] = Array(n_cols);

  // Read the current table structure into a two-dimensional array.
  for (var i = 0; i < tbody.rows.length; i++) {
    var cells   = tbody.rows[i].cells;
    var cur_col = 0;

    // Walk through all cells that start in the current row.
    for (var j = 0; j < cells.length; j++) {
      // If the current row is already occupied (this happens when a cell
      // in the row above has a rowspan > 1), skip to the next free slot.
      while (this.table[i][cur_col])
        cur_col++;

      // If the current cell has a colspan/rowspan, also assign it to the
      // following rows.
      rowspan = cells[j].getAttribute('rowspan');
      colspan = cells[j].getAttribute('colspan');
      rowspan = rowspan ? rowspan : 1;
      colspan = colspan ? colspan : 1;
      for (var k = 0; k < rowspan; k++)
        for (var l = 0; l < colspan; l++)
          this.table[i + k][cur_col + l] = cells[j];
    }
  }
}

TableEditor.prototype.table;
TableEditor.prototype.tbody;

// Print the iternal table structure for debugging.
TableEditor.prototype.dump_table = function() {
  var str = '';
  for (var i = 0; i < this.get_n_rows(); i++) {
    for (var j = 0; j < this.get_n_columns(); j++)
      str = str + this.get_cell(i, j).innerHTML + '|';
    str = str + "\n";
  }
  alert("Table debug:\n\n" + str);
}

// Returns the row number of the given tr element.
TableEditor.prototype.get_row_number = function(row) {
  var row_number = 0;
  var sibling    = row;
  while (sibling = sibling.previousSibling)
    if (sibling.nodeType == 1)
      row_number = row_number + 1;
  return row_number;
}

// Returns the number of rows in this table.
TableEditor.prototype.get_n_rows = function() {
  return this.table.length;
}

// Returns the number of columns in this table.
TableEditor.prototype.get_n_columns = function() {
  return this.table[0].length;
}

// Returns the td element at the given position.
TableEditor.prototype.get_cell = function(row_number, col_number) {
  return this.table[row_number][col_number];
}

// Returns the previous sibling that is an element.
TableEditor.prototype.get_previous_row = function(row) {
  if (!row)
    return null;
  while (row = row.previousSibling)
    if (row.nodeType == 1)
      break;
  return row;
}

// Returns the next sibling that is an element.
TableEditor.prototype.get_next_row = function(row) {
  if (!row)
    return null;
  while (row = row.nextSibling)
    if (row.nodeType == 1)
      break;
  return row;
}

// Returns a list [a,b], where a is the row number and b is the column
// number of the given cell. Returns null if the cell was not found.
TableEditor.prototype.find_cell = function(cell) {
  for (var i = 0; i < this.table.length; i++)
    for (var j = 0; j < this.table[i].length; j++)
      if (this.table[i][j] == cell)
        return [i, j];
  return null;
}

// Splits a cell horizontally by a) increasing the rowspan of other cells
// in the row and b) inserting the new td element below the given cell.
//FIXME: At this time, this can (maybe?) only split cells that have no rowspan.
TableEditor.prototype.hsplit_cell = function(cell) {
  var pos = this.find_cell(cell);

  // Start by increasing the rowspan of the cells.
  for (var i = 0; i < this.get_n_columns(); i++) {
    var current_cell = this.table[pos[0]][i];
    if (current_cell == cell)
      continue;
    rowspan = current_cell.getAttribute('rowspan');
    colspan = current_cell.getAttribute('colspan');
    rowspan = rowspan ? rowspan : 1;
    colspan = colspan ? colspan : 1;
    current_cell.setAttribute('rowspan', rowspan + 1);
    i += colspan - 1;
  }

  // Reflect the change in our table array. Copy the row of the given
  // cell, and shift down all others.
  var last_row = this.table[pos[0]];
  for (var i = pos[0]; i < this.get_n_rows(); i++) {
    var row = this.table[i];
    this.table[i] = last_row;
    last_row = row;
  }
  this.table.push(last_row);

  // Create the new row in the table.
  row      = cell.parentNode;
  next_row = this.get_next_row(row);
  new_row  = document.createElement('tr');
  new_cell = document.createElement('td');
  colspan  = cell.getAttribute('colspan');
  colspan  = colspan ? colspan : 1;
  new_cell.setAttribute('colspan', colspan);
  new_row.appendChild(new_cell);
  if (next_row)
    this.tbody.insertBefore(new_row, next_row);
  else
    this.tbody.appendChild(new_row);

  // Again, make the same change in our table array.
  for (var i = 0; i < colspan; i++)
    this.table[pos[0]][pos[1] + i] = new_cell;
}

// Adds a new column to the table before the given cell. If no cell is given,
// the new column is appended to table.
TableEditor.prototype.add_column_before = function(cell) {
  // Create the new cell.
  var row    = this.tbody.rows[0];
  var new_td = document.createElement('td');
  new_td.setAttribute('rowspan', this.table.length);

  // Append it to the table and to the table array.
  if (!cell) {
    row.appendChild(new_td);
    for (var i = 0; i < this.table.length; i++)
      this.table[i].push(new_td);
    return new_td;
  }

  // Find the right cell in the first row.
  var pos           = this.find_cell(cell);
  var column_number = pos[1];
  next_cell = this.table[0][column_number];
  //alert("asdasd:" + row + ":" + pos[1] + "/" + next_cell);
  row.insertBefore(new_td, next_cell);

  // Insert into the table array.
  for (var i = 0; i < this.table.length; i++) {
    var last_cell = new_td;
    var length    = this.get_n_columns();
    for (var j = 0; j < length; j++) {
      var cell         = this.table[i][j];
      this.table[i][j] = last_cell;
      last_cell        = cell;
    }
    this.table[i].push(last_cell);
  }
  return new_td;
}

// Adds a new row to the table before the given row. If no row is given,
// the new row is appended to table.
TableEditor.prototype.add_row_before = function(row) {
  // Create the row.
  new_row  = document.createElement('tr');
  new_cell = document.createElement('td');
  new_cell.setAttribute('colspan', this.get_n_columns());
  new_row.appendChild(new_cell);
  
  // Prepare a row for our table array.
  cells = new Array();
  for (var i = 0; i < this.table[0].length; i++)
    cells.push(new_cell);

  // Append as the last row.
  if (!row) {
    this.tbody.appendChild(new_row);
    this.table.push(cells);
    return new_row;
  }

  // Insert the new row.
  this.tbody.insertBefore(new_row, row);
  var row_number = this.get_row_number(row);
  var last_row = cells;
  for (var i = row_number - 1; i < this.table.length; i++) {
    var row = this.table[i];
    this.table[i] = last_row;
    last_row = row;
  }
  this.table.push(last_row);

  return new_row;
}
