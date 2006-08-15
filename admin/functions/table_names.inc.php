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
      't_acl'                => cfg("db_table_prefix") . 'acl',
      't_aco'                => cfg("db_table_prefix") . 'aco',
      't_aco_map'            => cfg("db_table_prefix") . 'aco_map',
      't_axo'                => cfg("db_table_prefix") . 'axo',
      't_axo_map'            => cfg("db_table_prefix") . 'axo_map',
      't_axo_attribs'        => cfg("db_table_prefix") . 'axo_attribs',
      't_axo_groups'         => cfg("db_table_prefix") . 'axo_groups',
      't_axo_groups_map'     => cfg("db_table_prefix") . 'axo_groups_map',
      't_axo_groups_attribs' => cfg("db_table_prefix") . 'axo_groups_attribs',
      't_axo_sections'       => cfg("db_table_prefix") . 'axo_sections',
      't_aro'                => cfg("db_table_prefix") . 'aro',
      't_aro_attribs'        => cfg("db_table_prefix") . 'aro_attribs',
      't_aro_groups'         => cfg("db_table_prefix") . 'aro_groups',
      't_aro_groups_map'     => cfg("db_table_prefix") . 'aro_groups_map',
      't_aro_groups_attribs' => cfg("db_table_prefix") . 'aro_groups_attribs',
      't_aro_sections'       => cfg("db_table_prefix") . 'aro_sections',
      't_groups_axo_map'     => cfg("db_table_prefix") . 'groups_axo_map',
      't_groups_aro_map'     => cfg("db_table_prefix") . 'groups_aro_map',
    );
    return $tables;
  }
?>
