<?php
  require_once '../libs/phpgacl-v3.3.6/gacl.class.php';
  require_once '../libs/phpgacl-v3.3.6/gacl_api.class.php';

  $gacl = new gacl_api();
  $gacl->clear_database() or die('Unable to clear db.');

  // Create main sections.
  $gacl->add_object_section('Content', 'content', 10, FALSE, 'AXO')
           or die('Section "Content" failed.');
  $gacl->add_object_section('Users', 'users', 10, FALSE, 'ARO')
           or die('Section "Users" failed.');

  // Add homepage objects.
  $gacl->add_object('content', 'Homepage', 'homepage', 10, FALSE, 'AXO')
           or die('Homepage AXO creation for "view" failed.');

  // Create groups.
  $content_gid = $gacl->add_group('content', 'Content', 0, 'AXO')
           or die('Content group AXO creation failure.');
  $everybody_gid = $gacl->add_group('everybody', 'Everybody', 0, 'ARO')
           or die('"Everybody" user group ARO creation failure.');
  $admin_gid = $gacl->add_group('administrators', 'Administrators', $everybody_gid, 'ARO')
           or die('Root user group ARO creation failure.');
  $user_gid = $gacl->add_group('users', 'Users', $everybody_gid, 'ARO')
           or die('User group ARO creation failure.');

  // Add users into groups.
  $gacl->add_object('users', 'Administrator', 'administrator', 10, FALSE, 'ARO')
           or die('Root user ARO creation failure.');
  $gacl->add_group_object($admin_gid, 'users', 'administrator', 'ARO')
           or die('Root user assign failure.');
  $gacl->add_object('users', 'Anonymous George', 'anonymous', 10, FALSE, 'ARO')
           or die('Anonymous user ARO creation failure.');
  $gacl->add_group_object($user_gid, 'users', 'anonymous', 'ARO')
           or die('Anonymous user assign failure.');

  echo "All tests successfully finished, database is now initialized.\n";
?>
