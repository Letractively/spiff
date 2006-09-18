<?php
  /*
  Copyright (C) 2006 Samuel Abels, <spam debain org>
  
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
  */
?>
<?php
error_reporting(E_ALL);
define('SPIFF_DIR',             dirname(__FILE__));
define('SPIFF_DATA_DIR',        SPIFF_DIR .      '/data');
define('SPIFF_PLUGIN_DIR',      SPIFF_DATA_DIR . '/installed_plugins');
define('SPIFF_REPO_DIR',        SPIFF_DATA_DIR . '/repo');
define('SPIFF_SPIFFPLUGIN_DIR', SPIFF_DIR .      '/plugins');
define('MY_SMARTY_DIR',         SPIFF_DIR .      '/libs/smarty');
define('SMARTY_TEMP_DIR',       SPIFF_DATA_DIR . '/smarty_templates_c/');
define('ADODB_DIR',             SPIFF_DIR .      '/libs/adodb');
define('LIBSPIFFACL_DIR',       SPIFF_DIR .      '/libs/libspiffacl');
define('LIBSPIFFEXTENSION_DIR', SPIFF_DIR .      '/libs/libspiffextension');
define('LIBUSEFUL_DIR',         SPIFF_DIR .      '/libs/libuseful');

// Load libs.
include_once LIBUSEFUL_DIR .         '/assert.inc.php';
include_once LIBUSEFUL_DIR .         '/SqlQuery.class.php5';
include_once LIBUSEFUL_DIR .         '/EventBus.class.php5';
include_once LIBUSEFUL_DIR .         '/string.inc.php';
include_once LIBUSEFUL_DIR .         '/httpquery.inc.php';
include_once LIBUSEFUL_DIR .         '/files.inc.php';
include_once LIBUSEFUL_DIR .         '/cookie.inc.php';
include_once LIBUSEFUL_DIR .         '/URL.class.php';
require_once MY_SMARTY_DIR .         '/Smarty.class.php';
require_once ADODB_DIR .             '/adodb.inc.php';
require_once LIBSPIFFACL_DIR .       '/SpiffAclDB.class.php5';
require_once LIBSPIFFEXTENSION_DIR . '/SpiffExtensionStore.class.php5';

// Load shared internal stuff.
include_once SPIFF_DIR . '/functions/config.inc.php';
include_once SPIFF_DIR . '/functions/smarty.inc.php';
include_once SPIFF_DIR . '/actions/printer_base.class.php';

class Spiff {
  private $db;
  private $debug;
  private $event_bus;
  private $extension_store;
  private $smarty;
  private $acldb;
  
  function __construct() {
    // Select a language.
    $l = cfg('lang');
    if ($l == 'auto')
      $l = ($_REQUEST[language] ? $_REQUEST[language] : cfg('lang_default'));
    //putenv("LANG=$l");
    setlocale(LC_MESSAGES, $l);
    
    // Setup gettext.
    assert('function_exists("gettext")');
    $domain = 'spiff';
    bindtextdomain($domain, './language');
    textdomain($domain);
    bind_textdomain_codeset($domain, 'UTF-8');

    // Connect to the DB.
    $this->db = &ADONewConnection(cfg('db_dbn'))
      or die('Spiff::Spiff(): Error: Can\'t connect.'
           . ' Please check username, password and hostname.');

    $this->debug           = FALSE;
    $this->acldb           = &new SpiffAclDB($this->db);
    $this->event_bus       = &new EventBus();
    $this->extension_store = &new SpiffExtensionStore($this,
                                                      $this->acldb,
                                                      SPIFF_PLUGIN_DIR);

    // Init Smarty.
    $this->smarty = &new Smarty();
    $this->smarty->compile_dir  = SMARTY_TEMP_DIR;
    $this->smarty->cache_dir    = MY_SMARTY_DIR . '/cache';
    $this->smarty->config_dir   = MY_SMARTY_DIR . '/configs';
    $this->smarty->register_function('gettext',        'smarty_gettext');
    
    if (get_magic_quotes_gpc()) {
      $_GET    = array_map('stripslashes_deep', $_GET);
      $_POST   = array_map('stripslashes_deep', $_POST);
      $_COOKIE = array_map('stripslashes_deep', $_COOKIE);
    }

    /* Plugin hook: on_construct
     *   Type: EventBus signal.
     *   Called from within the Spiff() constructor before any
     *   other output is produced.
     *   The return value of the callback is ignored.
     *   Args: None.
     */
    $this->event_bus->emit('on_construct');
  }
  
  
  function debug($debug = TRUE) {
    $this->debug = $debug;
  }


  function &get_extension_store() {
    return $this->extension_store;
  }


  public function &get_event_bus()
  {
    return $this->event_bus;
  }


  function &get_smarty() {
    return $this->smarty;
  }


  function &get_acldb() {
    return $this->acldb;
  }


  function get_current_user_id() {
    if (session_id() == '' || !isset($_SESSION['uid']))
      return -1;
    return $_SESSION['uid'];
  }


  function &get_current_user() {
    if ($this->get_current_user_id() <= 0) {
      $null = NULL;
      return $null;
    }
    return $this->acldb->get_resource_from_id($this->get_current_user_id());
  }


  function show() {
    if (!session_id())
      session_start();

    // Decide which site was requested.
    $section  = isset($_GET['section']) ? $_GET['section'] : 'content';
    $handle   = isset($_GET['handle'])  ? $_GET['handle']  : 'homepage';
    $resource = $this->acldb->get_resource_from_handle($handle, $section);
    if (!$resource)
      die('No such resource.');

    // Find out which user it is that requests the site.
    $current_user = $this->get_current_user();
    if ($current_user == NULL)
      $current_user = $this->acldb->get_resource_from_handle('anonymous',
                                                             'users');
    
    // Check permissions.
    //$this->debug();
    if ($this->debug)
      echo 'User "'            . $current_user->get_name()   . '"'
         . ' (Handle: "'       . $current_user->get_handle() . '")'
         . ' trying to view "' . $resource->get_name()       . '"'
         . ' (Handle: "'       . $resource->get_handle()     . '")'
         . '<br>';
    $read = $this->acldb->get_action_from_handle('view', 'content');
    assert('is_object($read)');
    if (!$this->acldb->has_permission_from_id($current_user->get_id(),
                                              $read->get_id(),
                                              $resource->get_id())) {
      if ($this->debug)
        echo 'Permission denied.<br/>';
      $resource = $this->acldb->get_resource_from_handle('system/login',
                                                         'content');
      assert('is_object($resource)');
    }
    if ($this->debug)
      echo 'Loading: "'  . $resource->get_name()   . '"'
         . ' (Handle: "' . $resource->get_handle() . '")<br/>';

    // Setup base url that plugins should use to access the current site.
    $url = new URL($_SERVER['PHP_SELF']);
    if (isset($_GET['section']))
      $url->set_var('section', $_GET['section']);
    if (isset($_GET['handle']))
      $url->set_var('handle',  $_GET['handle']);
    
    // Load all plugins required to use the extension associated with the
    // current page.
    $extension      = $resource->get_attribute('extension');
    $extension      = $this->extension_store->prepare_extension($extension);
    $rel_plugin_dir = substr(SPIFF_PLUGIN_DIR, strlen(SPIFF_DIR) + 1);
    $basename       = basename($extension->get_filename());
    $this->smarty->clear_all_assign();
    $this->smarty->template_dir = $extension->get_filename();
    $this->smarty->assign('url',        $url->get_string());
    $this->smarty->assign('plugin_dir', $rel_plugin_dir  . '/' . $basename);

    /* Plugin hook: on_page_open
     *   Type: EventBus signal.
     *   Called from within Spiff->show().
     *   The return value of the callback is ignored.
     *   Args: None.
     */
    $this->event_bus->emit('on_page_open');
    
    /* Plugin hook: on_render_request
     *   Type: Method call.
     *   Called from within Spiff->show().
     *   The callback must return the content to be printed.
     *   Args: None.
     */
    print $extension->on_render_request();
  }


  function destroy() {
    unset($this->content);
    $this->db->Close();
    /* Plugin hook: on_destroy
     *   Type: EventBus signal.
     *   Called from within Spiff->destroy().
     *   The return value of the callback is ignored.
     *   Args: None.
     */
    $this->event_bus->emit('on_destroy');
  }
}
?>