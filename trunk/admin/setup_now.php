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
<? if ($_GET['do'] == 1) { ?>
    <h2>Spiff&trade; Installation Process Running...</h2>
    <small><i>Dear user, please ignore the technical hogwash below.<br/>
    You can just scroll down to the bottom of this page. Thank you.</i></small>
<?php
define('PHPGACL_DIR',      '../libs/phpgacl-v3.3.6/');
define('SMARTY_TEMP_DIR',  '../libs/smarty/templates_c/');
define('SPIFF_PLUGIN_DIR', 'plugins/');

require_once PHPGACL_DIR . 'gacl.class.php';
require_once PHPGACL_DIR . 'gacl_api.class.php';
require_once PHPGACL_DIR . 'admin/gacl_admin.inc.php';
require_once ADODB_DIR   . '/adodb-xmlschema.inc.php';
require_once dirname(__FILE__).'/services/gacl_db.class.php';


function category($title) {
  echo "<h3 style='padding-left: 0px; padding-bottom: 5px;'>$title</h3>";
}

function start($message) {
  echo "$message: ";
}

function success() {
  echo "<font color='green'><b>Success!</b></font><br/>";
}

function unnecessary() {
  echo "<font color='green'><b>Not necessary.</b></font><br/>";
}

function failed() {
  echo "<font color='red'><b>Failed! Sorry dude.</b></font><br/>\n";
}

function test($result) {
  if ($result)
    success();
  else {
    failed();
    global $success;
    $success = FALSE;
  }
}

$success = TRUE;
$gacl    = new GaclDB($gacl);

/*******************************************************************
 * Tests.
 *******************************************************************/
// Test database connection.
category('Testing database');
start('Trying to connect to the database server');
test(is_resource($gacl->db->_connectionID));

start('Checking whether the database server type "' . $gacl->_db_type.
      '" is supported');
test($gacl->_db_type === 'mysqlt' || $gacl->_db_type === 'mysqli');

start('Making sure that database "'.$gacl->_db_name.'" exists');
$databases = $gacl->db->GetCol("show databases");
test(in_array($gacl->_db_name, $databases));

start('Checking whether template dir ' . SMARTY_TEMP_DIR . ' exists');
test(is_dir(SMARTY_TEMP_DIR));

start('Checking file permissions of ' . SMARTY_TEMP_DIR);
test(substr(sprintf('%o', fileperms(SMARTY_TEMP_DIR)), -4) === "0775");

start('Checking whether template dir ' . SPIFF_PLUGIN_DIR . ' exists');
test(is_dir(SPIFF_PLUGIN_DIR));

start('Checking file permissions of ' . SPIFF_PLUGIN_DIR);
test(substr(sprintf('%o', fileperms(SPIFF_PLUGIN_DIR)), -4) === "0775");

// Make sure that the installation was not already finished previously.
//start('Making sure that we are not installing above another installation');


/*******************************************************************
 * Set up phpGACL.
 *******************************************************************/
// If necessary, create tables.
category('Setting Up phpGACL');
start('Creating database tables');
$tables = $gacl->db->MetaTables();
//echo "Tables: " . count($tables) . "<br/>";
//FIXME: Compare the count with the number of tables in the schema file.
if (count($tables) == 31)
  unnecessary();
else {
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
  test($result == 2);
}

start('Clearing phpgacl database tables');
test($gacl->clear_database());

// Add axo group attribute support to phpgacl.
start('Creating phpgacl AXO group attribute support');
$fields   = 'axo_group_id I(11),
             description C(255)';
$opts     = array('constraints' => ', FOREIGN KEY (axo_group_id) REFERENCES axo_groups (id) ON DELETE CASCADE');
$dict     = NewDataDictionary($gacl->db);
$sqlarray = $dict->ChangeTableSQL('axo_groups_attribs', $fields, $opts);
test($dict->ExecuteSQLArray($sqlarray));

// Add axo attribute support to phpgacl.
start('Creating phpgacl AXO attribute support');
$fields   = 'axo_id I(11),
             description C(255)';
$opts     = array('constraints' => ', FOREIGN KEY (axo_id) REFERENCES axo (id) ON DELETE CASCADE');
$dict     = NewDataDictionary($gacl->db);
$sqlarray = $dict->ChangeTableSQL('axo_attribs', $fields, $opts);
test($dict->ExecuteSQLArray($sqlarray));

// Add aro group attribute support to phpgacl.
start('Creating phpgacl ARO group attribute support');
$fields   = 'aro_group_id I(11),
             use_group_rights L DEFAULT 1,
             description C(255)';
$opts     = array('constraints' => ', FOREIGN KEY (aro_group_id) REFERENCES aro_groups (id) ON DELETE CASCADE');
$dict     = NewDataDictionary($gacl->db);
$sqlarray = $dict->ChangeTableSQL('aro_groups_attribs', $fields, $opts);
test($dict->ExecuteSQLArray($sqlarray));

// Add aro attribute support to phpgacl.
start('Creating phpgacl ARO attribute support');
//$gacl->db->debug = 1;
$fields   = 'aro_id I(11),
             use_group_rights L DEFAULT 1,
             description C(255)';
$opts     = array('constraints' => ', FOREIGN KEY (aro_id) REFERENCES aro (id) ON DELETE CASCADE');
$dict     = NewDataDictionary($gacl->db);
$sqlarray = $dict->ChangeTableSQL('aro_attribs', $fields, $opts);
test($dict->ExecuteSQLArray($sqlarray));

category('Initializing ACO List');
start('Creating access request section "Users"');
test($aro_users_section = $gacl->add_actor_section('Users'));

start('Creating access control section for users');
test($aco_users = $gacl->add_action_section('Users'));

start('Creating access control action "Administer User"');
test($aco_users_admin = $gacl->add_action('Administer', $aco_users));

start('Creating access control action "View User"');
test($aco_users_view = $gacl->add_action('View', $aco_users));

start('Creating access control action "Create User"');
test($aco_users_create = $gacl->add_action('Create', $aco_users));

start('Creating access control action "Edit User"');
test($aco_users_edit = $gacl->add_action('Edit', $aco_users));

start('Creating access control action "Delete User"');
test($aco_users_delete = $gacl->add_action('Delete', $aco_users));


start('Creating access control section for content');
test($aco_content = $gacl->add_action_section('Content'));

start('Creating access control action "View Content"');
test($aco_content_view = $gacl->add_action('View', $aco_content));

start('Creating access control action "Create Content"');
test($aco_content_create = $gacl->add_action('Create', $aco_content));

start('Creating access control action "Edit Content"');
test($aco_content_edit = $gacl->add_action('Edit', $aco_content));

start('Creating access control action "Delete Content"');
test($aco_content_delete = $gacl->add_action('Delete', $aco_content));


category('Initializing AXO Tree');
start('Creating access control section "root"');
test($axo_section_root = $gacl->add_resource_section('Root'));

//$gacl->_debug = 1; $gacl->db->debug = 1;
start('Creating access control group "root"');
test($axo_group_root = $gacl->add_resource_group(NULL, 'Root'));

start('Creating access control section "Content"');
test($axo_section_root = $gacl->add_resource_section('Content'));

start('Creating access control group "Content"');
test($axo_group_content = $gacl->add_resource_group($axo_group_root, 'Content'));



/*******************************************************************
 * Build the following group table:
 * users:   Everybody
 *            |-Administrators
 *            |   \-Administrator
 *            \-Users
 *                \-Anonymous
 *******************************************************************/
category('Creating Default Groups');
start('Creating group "Everybody"');
test($aro_everybody = $gacl->add_actor_group(NULL, 'Everybody'));

start('Creating group "Administrators"');
test($aro_admin = $gacl->add_actor_group($aro_everybody, 'Administrators'));

start('Creating group "Users"');
test($aro_users = $gacl->add_actor_group($aro_everybody, 'Users'));


/*******************************************************************
 * Build the following user table:
 * users:   Everybody
 *            |-Administrators
 *            |   \-Administrator
 *            \-Users
 *                \-Anonymous
 *******************************************************************/
$jobs['Creating Default Users'] = '-';
start('Creating user "Administrator"');
test($usr_admin = $gacl->add_actor('Administrator', $aro_users_section));

start('Assigning user "Administrator" to group "Administrators"');
test($gacl->assign_actor_to_group($usr_admin, $aro_admin));

start('Creating user "Anonymous George"');
test($usr_anon= $gacl->add_actor('Anonymous George', $aro_users_section));

start('Assigning user "Anonymous George" to group "Users"');
test($gacl->assign_actor_to_group($usr_anon, $aro_users));


/*******************************************************************
 * Build the following axo table:
 * content: Content
 *            \-Homepage
 *******************************************************************/
category('Initializing Content');
start('Creating access control object "Homepage" in "Content"');
test($homepage = $gacl->add_resource('Homepage', $axo_group_content));


/*******************************************************************
 * Define permissions of the default groups.
 *******************************************************************/
category('Assigning Permissions To Groups');
start('Defining permissions of group "Administrators"');
$aco_array = array(
  $aco_users_admin,
  $aco_users_view,
  $aco_users_create,
  $aco_users_edit,
  $aco_users_delete
);
$aro_array = array($aro_admin);
$axo_array = array($aro_everybody->get_resource_group());
test($aclid = $gacl->grant($aco_array, $aro_array, $axo_array));

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
<? } else { ?>
    Not confirmed.
<? } ?>
    </td>
  </tr>
</table>
</div>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr><td height="1" bgcolor="#888888"></td></tr>
  <tr>
    <td align="right"><table class="footer"><tr><td><img src="img/logo_small.png" alt="" /></td><td>powered by spiff</td></tr></table></td>
  </tr>
</table>

</body>
</html>

