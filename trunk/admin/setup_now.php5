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
require_once '../Spiff.class.php5';
require_once ADODB_DIR . '/adodb-xmlschema03.inc.php';

define('SMARTY_TEMP_DIR', MY_SMARTY_DIR . '/templates_c/');

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
$db      = &ADONewConnection($cfg['db_dbn']);
$acldb   = new SpiffAclDB($db);

/*******************************************************************
 * Tests.
 *******************************************************************/
// Test database connection.
category('Testing database');
start('Trying to connect to the database server');
test(is_resource($db->_connectionID));

start('Checking whether the database server type "' . $cfg['db_type'] .
      '" is supported');
test($cfg['db_type'] === 'mysqlt' || $cfg['db_type'] === 'mysqli');

start('Making sure that database "'.$cfg['db_name'].'" exists');
$databases = $db->GetCol("show databases");
test(in_array($cfg['db_name'], $databases));

start('Checking whether template dir ' . SMARTY_TEMP_DIR . ' exists');
test(is_dir(SMARTY_TEMP_DIR));

start('Checking file permissions of ' . SMARTY_TEMP_DIR);
test(substr(sprintf('%o', fileperms(SMARTY_TEMP_DIR)), -4) === "0775");

start('Checking whether data dir ' . SPIFF_DATA_DIR . ' exists');
test(is_dir(SPIFF_DATA_DIR));

start('Checking file permissions of ' . SPIFF_DATA_DIR);
test(substr(sprintf('%o', fileperms(SPIFF_DATA_DIR)), -4) === "0775");

// Make sure that the installation was not already finished previously.
//start('Making sure that we are not installing above another installation');


/*******************************************************************
 * Set up directories.
 *******************************************************************/
category('Creating Spiff directories');
start('Creating extension directory ' . SPIFF_PLUGIN_DIR);
if (is_dir(SPIFF_PLUGIN_DIR))
  unnecessary();
else
  test(mkdir(SPIFF_PLUGIN_DIR));

start('Setting permissions of ' . SPIFF_PLUGIN_DIR);
test(chmod(SPIFF_PLUGIN_DIR, 0775));

start('Creating extension repository directory ' . SPIFF_REPO_DIR);
if (is_dir(SPIFF_REPO_DIR))
  unnecessary();
else
  test(mkdir(SPIFF_REPO_DIR));

start('Setting permissions of ' . SPIFF_REPO_DIR);
test(chmod(SPIFF_REPO_DIR, 0775));


/*******************************************************************
 * Set up phpGACL.
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


category('Initializing User Actions');
start('Creating action section "User Permissions"');
$ac_user_section = new SpiffAclActionSection('users', 'User Permissions');
test($ac_user_section = $acldb->add_action_section($ac_user_section));

start('Creating action "Administer User"');
$action = new SpiffAclAction('administer', 'Administer User', $ac_user_section);
test($ac_user_administer = $acldb->add_action($action));

start('Creating action "View User"');
$action = new SpiffAclAction('view', 'View User', $ac_user_section);
test($ac_user_view = $acldb->add_action($action));

start('Creating action "Create User"');
$action = new SpiffAclAction('create', 'Create User', $ac_user_section);
test($ac_user_create = $acldb->add_action($action));

start('Creating action "Edit User"');
$action = new SpiffAclAction('edit', 'Edit User', $ac_user_section);
test($ac_user_edit = $acldb->add_action($action));

start('Creating action "Delete User"');
$action = new SpiffAclAction('delete', 'Delete User', $ac_user_section);
test($ac_user_delete = $acldb->add_action($action));


category('Initializing Content Actions');
start('Creating action section "Content Permissions"');
$ac_cont_section = new SpiffAclActionSection('content',
                                        'Content Permissions');
test($ac_cont_section = $acldb->add_action_section($ac_cont_section));
start('Creating action "View Content"');
test($ac_cont_view = $acldb->add_action(new SpiffAclAction('view',
                                                      'View Content',
                                                      $ac_cont_section)));

start('Creating action "Create Content"');
test($ac_cont_create = $acldb->add_action(new SpiffAclAction('create',
                                                        'Create Content',
                                                         $ac_cont_section)));

start('Creating action "Edit Content"');
test($ac_cont_edit = $acldb->add_action(new SpiffAclAction('edit',
                                                      'Edit Content',
                                                      $ac_cont_section)));

start('Creating action "Delete Content"');
test($ac_cont_delete = $acldb->add_action(new SpiffAclAction('delete',
                                                        'Delete Content',
                                                        $ac_cont_section)));


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
$users_section = new SpiffAclResourceSection('users', 'Users');
test($users_section = $acldb->add_resource_section($users_section));

start('Creating group "Everybody"');
$actor = new SpiffAclActorGroup('everybody', 'Everybody', $users_section);
test($everybody = $acldb->add_resource(NULL, $actor));

start('Creating group "Administrators"');
$actor = new SpiffAclActorGroup('administrators', 'Administrators', $users_section);
test($admin = $acldb->add_resource($everybody->get_id(), $actor));

start('Creating user "Administrator"');
$actor = new SpiffAclActor('administrator', 'Administrator', $users_section);
test($usr_admin = $acldb->add_resource($admin->get_id(), $actor));

start('Creating group "Users"');
$actor = new SpiffAclActorGroup('users', 'Users', $users_section);
test($users = $acldb->add_resource($everybody->get_id(), $actor));

start('Creating user "Anonymous George"');
$actor = new SpiffAclActor('anonymous', 'Anonymous George', $users_section);
test($usr_anon = $acldb->add_resource($users->get_id(), $actor));


/*******************************************************************
 * Set up libspiffextension.
 *******************************************************************/
category('Setting Up libspiffextension');
$extstore = new SpiffExtensionStore($db, SPIFF_PLUGIN_DIR);
start('Creating database tables');
$tables = $db->MetaTables();
//echo "Tables: " . count($tables) . "<br/>";
//FIXME: Compare the count with the number of tables in the schema file.
if (count($tables) >= 11)
  unnecessary();
else {
  $extstore->set_table_prefix($cfg['db_table_prefix']);
  //$extstore->debug();
  test($extstore->install());
}

start('Clearing libspiffextension database tables');
test($extstore->clear_database());


/*******************************************************************
 * Install core plugins.
 *******************************************************************/
category('Installing Core Extensions');
start('Registering Spiff extension');
$spiff_ext = $extstore->add_extension(SPIFF_SPIFFPLUGIN_DIR . '/spiff');
test(is_object($spiff_ext));

start('Installing login extension');
$login_ext = $extstore->add_extension(SPIFF_SPIFFPLUGIN_DIR . '/login');
test(is_object($login_ext));


/*******************************************************************
 * Build the following content table:
 * content: Content
 *            \-Homepage
 *******************************************************************/
category('Initializing Content');
start('Creating resource section "Content"');
$cont_sect = new SpiffAclResourceSection('content', 'Content');
test($cont_sect = $acldb->add_resource_section($cont_sect));

start('Creating resource "Homepage" in "Content"');
$resource = new SpiffAclResourceGroup('homepage', 'Homepage', $cont_sect);
test($homepage = $acldb->add_resource(NULL, $resource));

start('Adding login extension to homepage');
$login_ext = $acldb->add_resource($homepage->get_id(), $login_ext);
test(is_object($login_ext));


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

