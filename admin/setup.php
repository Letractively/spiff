<html>
<body>
<div align='center'>
<table cellpadding='20'>
  <tr>
    <td bgcolor='#f5f5f2'>
    <h2>Spiff&trade; Installation Process Running...</h2>
<?php
require_once '../libs/phpgacl-v3.3.6/gacl.class.php';
require_once '../libs/phpgacl-v3.3.6/gacl_api.class.php';

function clear_database($gacl) {
  return $gacl->clear_database();
}

function create_gacl_aro_table($gacl) {
  $fields = 'aro_id I(11),
             use_group_rights L DEFAULT 1,
             description C(255)';
  $opts   = array('constraints' => ', FOREIGN KEY (aro_id) REFERENCES aro (id) ON DELETE CASCADE');
  //$gacl->db->debug = 1;
  $dict     = NewDataDictionary($gacl->db);
  $sqlarray = $dict->ChangeTableSQL('aro_groups_attribs', $fields, $opts);
  return $dict->ExecuteSQLArray($sqlarray);
}

function create_content_section($gacl) {
 return $gacl->add_object_section('Content', 'content', 10, FALSE, 'AXO');
}

function create_content_group($gacl) {
  global $content_gid;
  return $content_gid = $gacl->add_group('content', 'Content', 0, 'AXO');
}

function create_user_aro_section($gacl) {
 return $gacl->add_object_section('Users', 'users', 10, FALSE, 'ARO');
}

function create_user_axo_section($gacl) {
 return $gacl->add_object_section('Users', 'users', 10, FALSE, 'AXO');
}

function create_everybody_group($gacl) {
  global $everybody_gid;
  return $everybody_gid = $gacl->add_group('everybody', 'Everybody', 0, 'ARO');
}

function create_admin_group($gacl) {
  global $everybody_gid;
  global $admin_gid;
  return $admin_gid = $gacl->add_group('administrators',
                                       'Administrators',
                                       $everybody_gid,
                                       'ARO');
}

function create_user_group($gacl) {
  global $everybody_gid;
  global $user_gid;
  return $user_gid = $gacl->add_group('users',
                                      'Users',
                                       $everybody_gid,
                                       'ARO');
}

function create_root_user($gacl) {
  return $gacl->add_object('users',
                           'Administrator',
                           'administrator',
                           10,
                           FALSE,
                           'ARO');
}

function create_root_axo($gacl) {
  return $gacl->add_object('users',
                           'Administrator',
                           'administrator',
                           10,
                           FALSE,
                           'AXO');
}

function assign_root_user($gacl) {
  global $admin_gid;
  return $gacl->add_group_object($admin_gid,
                                 'users',
                                 'administrator',
                                 'ARO');
}

function create_anonymous_user($gacl) {
  return $gacl->add_object('users',
                           'Anonymous George',
                           'anonymous',
                           10,
                           FALSE,
                           'ARO');
}

function assign_anonymous_user($gacl) {
  global $user_gid;
  return $gacl->add_group_object($user_gid,
                                 'users',
                                 'anonymous',
                                 'ARO');
}

function create_default_homepage_axo($gacl) {
  return $gacl->add_object('content',
                           'Homepage',
                           'homepage',
                           10,
                           FALSE,
                           'AXO');
}

$jobs = array(
  'clear_database'
    => 'Clearing phpgacl database tables',
  'create_content_section'
    => 'Creating access control object section for content',
  'create_content_group'
    => 'Creating access control group for content',
  'create_user_aro_section'
    => 'Creating access request object section for users',
  'create_user_axo_section'
    => 'Creating access control object section for users',
  'create_everybody_group'
    => 'Creating access request group "Everybody"',
  'create_admin_group'
    => 'Creating access request group "Administrators"',
  'create_user_group'
    => 'Creating access request group "Users"',
  'create_gacl_aro_table'
    => 'Creating a table for extending phpgacl with aro attribute support',
  'create_root_user'
    => 'Creating administrator account',
  'create_root_axo'
    => 'Creating administrator account control object',
  'assign_root_user'
    => 'Assigning administrator account to administrator group',
  'create_anonymous_user'
    => 'Creating anonymous account',
  'assign_anonymous_user'
    => 'Assigning anonymous account to user group',
  'create_default_homepage_axo'
    => 'Creating default homepage access control object'
);

$gacl = new gacl_api();

foreach ($jobs as $job => $descr) {
  echo "$descr: ";
  if (call_user_func($job, $gacl))
    echo "<font color='green'>Success!</font><br/>";
  else
    echo "<font color='red'>Failed! Sorry dude.</font><br/>";
}
?>
    </td>
  </tr>
  <tr>
    <td align='center'>
    <font size='+1' color='green'>Successfully finished initialization,
    Spiff&trade; setup is now complete! :-)</font><br/>
    <br/>
    You can now start to <a href=".">edit your web site</a>,
    or <a href="..">view your home page</a>.
    </td>
  </tr>
</table>
</div>
</body>
</html>
