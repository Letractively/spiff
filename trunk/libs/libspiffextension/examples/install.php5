<?
include_once '../../../config.inc.php';
include_once '../SpiffExtensionDB.class.php5';
require_once '../../adodb/adodb-xmlschema03.inc.php';

$adodb = &ADONewConnection($cfg['db_dbn']);
$acldb = new SpiffAclDB($adodb);
$extdb = new SpiffExtensionDB($acldb);
//$extdb->debug();
$extdb->install();
?>
