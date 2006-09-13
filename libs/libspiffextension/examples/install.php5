<?
include_once '../../../config.inc.php';
include_once '../SpiffExtensionDB.class.php5';
require_once '../../adodb/adodb-xmlschema03.inc.php';

$adodb = &ADONewConnection($cfg['db_dbn']);
$extdb = new SpiffExtensionDB($adodb);
//$extdb->debug();
$extdb->install();
?>
