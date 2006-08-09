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
define('PHPGACL_DIR', '../libs/phpgacl-v3.3.6/');
define('SUCCESS',     1);
define('FAILED',      2);
define('UNNECESSARY', 3);

require_once PHPGACL_DIR . 'gacl.class.php';
require_once PHPGACL_DIR . 'gacl_api.class.php';
require_once PHPGACL_DIR . 'admin/gacl_admin.inc.php';
require_once ADODB_DIR   . '/adodb-xmlschema.inc.php';
require_once dirname(__FILE__).'/functions/phpgacl.inc.php';

$jobs = array();

/*******************************************************************
 * Tests.
 *******************************************************************/
// Test database connection.
$jobs['Testing database'] = '-';
$jobs['check_database_connection'] = 'Trying to connect to the database server';
function check_database_connection($gacl) {
  return is_resource($gacl->db->_connectionID) ? SUCCESS : FAILED;
}

// Test DBMS type.
$jobs['check_database_type'] = 'Checking whether the database server type "'.$gacl->_db_type.'" is supported';
function check_database_type($gacl) {
  return $gacl->_db_type === 'mysqlt' || $gacl->_db_type === 'mysqli' ? SUCCESS : FAILED;
}

// Test whether the specified database exists.
$jobs['check_database_exists'] = 'Making sure that database "'.$gacl->_db_name.'" exists';
function check_database_exists($gacl) {
  $databases = $gacl->db->GetCol("show databases");
  return in_array($gacl->_db_name, $databases) ? SUCCESS : FAILED;
}

// Make sure that the installation was not already finished previously.
//$jobs['check_installation_necessary'] = 'Making sure that we are not installing above another installation';
function check_installation_necessary($gacl) {
  return SUCCESS;
}

/*******************************************************************
 * Set up phpGACL.
 *******************************************************************/
// If necessary, create tables.
$jobs['Setting Up phpGACL'] = '-';
$jobs['set_up_phpgacl_tables'] = 'Creating database tables';
function set_up_phpgacl_tables($gacl) {
  $tables = $gacl->db->MetaTables();
  //echo "Tables: " . count($tables) . "<br/>";
  if (count($tables) == 28) //FIXME: Should compare the count with the number of tables in the schema file.
    return UNNECESSARY;

  $schema = new adoSchema($gacl->db);
  $schema->SetPrefix($gacl->_db_table_prefix);

  // Build the SQL array
  $schema->ParseSchema(PHPGACL_DIR . 'schema.xml');
  
  // Execute the SQL on the database
  #ADODB's xmlschema is being lame, continue on error.
  $schema->ContinueOnError(TRUE);
  $result = $schema->ExecuteSchema();
	//print $schema->getSQL('html');
  //echo "Result: $result";
  return $result == 2 ? SUCCESS : FAILED;
}

// Erase all user database content (if any).
$jobs['clear_database'] = 'Clearing phpgacl database tables';
function clear_database($gacl) {
  return $gacl->clear_database() ? SUCCESS : FAILED;
}

// Add aro attribute support to phpgacl.
$jobs['create_aro_attribute_table'] = 'Creating phpgacl aro attribute support';
function create_aro_attribute_table($gacl) {
  //$gacl->db->debug = 1;
  $fields   = 'aro_id I(11),
               use_group_rights L DEFAULT 1,
               description C(255)';
  $opts     = array('constraints' => ', FOREIGN KEY (aro_id) REFERENCES aro (id) ON DELETE CASCADE');
  $dict     = NewDataDictionary($gacl->db);
  $sqlarray = $dict->ChangeTableSQL('aro_groups_attribs', $fields, $opts);
  return $dict->ExecuteSQLArray($sqlarray) ? SUCCESS : FAILED;
}


/*******************************************************************
 * Build the following aco actions:
 * content: view, create, edit, delete
 * users: administrate, view, create, edit, delete
 *******************************************************************/
$jobs['Initializing ACO'] = '-';
$jobs['create_aco_section_content'] = 'Creating access control section for content';
function create_aco_section_content($gacl) {
  return $gacl->add_object_section('Content', 'content', 10, FALSE, 'ACO') ? SUCCESS : FAILED;
}

$jobs['create_aco_content_view'] = 'Creating access control action "View Content"';
function create_aco_content_view($gacl) {
  return $gacl->add_object('content',
                           'View',
                           'view',
                           10,
                           FALSE,
                           'ACO') ? SUCCESS : FAILED;
}

$jobs['create_aco_section_users'] = 'Creating access control section for users';
function create_aco_section_users($gacl) {
  return $gacl->add_object_section('Users', 'users', 10, FALSE, 'ACO') ? SUCCESS : FAILED;
}

$jobs['create_aco_users_view'] = 'Creating access control action "View User"';
function create_aco_users_view($gacl) {
  return $gacl->add_object('users',
                           'View',
                           'view',
                           10,
                           FALSE,
                           'ACO') ? SUCCESS : FAILED;
}


/*******************************************************************
 * Create a root object for the AXO table.
 *******************************************************************/
$jobs['Initializing AXO tree'] = '-';
$jobs['create_axo_section_root'] = 'Creating access control section "root"';
function create_axo_section_root($gacl) {
 return $gacl->add_object_section('root', 'root', 10, FALSE, 'AXO') ? SUCCESS : FAILED;
}

$jobs['create_axo_root_root'] = 'Creating access control group "root"';
function create_axo_root_root($gacl) {
  global $root_gid;
  $root_gid->axo = $gacl->add_group('root', 'root', 0, 'AXO');
  $root_gid->aro = 0;
  return $root_gid->axo ? SUCCESS : FAILED;
}


/*******************************************************************
 * Create user sections.
 *******************************************************************/
$jobs['Initializing User And Group Sections'] = '-';
$jobs['create_axo_section_users'] = 'Creating access control section "Users"';
function create_axo_section_users($gacl) {
 return $gacl->add_object_section('Users', 'users', 10, FALSE, 'AXO') ? SUCCESS : FAILED;
}

$jobs['create_aro_section_users'] = 'Creating access request section "Users"';
function create_aro_section_users($gacl) {
 return $gacl->add_object_section('Users', 'users', 10, FALSE, 'ARO') ? SUCCESS : FAILED;
}


/*******************************************************************
 * Build the following group table:
 * users:   Everybody
 *            |-Administrators
 *            |   \-Administrator
 *            \-Users
 *                \-Anonymous
 *******************************************************************/
$jobs['Creating Default Groups'] = '-';
$jobs['create_users_everybody'] = 'Creating group "Everybody"';
function create_users_everybody($gacl) {
  global $root_gid;
  global $everybody_gid;
  $everybody_gid = phpgacl_create_group($gacl, "Everybody", $root_gid);
  return $everybody_gid ? SUCCESS : FAILED;
}

$jobs['create_users_everybody_administrators'] = 'Creating group "Administrators"';
function create_users_everybody_administrators($gacl) {
  global $everybody_gid;
  global $everybody_administrators_gid;
  $everybody_administrators_gid = phpgacl_create_group($gacl, "Administrators", $everybody_gid);
  return $everybody_administrators_gid ? SUCCESS : FAILED;
}

$jobs['create_users_everybody_users'] = 'Creating group "Users"';
function create_users_everybody_users($gacl) {
  global $everybody_gid;
  global $everybody_users_gid;
  $everybody_users_gid = phpgacl_create_group($gacl, "Users", $everybody_gid);
  return $everybody_users_gid ? SUCCESS : FAILED;
}


/*******************************************************************
 * Build the following user table:
 * users:   Everybody
 *            |-Administrators
 *            |   \-Administrator
 *            \-Users
 *                \-Anonymous
 *******************************************************************/
$jobs['Creating Default Users'] = '-';
$jobs['create_users_everybody_administrators_administrator'] = 'Creating user "Administrator"';
function create_users_everybody_administrators_administrator($gacl) {
  global $everybody_administrators_gid;
  return phpgacl_create_user($gacl, "Administrator", $everybody_administrators_gid) ? SUCCESS : FAILED;
}

$jobs['create_users_everybody_users_anonymous'] = 'Creating user "Anonymous"';
function create_users_everybody_users_anonymous($gacl) {
  global $everybody_users_gid;
  return phpgacl_create_user($gacl, "Anonymous George", $everybody_users_gid) ? SUCCESS : FAILED;
}


/*******************************************************************
 * Build the following axo table:
 * content: Content
 *            \-Homepage
 *******************************************************************/
$jobs['Initializing Content AXOs'] = '-';
$jobs['create_axo_section_content'] = 'Creating access control section "Content"';
function create_axo_section_content($gacl) {
 return $gacl->add_object_section('Content', 'content', 10, FALSE, 'AXO') ? SUCCESS : FAILED;
}

$jobs['create_axo_content_content'] = 'Creating access control group "Content"';
function create_axo_content_content($gacl) {
  global $root_gid;
  global $axo_content_gid;
  return ($axo_content_gid = $gacl->add_group('content', 'Content', $root_gid->axo, 'AXO')) ? SUCCESS : FAILED;
}

$jobs['create_axo_content_content_homepage'] = 'Creating access control object "Homepage" in "Content"';
function create_axo_content_content_homepage($gacl) {
  return $gacl->add_object('content',
                           'Homepage',
                           'homepage',
                           10,
                           FALSE,
                           'AXO') ? SUCCESS : FAILED;
}


/*******************************************************************
 * Define permissions of the default groups.
 *******************************************************************/
$jobs['Assigning Permissions To Groups'] = '-';
$jobs['assign_permission_administrators'] = 'Defining permissions of group "Administrators"';
function assign_permission_administrators($gacl) {
  global $everybody_administrators_gid;
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
                          array($everybody_administrators_gid->aro),
                          $axo_array,
                          NULL,
                          $allow,
                          $enabled,
                          $return_value,
                          NULL,
                          'user');
  //$gacl->db->debug = 0; $gacl->_debug = 0;
  return $aclid ? SUCCESS : FAILED;
}

//$gacl = new gacl_api();
$success = TRUE;

foreach ($jobs as $job => $descr) {
  if ($descr === "-") {
    echo "<h3 style='padding-left: 0px; padding-bottom: 5px;'>$job</h3>";
    continue;
  }
  echo "$descr: ";
  switch (call_user_func($job, $gacl)) {
  case SUCCESS:
    echo "<font color='green'><b>Success!</b></font><br/>";
    break;

  case UNNECESSARY:
    echo "<font color='green'><b>Not necessary.</b></font><br/>";
    break;

  default:
    echo "<font color='red'><b>Failed! Sorry dude.</b></font><br/>\n";
    $success = FALSE;
    break;
  }

  if (!$success)
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
