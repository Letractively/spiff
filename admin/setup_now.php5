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
<? if (isset($_POST['do'])) { ?>
    <h2>Spiff&trade; Installation Process Running...</h2>
    <small><i>Dear user, please ignore the technical hogwash below.<br/>
    You can just scroll down to the bottom of this page. Thank you.</i></small>
<?php
require_once '../Spiff.class.php5';
require_once ADODB_DIR . '/adodb-xmlschema03.inc.php';

function category($title) {
  echo "<h3 style='padding-left: 0px; padding-bottom: 5px;'>$title</h3>";
}

function start($message) {
  echo "<div class='install_log_msg'>$message: ";
}

function success() {
  echo "<font color='green'><b>Success!</b></font></div>";
}

function unnecessary() {
  echo "<font color='green'><b>Not necessary.</b></font></div>";
}

function failed() {
  echo "<font color='red'><b>Failed! Sorry dude.</b></font></div>\n";
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

function strip_spiff_dir($dir) {
  return substr($dir, strlen(SPIFF_DIR) + 1);
}

function db_supports_innodb(&$db) {
  $sql = 'SHOW VARIABLES LIKE "have_innodb"';
  //$db->debug = 1;
  $rs = $db->Execute($sql);
  assert('isset($rs)');
  $row = $rs->FetchRow();
  if (!$row)
    return FALSE;
  return $row['Value'] == 'YES';
}

$success = TRUE;
$db      = &ADONewConnection($cfg['db_dbn']);
$acldb   = new SpiffAclDB($db);

/*******************************************************************
 * Dependency tests.
 *******************************************************************/
category('Checking dependencies');
start('Checking whether server is running a supported version of PHP');
test(version_compare(PHP_VERSION, '5.1', '>='));

start('Checking whether gettext is installed');
test(function_exists('gettext'));


/*******************************************************************
 * Database tests.
 *******************************************************************/
category('Testing database');
start('Trying to connect to the database server');
test(is_resource($db->_connectionID));

start('Checking whether the database server type "' . $cfg['db_type'] .
      '" is supported');
test($cfg['db_type'] === 'mysqlt' || $cfg['db_type'] === 'mysqli');

start('Checking whether the database server supports InnoDB tables');
test(db_supports_innodb($db));

start('Making sure that database "'.$cfg['db_name'].'" exists');
$databases = $db->GetCol("show databases");
test(in_array($cfg['db_name'], $databases));


/*******************************************************************
 * File system checks.
 *******************************************************************/
category('Checking for files and directories');
start('Checking whether data dir ' . strip_spiff_dir(SPIFF_DATA_DIR)
    . ' exists');
test(is_dir(SPIFF_DATA_DIR));

start('Checking file permissions of ' . strip_spiff_dir(SPIFF_DATA_DIR));
test(substr(sprintf('%o', fileperms(SPIFF_DATA_DIR)), -4) === "0775");

// Make sure that the installation was not already finished previously.
//start('Making sure that we are not installing above another installation');


/*******************************************************************
 * Set up directories.
 *******************************************************************/
category('Creating Spiff directories');
start('Deleting installed extensions from ' . strip_spiff_dir(SPIFF_PLUGIN_DIR)
    . ', if any');
test(rmdir_recursive(SPIFF_PLUGIN_DIR));

start('Creating smarty template directory ' . strip_spiff_dir(SMARTY_TEMP_DIR));
if (is_dir(SMARTY_TEMP_DIR))
  unnecessary();
else
  test(mkdir(SMARTY_TEMP_DIR));

start('Setting permissions of ' . strip_spiff_dir(SMARTY_TEMP_DIR));
test(chmod(SMARTY_TEMP_DIR, 0775));

start('Creating extension directory ' . strip_spiff_dir(SPIFF_PLUGIN_DIR));
if (is_dir(SPIFF_PLUGIN_DIR))
  unnecessary();
else
  test(mkdir(SPIFF_PLUGIN_DIR));

start('Setting permissions of ' . strip_spiff_dir(SPIFF_PLUGIN_DIR));
test(chmod(SPIFF_PLUGIN_DIR, 0775));

start('Creating extension repository directory '
    . strip_spiff_dir(SPIFF_REPO_DIR));
if (is_dir(SPIFF_REPO_DIR))
  unnecessary();
else
  test(mkdir(SPIFF_REPO_DIR));

start('Setting permissions of ' . strip_spiff_dir(SPIFF_REPO_DIR));
test(chmod(SPIFF_REPO_DIR, 0775));


/*******************************************************************
 * Set up libspiffacl.
 *******************************************************************/
// If necessary, create tables.
category('Setting Up libspiffacl');
start('Creating database tables');
$tables = $db->MetaTables();
//echo "Tables: " . count($tables) . "<br/>";
//FIXME: Compare the count with the number of tables in the schema file.
if (count($tables) >= 8)
  unnecessary();
else {
  $acldb->set_table_prefix($cfg['db_table_prefix']);
  //$acldb->debug();
  test($acldb->install());
}

start('Clearing libspiffacl database tables');
test($acldb->clear_database());


/*******************************************************************
 * Set up libspiffextension.
 *******************************************************************/
category('Setting Up libspiffextension');
$null = NULL;
$extstore = new SpiffExtensionStore($null, $acldb, SPIFF_PLUGIN_DIR);
start('Creating database tables');
$tables = $db->MetaTables();
//echo "Tables: " . count($tables) . "<br/>";
//FIXME: Compare the count with the number of tables in the schema file.
if (count($tables) >= 10)
  unnecessary();
else {
  $extstore->set_table_prefix($cfg['db_table_prefix']);
  //$extstore->debug();
  test($extstore->install());
}

start('Clearing libspiffextension database tables');
test($extstore->clear_database());


/*******************************************************************
 * Install core extensions.
 *******************************************************************/
category('Installing Core Extensions');
start('Creating resource section "Extensions"');
$ac_extension_section = new SpiffAclResourceSection('Extensions');
$ac_extension_section = $acldb->add_resource_section($ac_extension_section);
test($ac_extension_section);

start('Installing Spiff extension');
$spiff_ext = $extstore->add_extension(SPIFF_SPIFFPLUGIN_DIR . '/spiff');
test(is_object($spiff_ext));

start('Installing Login extension');
$login_ext = $extstore->add_extension(SPIFF_SPIFFPLUGIN_DIR . '/login');
test(is_object($login_ext));

start('Installing Admin Center extension');
$admin_ext = $extstore->add_extension(SPIFF_SPIFFPLUGIN_DIR . '/admin_center');
test(is_object($admin_ext));


/*******************************************************************
 * Set up ACL user actions.
 *******************************************************************/
category('Initializing User Actions');
start('Creating action section "User Permissions"');
$ac_user_section = new SpiffAclActionSection('User Permissions', 'users');
test($ac_user_section = $acldb->add_action_section($ac_user_section));

start('Creating action "Administer User"');
$action = new SpiffAclAction('Administer User', 'administer');
test($ac_user_administer = $acldb->add_action($action, $ac_user_section));

start('Creating action "View User"');
$action = new SpiffAclAction('View User', 'view');
test($ac_user_view = $acldb->add_action($action, $ac_user_section));

start('Creating action "Create User"');
$action = new SpiffAclAction('Create User', 'create');
test($ac_user_create = $acldb->add_action($action, $ac_user_section));

start('Creating action "Edit User"');
$action = new SpiffAclAction('Edit User', 'edit');
test($ac_user_edit = $acldb->add_action($action, $ac_user_section));

start('Creating action "Delete User"');
$action = new SpiffAclAction('Delete User', 'delete');
test($ac_user_delete = $acldb->add_action($action, $ac_user_section));


/*******************************************************************
 * Set up ACL content actions.
 *******************************************************************/
category('Initializing Content Actions');
start('Creating action section "Content Permissions"');
$ac_cont_section = new SpiffAclActionSection('Content Permissions',
                                             'content');
test($ac_cont_section = $acldb->add_action_section($ac_cont_section));

start('Creating action "View Content"');
$action = new SpiffAclAction('View Content', 'view');
test($ac_cont_view = $acldb->add_action($action, $ac_cont_section));

start('Creating action "Create Content"');
$action = new SpiffAclAction('Create Content', 'create');
test($ac_cont_create = $acldb->add_action($action, $ac_cont_section));

start('Creating action "Edit Content"');
$action = new SpiffAclAction('Edit Content', 'edit');
test($ac_cont_edit = $acldb->add_action($action, $ac_cont_section));

start('Creating action "Delete Content"');
$action = new SpiffAclAction('Delete Content', 'delete');
test($ac_cont_delete = $acldb->add_action($action, $ac_cont_section));


/*******************************************************************
 * Set up ACL extension actions.
 *******************************************************************/
category('Initializing Extension Actions');
start('Creating action section "Extension Permissions"');
$ac_ext_section = new SpiffAclActionSection('Extension Permissions',
                                            'extensions');
test($ac_ext_section = $acldb->add_action_section($ac_ext_section));


/*******************************************************************
 * Build the following group table:
 * users:   Everybody
 *            |-Administrators
 *            |   \-Administrator
 *            \-Users
 *                \-Anonymous
 *******************************************************************/
category('Initializing Users And Groups');
start('Creating resource section "Users"');
$users_section = new SpiffAclResourceSection('Users');
test($users_section = $acldb->add_resource_section($users_section));

start('Creating group "Everybody"');
$actor     = new SpiffAclActorGroup('Everybody');
$everybody = $acldb->add_resource(NULL, $actor, $users_section);
test($everybody);

start('Creating group "Administrators"');
$actor = new SpiffAclActorGroup('Administrators');
$admin = $acldb->add_resource($everybody->get_id(), $actor, $users_section);
test($admin);

start('Creating user "Administrator"');
$actor = new SpiffAclActor('Administrator');
$actor->set_auth_string($_POST['admin_pwd']);
assert('$actor->has_auth_string($_POST["admin_pwd"])');
$usr_admin = $acldb->add_resource($admin->get_id(), $actor, $users_section);
test($usr_admin);

start('Creating group "Users"');
$actor = new SpiffAclActorGroup('Users');
$users = $acldb->add_resource($everybody->get_id(), $actor, $users_section);
test($users);

start('Creating user "Anonymous George"');
$actor    = new SpiffAclActor('Anonymous George', 'anonymous');
$usr_anon = $acldb->add_resource($users->get_id(), $actor, $users_section);
test($usr_anon);


/*******************************************************************
 * Build the following content table:
 * content: Content
 *            |-Admin Center
 *            \-Homepage
 *******************************************************************/
category('Initializing Content');
start('Creating resource section "Content"');
$cont_sect = new SpiffAclResourceSection('Content');
test($cont_sect = $acldb->add_resource_section($cont_sect));

start('Creating Admin Center');
$resource  = new SpiffAclResource('Admin Center');
$extension = $admin_ext->get_handle() . '=' . $admin_ext->get_version();
$resource->set_attribute('extension', $extension);
$admin_center = $acldb->add_resource(NULL, $resource, $cont_sect);
test(is_object($admin_center));

start('Creating Homepage');
$resource  = new SpiffAclResource('Homepage');
$extension = $login_ext->get_handle() . '=' . $login_ext->get_version();
$resource->set_attribute('extension', $extension);
$homepage = $acldb->add_resource(NULL, $resource, $cont_sect);
test(is_object($homepage));


/*******************************************************************
 * Define permissions of the default groups.
 *******************************************************************/
category('Assigning Permissions To Groups');
start('Defining permissions of group "Administrators"');
$action_array = array(
  $ac_user_administer->get_id(),
  $ac_user_view->get_id(),
  $ac_user_create->get_id(),
  $ac_user_edit->get_id(),
  $ac_user_delete->get_id(),
  $ac_cont_view->get_id(),
  $ac_cont_create->get_id(),
  $ac_cont_edit->get_id(),
  $ac_cont_delete->get_id()
);
$resource_array = array(
  $everybody->get_id(),
  $homepage->get_id()
);
test($acldb->grant_from_id($admin->get_id(),
                           $action_array,
                           $resource_array));
?>
    </td>
  </tr>
  <tr>
    <td align='center'>
<? if ($success) { ?>
    <font size='+1' color='green'>Successfully finished initialization,
    Spiff&trade; setup is now complete! :-)</font><br/>
    <br/>
    You can now start to <a href="../index.php5?handle=admin_center">edit your web site</a>,
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

