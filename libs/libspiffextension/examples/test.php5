<?
include_once '../../../config.inc.php';
include_once '../SpiffExtensionDB.class.php5';
require_once '../../adodb/adodb-xmlschema03.inc.php';

$adodb = &ADONewConnection($cfg['db_dbn']);
$acldb = new SpiffAclDB($adodb);
$extdb = new SpiffExtensionDB($acldb);

class TestExtension1 extends SpiffExtension {
  function __construct()
  {
    parent::__construct('my_test_extension1',
                        'My First Test Extension',
                        '0.2');
  }
}

class TestExtension2 extends SpiffExtension {
  function __construct()
  {
    parent::__construct('my_test_extension2',
                        'My Second Extension',
                        '0.1');
    $this->add_dependency('my_test_extension1>=0.1');
  }
}

class TestExtension3 extends SpiffExtension {
  function __construct()
  {
    parent::__construct('my_test_extension3',
                        'Third Extension',
                        '0.1');
    $this->add_dependency('my_test_extension2>=0.1');
  }
}

$extdb->clear_database();
$extension = new TestExtension1();
$extdb->register_extension($extension);
$extension = new TestExtension2();
$extdb->register_extension($extension);
$extension = new TestExtension3();
$extdb->register_extension($extension);
?>
