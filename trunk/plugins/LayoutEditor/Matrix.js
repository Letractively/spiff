function Matrix(n_rows, n_cells, args) {
  // Create the initial table.
  this.table  = document.createElement('table');
  var _tbody  = document.createElement('tbody');
  var _matrix = null;
  this.table.appendChild(_tbody);


  // Removes the given cell from the table without adding a new one.
  this._remove_cell = function(cell) {
    var pos        = this.find_cell(cell);
    var row_number = pos[0];
    var col_number = pos[1];
    var rowspan    = cell.getAttribute('rowspan');
    var colspan    = cell.getAttribute('colspan');
    rowspan = rowspan ? parseInt(rowspan) : 1;
    colspan = colspan ? parseInt(colspan) : 1;
    _tbody.rows[row_number].removeChild(cell);
    for (var i = row_number; i < row_number + rowspan; i++)
      for (var j = col_number; j < col_number + colspan; j++)
        _matrix[i][j] = null;
  }


  // Removes all cells and replaces itself by a new matrix
  // with the given rows, cells and attributes.
  this.reset = function(n_rows, n_cells, args) {
    _matrix = Array(Array());

    // Set given default attributes.
    for (var key in args)
      this.set_attribute(key, args[key]);

    // Remove existing rows.
    while (_tbody.rows.length > 0)
      _tbody.removeChild(_tbody.rows[0]);

    // Append rows and cells.
    for (var i = 0; i < n_rows; i++) {
      var tr = document.createElement('tr');
      _tbody.appendChild(tr);
      for (var j = 0; j < n_cells; j++) {
        var td = document.createElement('td');
        tr.appendChild(td);
        _matrix[i][j] = td;
      }
    }
  }


  // Returns the previous sibling that is an element.
  this.get_previous_row = function(row) {
    if (!row)
      return null;
    while (row = row.previousSibling)
      if (row.nodeType == 1)
        break;
    return row;
  }


  // Returns the next sibling that is an element.
  this.get_next_row = function(row) {
    if (!row)
      return null;
    while (row = row.nextSibling)
      if (row.nodeType == 1)
        break;
    return row;
  }


  // Returns the row number of the given tr element.
  this.get_row_number = function(row) {
    var row_number = 0;
    var sibling    = row;
    while (sibling = sibling.previousSibling)
      if (sibling.nodeType == 1)
        row_number = row_number + 1;
    return row_number;
  }
  

  // Returns the number of rows.
  this.get_n_rows = function() {
    return _matrix.length;
  }


  // Returns the number of columns.
  this.get_n_columns = function() {
    return _matrix[0].length;
  }


  // Returns class of the table element.
  this.get_class = function() {
    var class = this.table.getAttribute('class');
    return class ? class : '';
  }


  // Sets an attribute on the table of the matrix.
  this.set_attribute = function(key, value) {
    this.table.setAttribute(key, value);
  }


  // Returns the td element from the given position.
  this.get_cell = function(row_number, col_number) {
    return _matrix[row_number][col_number];
  }


  // Defines the attribute of the td element on the given position.
  this.set_cell_attribute = function(row_number,
                                                 col_number,
                                                 key,
                                                 value) {
    var cell = this.get_cell(row_number, col_number);
    cell.setAttribute(key, value);
  }


  // Returns attribute of the td element from the given position.
  this.get_cell_attribute = function(row_number, col_number, key) {
    var cell  = this.get_cell(row_number, col_number);
    var value = cell ? cell.getAttribute(key) : '';
    return value ? value : '';
  }


  // Defines the class of the td element on the given position.
  this.set_cell_class = function(row_number,
                                             col_number,
                                             class) {
    this.set_cell_attribute(row_number, col_number, 'class', class);
  }


  // Returns class of the td element from the given position.
  this.get_cell_class = function(row_number, col_number) {
    return this.get_cell_attribute(row_number, col_number, 'class');
  }


  // Adds the given string into the td element on the given position.
  this.set_cell_html = function(row_number,
                                            col_number,
                                            html) {
    var cell = this.get_cell(row_number, col_number);
    cell.innerHTML = html;
  }


  // Returns content of the td element on the given position.
  this.get_cell_html = function(row_number, col_number) {
    var cell = this.get_cell(row_number, col_number);
    var html = cell ? cell.innerHTML : '';
    return html ? html : '';
  }


  // Print the matrix for debugging.
  this.dump = function() {
    var dump = '';
    for (var i = 0; i < this.get_n_rows(); i++) {
      dump += i + ':';
      for (var j = 0; j < this.get_n_columns(); j++) {
        var cell  = this.get_cell(i, j);
        var id    = cell.getAttribute('id');
        var class = cell.getAttribute('class');
        var txt   = id ? id : (class ? class : cell);
        dump = dump + '[' + txt + ']';
      }
      dump += "\n";
    }
    alert("Debug:\n\n" + dump);
  }


  // Returns a list [a,b], where a is the row number and b is the column
  // number of the given cell. Returns null if the cell was not found.
  this.find_cell = function(cell) {
    for (var i = 0; i < this.get_n_rows(); i++)
      for (var j = 0; j < this.get_n_columns(); j++)
        if (this.get_cell(i, j) == cell)
          return [i, j];
    return null;
  }


  // Adds a new column, positioned before the given cell. If no cell is given,
  // the new column is appended.
  // Returns the column number of the new column.
  this.add_column_before = function(cell) {
    // Append to the table and to the matrix.
    if (!cell) {
      for (var i = 0; i < this.get_n_rows(); i++) {
        var new_td = document.createElement('td');
        _tbody.rows[i].appendChild(new_td);
        _matrix[i].push(new_td);
      }
      return this.get_n_columns();
    }

    // Find the right cell.
    var pos           = this.find_cell(cell);
    var column_number = pos[1];

    // Insert the new cells into every row.
    for (var i = 0; i < this.get_n_rows(); i++) {
      var new_td = document.createElement('td');
      next_cell  = this.get_cell(i, column_number);
      _tbody.rows[i].insertBefore(new_td, next_cell);

      // Insert the cell into our matrix.
      var last_cell = new_td;
      var length    = this.get_n_columns();
      for (var j = 0; j < length; j++) {
        var cell      = this.get_cell(i, j);
        _matrix[i][j] = last_cell;
        last_cell     = cell;
      }
      _matrix[i].push(last_cell);
    }
    
    return column_number;
  }


  // Adds a new row, positioned before the given row. The new row consists of
  // only one cell with a colspan. If no row is given, the new row is appended.
  // Returns the newly created *cell*.
  this.add_row_before_with_colspan = function(row) {
    // Create the row.
    new_row  = document.createElement('tr');
    new_cell = document.createElement('td');
    new_cell.setAttribute('colspan', this.get_n_columns());
    new_row.appendChild(new_cell);
    
    // Prepare a row for our matrix.
    cells = new Array();
    for (var i = 0; i < this.get_n_columns(); i++)
      cells.push(new_cell);

    // Append as the last row.
    if (!row) {
      _tbody.appendChild(new_row);
      _matrix.push(cells);
      return new_cell;
    }

    // Insert the new row.
    _tbody.insertBefore(new_row, row);
    var row_number = this.get_row_number(row);
    var last_row   = cells;
    for (var i = row_number - 1; i < this.get_n_rows(); i++) {
      var row = _matrix[i];
      _matrix[i] = last_row;
      last_row = row;
    }
    _matrix.push(last_row);

    return new_cell;
  }


  // Adds a new column, positioned before the given cell. The new column consist
  // of one single cell with a rowspan. If no cell is given, the new column is
  // appended to table.
  // Returns the new cell.
  this.add_column_before_with_rowspan = function(cell) {
    // Create the new cell.
    var row    = _tbody.rows[0];
    var new_td = document.createElement('td');
    new_td.setAttribute('rowspan', this.table.length);

    // Append it to the table and to the matrix.
    if (!cell) {
      row.appendChild(new_td);
      for (var i = 0; i < this.get_n_rows(); i++)
        _matrix[i].push(new_td);
      return new_td;
    }

    // Find the right cell in the first row.
    var pos           = this.find_cell(cell);
    var column_number = pos[1];
    next_cell         = this.get_cell(0, column_number);
    row.insertBefore(new_td, next_cell);

    // Insert into the matrix.
    for (var i = 0; i < this.get_n_rows(); i++) {
      var last_cell = new_td;
      var length    = this.get_n_columns();
      for (var j = 0; j < length; j++) {
        var cell           = this.get_cell(i, j);
        _matrix[i][j] = last_cell;
        last_cell          = cell;
      }
      _matrix[i].push(last_cell);
    }
    return new_td;
  }


  // Splits a cell horizontally. The original content will be in the upper half.
  // Returns the td of the lower half.
  this.hsplit_cell = function(cell) {
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
      var next_row         = _tbody.rows[next_row_number];
      var next_cell        = this.get_cell(next_row_number, next_cell_number);
      new_cell.setAttribute('colspan', colspan);
      next_row.insertBefore(new_cell, next_cell);
      
      // Update matrix.
      for (var i = pos[1]; i < pos[1] + colspan; i++)
        _matrix[next_row_number][i] = new_cell;
      return new_cell;
    }

    // Ending up here, the given cell has no rowspan. We must start by
    // increasing the rowspan of the cells.
    for (var i = 0; i < this.get_n_columns(); i++) {
      var current_cell = this.get_cell(pos[0], i);
      if (current_cell == cell)
        continue;
      rowspan = current_cell.getAttribute('rowspan');
      colspan = current_cell.getAttribute('colspan');
      rowspan = rowspan ? parseInt(rowspan) : 1;
      colspan = colspan ? parseInt(colspan) : 1;
      current_cell.setAttribute('rowspan', rowspan + 1);
      i += colspan - 1;
    }

    // Reflect the change in our matrix. Copy the row of the given
    // cell, and shift down all others.
    var last_row = _matrix[pos[0]].slice();
    for (var i = pos[0]; i < this.get_n_rows(); i++) {
      var row = _matrix[i];
      _matrix[i] = last_row;
      last_row = row;
    }
    _matrix.push(last_row);

    // Create the new row in the table.
    var row      = cell.parentNode;
    var colspan  = cell.getAttribute('colspan');
    var next_row = this.get_next_row(row);
    var new_row  = document.createElement('tr');
    var new_cell = document.createElement('td');
    colspan      = colspan ? parseInt(colspan) : 1;
    new_cell.setAttribute('colspan', colspan);
    new_row.appendChild(new_cell);
    if (next_row)
      _tbody.insertBefore(new_row, next_row);
    else
      _tbody.appendChild(new_row);

    // Again, make the same change in our matrix.
    for (var i = 0; i < colspan; i++)
      _matrix[pos[0] + 1][pos[1] + i] = new_cell;

    return new_cell;
  }


  // Joins the given cells together by removing the second one and
  // increasing the colspan (or rowspan) of the first cell.
  this.join_cells = function(cell1, cell2) {
    var pos1          = this.find_cell(cell1);
    var pos2          = this.find_cell(cell2);
    var row_number1   = pos1[0];
    var col_number1   = pos1[1];
    var row_number2   = pos2[0];
    var col_number2   = pos2[1];
    var row1          = _tbody.rows[row_number1];
    var row2          = _tbody.rows[row_number2];
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

      // Update matrix.
      for (var i = row_number1; i < row_number1 + rowspan1; i++)
        for (var j = first_col; j < last_col; j++)
          _matrix[i][j] = cell1;
    }

    // If both cells are in the same column.
    else {
      // Find the next cell.
      var first_row = row_number1 < row_number2 ? row_number1 : row_number2;
      var next_cell = this.get_cell(first_row, col_number1 + colspan1);
      
      // Re-insert the cell.
      cell1.setAttribute('rowspan', rowspan1 + rowspan2);
      _tbody.rows[first_row].insertBefore(cell1, next_cell);

      // Update matrix.
      for (var i = first_row; i < first_row + rowspan1 + rowspan2; i++)
        for (var j = col_number1; j < col_number1 + colspan1; j++)
          _matrix[i][j] = cell1;
    }
  }


  // Returns a description of the current layout in a layout language.
  this.get_layout = function() {
    var class  = this.get_class();
    var layout = '<table class="' + class + '"><tbody>';
    for (var i = 0; i < _tbody.rows.length; i++) {
      layout += '<tr>';
      for (var j = 0; j < _tbody.rows[i].cells.length; j++) {
        var cell    = _tbody.rows[i].cells[j];
        var rowspan = cell.getAttribute('rowspan');
        var colspan = cell.getAttribute('colspan');
        rowspan = rowspan ? parseInt(rowspan) : 1;
        colspan = colspan ? parseInt(colspan) : 1;
        layout += '<td rowspan="' + rowspan + '" colspan="' + colspan + '">';
        layout += cell.innerHTML;
        layout += '</td>';
      }
      layout += '</tr>\n';
    }
    return layout + '</tbody></table>';
  }


  this.set_attribute('width', '100%');
  this.reset(n_rows, n_cells, args);
}


Matrix.prototype.table;
