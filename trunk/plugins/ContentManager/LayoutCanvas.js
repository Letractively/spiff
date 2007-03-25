function LayoutCanvas(args) {
  this._args            = args;
  this._connected_ids   = Array();
  this.table            = null;
  var _last_highlighted = null;
  var _layout           = null;
  var _container_list   = null;

  // Create the initial tables.
  _layout = new Matrix(1, 1, {class: 'canvas'});
  this.table = _layout.table;
  _container_list = {
    header: new Matrix(1, 1, {class: 'container header'}),
    body:   new Matrix(1, 1, {class: 'container body'}),
    footer: new Matrix(1, 1, {class: 'container footer'}),
    left:   new Matrix(1, 1, {class: 'container left'}),
    right:  new Matrix(1, 1, {class: 'container right'})
  };


  // Makes all cells droppable that have the "droppable" class.
  // Also makes all cells listen to the onHover signal.
  this.connect_events = function() {
    this._disconnect_events();
    //FIXME: hardcoded id
    Droppables.add('content_editor', {
      accept:  this._args['accept_drop'],
      greedy:  true,
      onHover: this._on_hover
    });
    
    for (var key in _container_list) {
      var matrix = _container_list[key];
      if (!matrix.table.parentNode)
        continue;
      for (var j = 0; j < matrix.table.rows.length; j++) {
        for (var k = 0; k < matrix.table.rows[j].cells.length; k++) {
          var cell = matrix.table.rows[j].cells[k];
          var id   = key + '_' + j + '_' + k;
          this._connected_ids.push(id);
          cell.setAttribute('id', id);
          if (matrix.get_cell_class(j, k).match(/droppable/)) {
            Droppables.add(id, {
              accept:  this._args['accept_drop'],
              greedy:  true,
              onHover: this._on_hover,
              onDrop:  on_drop_closure(this)
            });
          }
          else {
            Droppables.add(id, {
              accept:  this._args['accept_drop'],
              greedy:  true,
              onHover: this._on_hover
            });
          }
        }
      }
    }
  }


  // Disconnects all signals.
  this._disconnect_events = function() {
    Droppables.remove('content_editor'); //FIXME: harcoded id
    for (var i = 0; i < this._connected_ids.length; i++) {
      var id = this._connected_ids[i];
      Droppables.remove(id);
    }
    this._connected_ids = Array();
  }


  // Called whenever an item is dragged over the canvas.
  // Highlights the cell over which the item was dragged and
  // removes highlighting from all others.
  this._on_hover = function(draggable, droppable) {
    if (droppable == _last_highlighted)
      return;

    // Remove the old highlighting.
    if (_last_highlighted) {
      var class = _last_highlighted.getAttribute('class');
      class = class.replace(/ highlight$/, '');
      _last_highlighted.setAttribute('class', class);
      _last_highlighted = null;
    }

    // Ignore cells that need not be highlighted.
    var class = droppable.getAttribute('class');
    if (!class || !class.match(/droppable/))
      return;
    
    // Highlight.
    droppable.setAttribute('class', class + ' highlight');
    _last_highlighted = droppable;
  }


  // This is necessary because JS sucks dick (method pointers/references
  // are really closures without a reference to the object).
  var on_drop_closure = function(obj) {
    return function(draggable, droppable) {
      return obj['_on_drop'](draggable, droppable);
    };
  }


  // Called whenever an item was dropped on the canvas.
  this._on_drop = function(draggable, droppable) {
    var table = droppable.parentNode.parentNode.parentNode;
    var row   = table.parentNode.parentNode;
    var class = table.getAttribute('class');
    if (!class)
      return;

    // If this is the first cell that is populated, extend the layout by adding
    // drag targets around it.
    if (_layout.get_n_rows() == 1 && _layout.get_n_columns() == 1) {
      var header        = _layout.add_row_before_with_colspan(row);
      var footer        = _layout.add_row_before_with_colspan();
      var right_col_num = _layout.add_column_before();
      var left_col_num  = _layout.add_column_before(table.parentNode);
      var top_right     = _layout.get_cell(0, right_col_num);
      var top_left      = _layout.get_cell(0, left_col_num);
      var right         = _layout.get_cell(1, right_col_num);
      var left          = _layout.get_cell(1, left_col_num);
      var bot_right     = _layout.get_cell(2, right_col_num);
      var bot_left      = _layout.get_cell(2, left_col_num);
      top_right.setAttribute('class', 'inactive');
      top_left.setAttribute('class', 'inactive');
      bot_right.setAttribute('class', 'inactive');
      bot_left.setAttribute('class', 'inactive');

      // Add the containers into the newly created cells.
      header.appendChild(_container_list['header'].table);
      footer.appendChild(_container_list['footer'].table);
      left.appendChild(_container_list['left'].table);
      right.appendChild(_container_list['right'].table);
    }

    // Join the cells in the layout so that the added item spans the maximum
    // possible number of cells.
    var matrix = _container_list['body'];
    if (class.match(/header/)) {
      matrix = _container_list['header'];
      var top_l       = _layout.get_cell(0, 0);
      var top_l_class = _layout.get_cell_class(0, 0);
      var top_m       = table.parentNode;
      var top_r       = _layout.get_cell(0, 2);
      var top_r_class = _layout.get_cell_class(0, 2);
      if (top_l_class.match(/inactive/))
        _layout.join_cells(top_m, top_l);
      if (top_r_class.match(/inactive/))
        _layout.join_cells(top_m, top_r);
    }
    else if (class.match(/footer/)) {
      matrix = _container_list['footer'];
      var bot_l       = _layout.get_cell(_layout.get_n_rows() - 1, 0);
      var bot_l_class = _layout.get_cell_class(_layout.get_n_rows() - 1, 0);
      var bot_m       = table.parentNode;
      var bot_r       = _layout.get_cell(_layout.get_n_rows() - 1, 2);
      var bot_r_class = _layout.get_cell_class(_layout.get_n_rows() - 1, 2);
      if (bot_l_class.match(/inactive/))
        _layout.join_cells(bot_m, bot_l);
      if (bot_r_class.match(/inactive/))
        _layout.join_cells(bot_m, bot_r);
    }
    else if (class.match(/left/)) {
      matrix = _container_list['left'];
      var top_l       = _layout.get_cell(0, 0);
      var top_l_class = _layout.get_cell_class(0, 0);
      var mid_l       = table.parentNode;
      var bot_l       = _layout.get_cell(_layout.get_n_rows() - 1, 0);
      var bot_l_class = _layout.get_cell_class(_layout.get_n_rows() - 1, 0);
      if (top_l_class.match(/inactive/))
        _layout.join_cells(mid_l, top_l);
      if (bot_l_class.match(/inactive/))
        _layout.join_cells(mid_l, bot_l);
    }
    else if (class.match(/right/)) {
      matrix = _container_list['right'];
      var top_r       = _layout.get_cell(0, 2);
      var top_r_class = _layout.get_cell_class(0, 2);
      var mid_r       = table.parentNode;
      var bot_r       = _layout.get_cell(_layout.get_n_rows() - 1, 2);
      var bot_r_class = _layout.get_cell_class(_layout.get_n_rows() - 1, 2);
      if (top_r_class.match(/inactive/))
        _layout.join_cells(mid_r, top_r);
      if (bot_r_class.match(/inactive/))
        _layout.join_cells(mid_r, bot_r);
    }

    // Now add the item into the target cell.
    droppable.style.height = '100px';
    droppable.style.width  = '100%';  //FIXME: Use plugin recommendation.
    droppable.innerHTML    = draggable.innerHTML;
    droppable.setAttribute('class', 'occupied');

    // Add a new droppable below it.
    var new_cell = matrix.hsplit_cell(droppable);
    new_cell.setAttribute('class', 'horizontal droppable');

    this.connect_events();
  }


  // Set default attributes.
  this.init = function() {
    _layout.get_cell(0, 0).appendChild(_container_list['body'].table);
    _layout.set_cell_class(0, 0, 'body');
    _container_list['header'].set_cell_class(0, 0, 'horizontal droppable');
    _container_list['footer'].set_cell_class(0, 0, 'horizontal droppable');
    _container_list['left'].set_cell_class(0, 0, 'vertical droppable');
    _container_list['right'].set_cell_class(0, 0, 'vertical droppable');
    _container_list['body'].set_cell_class(0, 0, 'droppable');
    _container_list['body'].set_cell_html(0, 0, 'Drag your content here');
  }


  // Clears out the canvas.
  this.reset = function() {
    this._disconnect_events();
    
    // Re-initialize the tables.
    _layout.reset(1, 1);
    for (var key in _container_list) {
      var parent = _container_list[key].table.parentNode;
      parent.removeChild(_container_list[key].table);
      _container_list[key].reset(1, 1);
    }
    this.init();
    this.connect_events();
  }


  // Returns a description of the current layout in a layout language.
  this.get_layout = function() {
    var layout = '<table><tbody>';
    var tbody  = _layout.get_cell(0, 0).parentNode.parentNode;
    for (var i = 0; i < tbody.rows.length; i++) {
      var row = '';
      for (var j = 0; j < tbody.rows[i].cells.length; j++) {
        var cell  = tbody.rows[i].cells[j];
        var table = cell.childNodes[0];
        if (!table)
          continue;
        var class   = table.getAttribute('class');
        var rowspan = cell.getAttribute('rowspan');
        var colspan = cell.getAttribute('colspan');
        rowspan = rowspan ? parseInt(rowspan) : 1;
        colspan = colspan ? parseInt(colspan) : 1;

        // Choose the matrix.
        var matrix = _container_list['body'];
        if (class.match(/header/))
          matrix = _container_list['header'];
        else if (class.match(/footer/))
          matrix = _container_list['footer'];
        else if (class.match(/left/))
          matrix = _container_list['left'];
        else if (class.match(/right/))
          matrix = _container_list['right'];

        // If there is any content in the matrix, append it to the layout.
        var matrix_layout = matrix.get_layout();
        //FIXME: Remove empty rows/body/table from matrix_layout.
        if (matrix_layout != '') {
          row += '<td rowspan="' + rowspan + '" colspan="' + colspan + '"';
          row += ' class="' + class + '">'
          row += matrix_layout
          row += '</td>';
        }
      }
      if (row != '')
        layout += '<tr>' + row + '</tr>\n';
    }
    return layout + '</tbody></table>';
  }


  // Changes the layout according to the given layout language.
  this.set_layout = function(layout) {
    this.reset();
    //FIXME
  }


  this.init();
}
