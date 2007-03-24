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
    for (var j = 0; j < this.get_n_columns(); j++) {
      var cell = this.get_cell(i, j);
      if (!cell) {
        str = str + '|| ';
        continue;
      }
      var html = cell.innerHTML.replace(/^\s*/, '').replace(/\s*$/, '');
      str = str + '|' + html + '| ';
    }
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
// Returns the newly created cell.
TableEditor.prototype.hsplit_cell = function(cell) {
  var pos     = this.find_cell(cell);
  var rowspan = cell.getAttribute('rowspan');
  var colspan = cell.getAttribute('colspan');
  rowspan     = rowspan ? parseInt(rowspan) : 1;
  colspan     = colspan ? parseInt(colspan) : 1;

  // If the cell already has rowspan, we only need to reduce it and add a
  // new cell.
  if (rowspan > 1) {
    cell.setAttribute('rowspan', rowspan - 1);
    var new_cell         = document.createElement('td');
    var next_row_number  = pos[0] + rowspan - 1;
    var next_cell_number = pos[1] + colspan;
    var next_row         = this.tbody.rows[next_row_number];
    var next_cell        = this.get_cell(next_row_number, next_cell_number);
    new_cell.setAttribute('colspan', colspan);
    next_row.insertBefore(new_cell, next_cell);
    
    // Update table array.
    for (var i = pos[1]; i < pos[1] + colspan; i++)
      this.table[next_row_number][i] = new_cell;
    return new_cell;
  }

  // Ending up here, the given cell has no rowspan. We must start by
  // increasing the rowspan of the cells.
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
  var last_row = this.table[pos[0]].slice();
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
  new_cell.setAttribute('colspan', colspan);
  new_row.appendChild(new_cell);
  if (next_row)
    this.tbody.insertBefore(new_row, next_row);
  else
    this.tbody.appendChild(new_row);

  // Again, make the same change in our table array.
  for (var i = 0; i < colspan; i++)
    this.table[pos[0] + 1][pos[1] + i] = new_cell;

  return new_cell;
}

// Adds a new column to the table before the given cell. If no cell is given,
// the new column is appended to table.
// Returns the new column number.
TableEditor.prototype.add_column_before = function(cell) {
  // Append to the table and to the table array.
  if (!cell) {
    for (var i = 0; i < this.get_n_rows(); i++) {
      var new_td = document.createElement('td');
      this.tbody.rows[i].appendChild(new_td);
      this.table[i].push(new_td);
    }
    return this.get_n_columns();
  }

  // Find the right cell in the first row.
  var pos           = this.find_cell(cell);
  var column_number = pos[1];

  // Insert the new cells into every row.
  for (var i = 0; i < this.get_n_rows(); i++) {
    var new_td = document.createElement('td');
    next_cell  = this.table[i][column_number];
    this.tbody.rows[i].insertBefore(new_td, next_cell);

    // Insert the cell into our table structure.
    var last_cell = new_td;
    var length    = this.get_n_columns();
    for (var j = 0; j < length; j++) {
      var cell         = this.table[i][j];
      this.table[i][j] = last_cell;
      last_cell        = cell;
    }
    this.table[i].push(last_cell);
  }
  
  return column_number;
}

// Adds a new column to the table before the given cell. If no cell is given,
// the new column is appended to table.
// The new column consist out of one single cell with a rowspan.
TableEditor.prototype.add_column_before_with_rowspan = function(cell) {
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
  next_cell         = this.table[0][column_number];
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
// Returns the new *cell*.
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
    return new_cell;
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

  return new_cell;
}

// Removes the given cell from the table without adding a new one.
TableEditor.prototype._remove_cell = function(cell) {
  var pos        = this.find_cell(cell);
  var row_number = pos[0];
  var col_number = pos[1];
  var rowspan    = cell.getAttribute('rowspan');
  var colspan    = cell.getAttribute('colspan');
  rowspan = rowspan ? parseInt(rowspan) : 1;
  colspan = colspan ? parseInt(colspan) : 1;
  this.tbody.rows[row_number].removeChild(cell);
  for (var i = row_number; i < row_number + rowspan; i++)
    for (var j = col_number; j < col_number + colspan; j++)
      this.table[i][j] = null;
}

// Joins the given cells together by removing the second one and
// increasing the colspan (or rowspan) of the first cell.
TableEditor.prototype.join_cells = function(cell1, cell2) {
  var pos1          = this.find_cell(cell1);
  var pos2          = this.find_cell(cell2);
  var row_number1   = pos1[0];
  var col_number1   = pos1[1];
  var row_number2   = pos2[0];
  var col_number2   = pos2[1];
  var row1          = this.tbody.rows[row_number1];
  var row2          = this.tbody.rows[row_number2];
  var rowspan1      = cell1.getAttribute('rowspan');
  var colspan1      = cell1.getAttribute('colspan');
  var rowspan2      = cell2.getAttribute('rowspan');
  var colspan2      = cell2.getAttribute('colspan');
  rowspan1 = rowspan1 ? parseInt(rowspan1) : 1;
  colspan1 = colspan1 ? parseInt(colspan1) : 1;
  rowspan2 = rowspan2 ? parseInt(rowspan2) : 1;
  colspan2 = colspan2 ? parseInt(colspan2) : 1;

  // Remove both cells first.
  this._remove_cell(cell1);
  this._remove_cell(cell2);

  // If both cells are in the same row, increase the colspan and add cell1
  // into the table again.
  if (row1 == row2) {
    // Find the next cell.
    var first_col = col_number1 < col_number2 ? col_number1 : col_number2;
    var last_col1 = col_number1 + colspan1;
    var last_col2 = col_number2 + colspan2;
    var last_col  = last_col1 > last_col2 ? last_col1 : last_col2;
    var next_cell = this.get_cell(row_number1, last_col);

    // Re-insert before the next cell.
    cell1.setAttribute('colspan', colspan1 + colspan2);
    row1.insertBefore(cell1, next_cell);

    // Update table array.
    for (var i = row_number1; i < row_number1 + rowspan1; i++)
      for (var j = first_col; j < last_col; j++)
        this.table[i][j] = cell1;
  }

  // If both cells are in the same column.
  else {
    // Find the next cell.
    var first_row = row_number1 < row_number2 ? row_number1 : row_number2;
    var next_cell = this.get_cell(first_row, col_number1 + colspan1);
    
    // Re-insert the cell.
    cell1.setAttribute('rowspan', rowspan1 + rowspan2);
    this.tbody.rows[first_row].insertBefore(cell1, next_cell);

    // Update table array.
    for (var i = first_row; i < first_row + rowspan1 + rowspan2; i++)
      for (var j = col_number1; j < col_number1 + colspan1; j++)
        this.table[i][j] = cell1;
  }
}

