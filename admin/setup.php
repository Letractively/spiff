<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=iso-8859-1" />
  <title>Spiff&trade; Installer</title>
  <link rel=stylesheet type="text/css" href="style.css" />
</head>

<body>
<table class="header" width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td class="banner_left" width="50"><a class="title" href="."><img class="logo" src="img/logo_medium.png" alt="" border="0" /></a></td>
    <td class="banner_left"><a class="title" href="."><span class="title">Spiff</span><span class="trade">&trade;</span><span class="title"> Web Installer</span></a></td>
    <td class="banner_right" align="right" width="482"></td>
  </tr>
</table>

<div align='center'>
<table cellpadding='20'>
  <tr>
    <td bgcolor='#f5f5f2'>
    <h2>Spiff&trade; Installation Process Running...</h2>
    <small><i>Dear user, please ignore the technical hogwash below.<br/>
    You can just scroll down to the bottom of this page. Thank you.</i></small>
<?php
require_once '../libs/phpgacl-v3.3.6/gacl.class.php';
require_once '../libs/phpgacl-v3.3.6/gacl_api.class.php';

$jobs = array();

$jobs['Initializing database'] = '-';
$jobs['clear_database'] = 'Clearing phpgacl database tables';
function clear_database($gacl) {
  return $gacl->clear_database();
}

// Add aro attribute support to phpgacl.
$jobs['create_aro_attribute_table'] = 'Creating phpgacl aro attribute support';
function create_aro_attribute_table($gacl) {
  $fields = 'aro_id I(11),
             use_group_rights L DEFAULT 1,
             description C(255)';
  $opts   = array('constraints' => ', FOREIGN KEY (aro_id) REFERENCES aro (id) ON DELETE CASCADE');
  //$gacl->db->debug = 1;
  $dict     = NewDataDictionary($gacl->db);
  $sqlarray = $dict->ChangeTableSQL('aro_groups_attribs', $fields, $opts);
  return $dict->ExecuteSQLArray($sqlarray);
}


/*******************************************************************
 * Build the following aco actions:
 * content: view, create, edit, delete
 * users: administrate, view, create, edit, delete
 *******************************************************************/
$jobs['Initializing ACO'] = '-';
$jobs['create_aco_section_content'] = 'Creating access control section for content';
function create_aco_section_content($gacl) {
  return $gacl->add_object_section('Content', 'content', 10, FALSE, 'ACO');
}

$jobs['create_aco_content_view'] = 'Creating access control action "View Content"';
function create_aco_content_view($gacl) {
  return $gacl->add_object('content',
                           'View',
                           'view',
                           10,
                           FALSE,
                           'ACO');
}

$jobs['create_aco_section_users'] = 'Creating access control section for users';
function create_aco_section_users($gacl) {
  return $gacl->add_object_section('Users', 'users', 10, FALSE, 'ACO');
}

$jobs['create_aco_users_view'] = 'Creating access control action "View User"';
function create_aco_users_view($gacl) {
  return $gacl->add_object('users',
                           'View',
                           'view',
                           10,
                           FALSE,
                           'ACO');
}


/*******************************************************************
 * Create a root object for the AXO table.
 *******************************************************************/
$jobs['Initializing AXO tree'] = '-';
$jobs['create_axo_section_root'] = 'Creating access control section "root"';
function create_axo_section_root($gacl) {
 return $gacl->add_object_section('root', 'root', 10, FALSE, 'AXO');
}

$jobs['create_axo_root_root'] = 'Creating access control group "root"';
function create_axo_root_root($gacl) {
  global $axo_root_gid;
  return $axo_root_gid = $gacl->add_group('root', 'root', 0, 'AXO');
}


/*******************************************************************
 * Build the following axo table:
 * users:   Everybody
 *            |-Administrators
 *            |   \-Administrator
 *            \-Users
 *                \-Anonymous
 *******************************************************************/
$jobs['Initializing User AXOs'] = '-';
$jobs['create_axo_section_users'] = 'Creating access control section "Users"';
function create_axo_section_users($gacl) {
 return $gacl->add_object_section('Users', 'users', 10, FALSE, 'AXO');
}

$jobs['create_axo_users_everybody'] = 'Creating access control group "Everybody"';
function create_axo_users_everybody($gacl) {
  global $axo_root_gid;
  global $axo_everybody_gid;
  return $axo_everybody_gid = $gacl->add_group('everybody', 'Everybody', $axo_root_gid, 'AXO');
}

$jobs['create_axo_users_everybody_administrators'] = 'Creating access control group "Administrators"';
function create_axo_users_everybody_administrators($gacl) {
  global $axo_everybody_gid;
  global $axo_everybody_administrators_gid;
  return $axo_everybody_administrators_gid = $gacl->add_group('administrators',
                                                              'Administrators',
                                                              $axo_everybody_gid,
                                                              'AXO');
}

$jobs['create_axo_users_everybody_administrators_administrator'] = 'Creating access control object "Administrator"';
function create_axo_users_everybody_administrators_administrator($gacl) {
  return $gacl->add_object('users',
                           'Administrator',
                           'administrator',
                           10,
                           FALSE,
                           'AXO');
}

$jobs['assign_axo_users_everybody_administrators_administrator'] = 'Assigning user "Administrator" to AXO group "Administrators"';
function assign_axo_users_everybody_administrators_administrator($gacl) {
  global $axo_everybody_administrators_gid;
  return $gacl->add_group_object($axo_everybody_administrators_gid,
                                 'users',
                                 'administrator',
                                 'AXO');
}

$jobs['create_axo_users_everybody_users'] = 'Creating access control group "Users"';
function create_axo_users_everybody_users($gacl) {
  global $axo_everybody_gid;
  global $axo_everybody_users_gid;
  return $axo_everybody_users_gid = $gacl->add_group('users',
                                                     'users',
                                                     $axo_everybody_gid,
                                                     'AXO');
}

$jobs['create_axo_users_everybody_users_anonymous'] = 'Creating access control object "Anonymous"';
function create_axo_users_everybody_users_anonymous($gacl) {
  return $gacl->add_object('users',
                           'Anonymous',
                           'anonymous',
                           10,
                           FALSE,
                           'AXO');
}

$jobs['assign_axo_users_everybody_users_anonymous'] = 'Assigning user "Anonymous" to AXO group "Users"';
function assign_axo_users_everybody_users_anonymous($gacl) {
  global $axo_everybody_users_gid;
  return $gacl->add_group_object($axo_everybody_users_gid,
                                 'users',
                                 'anonymous',
                                 'AXO');
}


/*******************************************************************
 * Build the following axo table:
 * content: Content
 *            \-Homepage
 *******************************************************************/
$jobs['Initializing Content AXOs'] = '-';
$jobs['create_axo_section_content'] = 'Creating access control section "Content"';
function create_axo_section_content($gacl) {
 return $gacl->add_object_section('Content', 'content', 10, FALSE, 'AXO');
}

$jobs['create_axo_content_content'] = 'Creating access control group "Content"';
function create_axo_content_content($gacl) {
  global $axo_root_gid;
  global $axo_content_gid;
  return $axo_content_gid = $gacl->add_group('content', 'Content', $axo_root_gid, 'AXO');
}

$jobs['create_axo_content_content_homepage'] = 'Creating access control object "Homepage" in "Content"';
function create_axo_content_content_homepage($gacl) {
  return $gacl->add_object('content',
                           'Homepage',
                           'homepage',
                           10,
                           FALSE,
                           'AXO');
}


/*******************************************************************
 * Build the following aro table:
 * Everybody
 *  |-Administrators
 *  |  \-Administrator
 *  \-Users
 *     \-Anonymous
 *******************************************************************/
$jobs['Initializing Users And Groups'] = '-';
$jobs['create_aro_section_users'] = 'Creating access request section "Users"';
function create_aro_section_users($gacl) {
 return $gacl->add_object_section('Users', 'users', 10, FALSE, 'ARO');
}

$jobs['create_aro_users_everybody'] = 'Creating access group "Everybody"';
function create_aro_users_everybody($gacl) {
  global $everybody_gid;
  return $everybody_gid = $gacl->add_group('everybody', 'Everybody', 0, 'ARO');
}

$jobs['create_aro_users_administrators'] = 'Creating access group "Administrators"';
function create_aro_users_administrators($gacl) {
  global $everybody_gid;
  global $admin_gid;
  return $admin_gid = $gacl->add_group('administrators',
                                       'Administrators',
                                       $everybody_gid,
                                       'ARO');
}

$jobs['create_aro_users_administrators_administrator'] = 'Creating user "Administrator"';
function create_aro_users_administrators_administrator($gacl) {
  return $gacl->add_object('users',
                           'Administrator',
                           'administrator',
                           10,
                           FALSE,
                           'ARO');
}

$jobs['create_aro_users_users'] = 'Creating access group "Users"';
function create_aro_users_users($gacl) {
  global $everybody_gid;
  global $user_gid;
  return $user_gid = $gacl->add_group('users',
                                      'Users',
                                       $everybody_gid,
                                       'ARO');
}

$jobs['create_aro_users_users_anonymous'] = 'Creating user "Anonymous"';
function create_aro_users_users_anonymous($gacl) {
  return $gacl->add_object('users',
                           'Anonymous George',
                           'anonymous',
                           10,
                           FALSE,
                           'ARO');
}


/*******************************************************************
 * Assign default users to the correct groups.
 *******************************************************************/
$jobs['Assigning Users To Groups'] = '-';
$jobs['assign_user_administrator'] = 'Assigning user "Administrator" to group "Administrators"';
function assign_user_administrator($gacl) {
  global $admin_gid;
  return $gacl->add_group_object($admin_gid,
                                 'users',
                                 'administrator',
                                 'ARO');
}

$jobs['assign_user_anonymous'] = 'Assigning user "Anonymous" to group "Users"';
function assign_user_anonymous($gacl) {
  global $user_gid;
  return $gacl->add_group_object($user_gid,
                                 'users',
                                 'anonymous',
                                 'ARO');
}


/*******************************************************************
 * Define permissions of the default groups.
 *******************************************************************/
$jobs['Assigning Permissions To Groups'] = '-';
$jobs['assign_permission_administrators'] = 'Defining permissions of group "Administrators"';
function assign_permission_administrators($gacl) {
  global $admin_gid;
  $aco_array = array(
    'users' => array('view'),
  );
  $axo_array = array(
    'users'   => array('administrator'),
  );
  $allow        = TRUE;
  $enabled      = TRUE;
  $return_value = NULL;
  //$gacl->_debug = 1; $gacl->db->debug = 1;
  $aclid = $gacl->add_acl($aco_array,
                          NULL,
                          array($admin_gid),
                          $axo_array,
                          NULL,
                          $allow,
                          $enabled,
                          $return_value,
                          NULL,
                          'user');
  //$gacl->db->debug = 0; $gacl->_debug = 0;
  return $aclid;
}

$gacl = new gacl_api();
$success = TRUE;

foreach ($jobs as $job => $descr) {
  if ($descr === "-") {
    echo "<h3 style='padding-left: 0px; padding-bottom: 5px;'>$job</h3>";
    continue;
  }
  echo "$descr: ";
  if (call_user_func($job, $gacl)) {
    echo "<font color='green'>Success!</font><br/>";
    continue;
  }

  echo "<font color='red'>Failed! Sorry dude.</font><br/>\n";
  $success = FALSE;
  break;
}
?>
    </td>
  </tr>
  <tr>
    <td align='center'>
<? if ($success) { ?>
    <font size='+1' color='green'>Successfully finished initialization,
    Spiff&trade; setup is now complete! :-)</font><br/>
    <br/>
    You can now start to <a href=".">edit your web site</a>,
    or <a href="..">view your home page</a>.
<? } else { ?>
    <font size='+1' color='red'>Initialization failed :-(.
    Please try to correct the above errors and try again.</font><br/>
<? } ?>
    </td>
  </tr>
</table>
</div>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr><td height="1" bgcolor="#888888"></td></tr>
  <tr>
    <td align="right"><table class="footer"><tr><td><img src="img/logo_small.png" alt="" /></td><td>powered by spiff ng</td></tr></table></td>
  </tr>
</table>

</body>
</html>
