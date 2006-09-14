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
  require_once MY_SMARTY_DIR .         '/Smarty.class.php';
  require_once ADODB_DIR .             '/adodb.inc.php';
  require_once LIBSPIFFACL_DIR .       '/SpiffAclDB.class.php5';
  require_once LIBSPIFFEXTENSION_DIR . '/SpiffExtensionStore.class.php5';

  // Load shared internal stuff.
  include_once SPIFF_DIR . '/functions/config.inc.php';
  include_once SPIFF_DIR . '/actions/printer_base.class.php';

  class Spiff {
    private $db;
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
      if (!function_exists('gettext'))
        die('Spiff::Spiff(): This webserver does not have gettext'
          . ' installed.<br/>'
          . 'Please contact your webspace provider.');
      $domain = 'spiff';
      bindtextdomain($domain, './language');
      textdomain($domain);
      bind_textdomain_codeset($domain, 'UTF-8');

      // Connect to the DB.
      $this->db = &ADONewConnection(cfg('db_dbn'))
        or die('Spiff::Spiff(): Error: Can\'t connect.'
             . ' Please check username, password and hostname.');

      $this->acldb           = &new SpiffAclDB($this->db);
      $this->extension_store = &new SpiffExtensionStore($this->db,
                                                        SPIFF_PLUGIN_DIR);

      // Init Smarty.
      $this->smarty = &new Smarty();
      $this->smarty->compile_dir  = MY_SMARTY_DIR . '/templates_c';
      $this->smarty->cache_dir    = MY_SMARTY_DIR . '/cache';
      $this->smarty->config_dir   = MY_SMARTY_DIR . '/configs';
      $this->smarty->register_function('gettext', 'smarty_gettext');
      
      if (get_magic_quotes_gpc()) {
        $_GET    = array_map('stripslashes_deep', $_GET);
        $_POST   = array_map('stripslashes_deep', $_POST);
        $_COOKIE = array_map('stripslashes_deep', $_COOKIE);
      }

      /* Plugin hook: on_construct
       *   Called from within the Spiff() constructor before any
       *   other output is produced.
       *   The return value of the callback is ignored.
       *   Args: None.
       */
      $this->extension_store->get_event_bus()->emit('on_construct');
    }
    
    
    function &get_extension_store() {
      return $this->extension_store;
    }


    function &get_smarty() {
      return $this->smarty;
    }


    function &get_acldb() {
      return $this->acldb;
    }


    function append_content(&$content) {
      $this->content .= $content . '\n';
    }


    function show() {
      $this->content = '';
      
      // Fetch the requested site.
      $section  = isset($_GET['section']) ? $_GET['section'] : 'content';
      $handle   = isset($_GET['handle'])  ? $_GET['handle']  : 'homepage';
      $section  = new SpiffAclResourceSection($section, $section);
      $resource = $this->acldb->get_resource_from_handle($handle, $section);
      
      // Check permissions.
      //FIXME

      // Load all plugins required to display the current page.
      //FIXME
    }


    function destroy() {
      unset($this->content);
      $this->db->Close();
      /* Plugin hook: on_destroy
       *   Called from within Spiff->destroy().
       *   The return value of the callback is ignored.
       *   Args: None.
       */
      $this->extension_store->get_event_bus()->emit('on_destroy');
    }
  }
?>
