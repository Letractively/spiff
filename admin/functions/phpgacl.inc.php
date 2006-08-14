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
function phpgacl_get_group_permission_list($gacl, $group_id, $section, $action)
{
  //echo "Group ID: $group_id, Section: $section, Action: $action<br>";
  $acl_table            = $gacl->_db_table_prefix . 'acl';
  $aco_map_table        = $gacl->_db_table_prefix . 'aco_map';
  $aro_groups_map_table = $gacl->_db_table_prefix . 'aro_groups_map';
  $axo_groups_map_table = $gacl->_db_table_prefix . 'axo_groups_map';
  $axo_groups_table     = $gacl->_db_table_prefix . 'axo_groups';
  $query = '
    SELECT    ag.id, ag.name, a.allow
    FROM      '. $acl_table            .' a
    LEFT JOIN '. $aco_map_table        .' ac  ON ac.acl_id=a.id
    LEFT JOIN '. $aro_groups_map_table .' arg ON arg.acl_id=a.id
    LEFT JOIN '. $axo_groups_map_table .' axg ON axg.acl_id=a.id
    LEFT JOIN '. $axo_groups_table     .' ag  ON ag.id=axg.group_id
    WHERE     a.enabled=1
    AND       ac.section_value="' . $section  . '"
    AND       ac.value="'         . $action   . '"
    AND       arg.group_id="'     . $group_id . '"
    ORDER BY  a.updated_DATE DESC';
  //$gacl->_debug = 1; $gacl->db->debug = 1;
  $rs = &$gacl->db->Execute($query);
  $user_data = array();
  
  if (is_object($rs)) {
    while($row = $rs->FetchRow()) {
      if ($row[2] == 1)
        $user_data['allow'][$row[0]] = $row[1];
      else
        $user_data['deny'][$row[0]]  = $row[1];
    }
  }
  //print_r($user_data);echo "<br>";
  return $user_data;
}

function phpgacl_get_user_permission_list($gacl, $user_id, $section, $action)
{
  //echo "Group ID: $group_id, Section: $section, Action: $action<br>";
  $acl_table            = $gacl->_db_table_prefix . 'acl';
  $aco_map_table        = $gacl->_db_table_prefix . 'aco_map';
  $aro_map_table        = $gacl->_db_table_prefix . 'aro_map';
  $aro_table            = $gacl->_db_table_prefix . 'aro';
  $axo_groups_map_table = $gacl->_db_table_prefix . 'axo_groups_map';
  $axo_groups_table     = $gacl->_db_table_prefix . 'axo_groups';
  $query = '
    SELECT    ag.id, ag.name, a.allow
    FROM      '. $acl_table            .' a
    LEFT JOIN '. $aco_map_table        .' acm  ON  acm.acl_id=a.id
    LEFT JOIN '. $aro_map_table        .' arm  ON  arm.acl_id=a.id
    LEFT JOIN '. $aro_table            .' ar   ON  ar.section_value=arm.section_value
                                               AND ar.value=arm.value
    LEFT JOIN '. $axo_groups_map_table .' axgm ON  axgm.acl_id=a.id
    LEFT JOIN '. $axo_groups_table     .' ag   ON  ag.id=axgm.group_id
    WHERE     a.enabled=1
    AND       acm.section_value="' . $section  . '"
    AND       acm.value="'         . $action   . '"
    AND       ar.id="'             . $user_id  . '"
    ORDER BY  a.updated_DATE DESC';
  //$gacl->_debug = 1; $gacl->db->debug = 1;
  $rs = &$gacl->db->Execute($query);
  $user_data = array();
  
  if (is_object($rs)) {
    while($row = $rs->FetchRow()) {
      if ($row[2] == 1)
        $user_data['allow'][$row[0]] = $row[1];
      else
        $user_data['deny'][$row[0]]  = $row[1];
    }
  }
  //print_r($user_data);echo "<br>";
  return $user_data;
}
