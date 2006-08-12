<?php
  /*
  Copyright (C) 2003 Samuel Abels, <spam debain org>
  
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
  */
?>
<?php
  function table_names() {
    $tables = array (
      't_axo_attribs' => cfg("db_table_prefix") . 'axo_attribs',
      't_axo_group_attribs' => cfg("db_table_prefix") . 'axo_groups_attribs',
      't_aro_attribs' => cfg("db_table_prefix") . 'aro_attribs',
      't_aro_group_attribs' => cfg("db_table_prefix") . 'aro_groups_attribs',
    );
    return $tables;
  }
?>
