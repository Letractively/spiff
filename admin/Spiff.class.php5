<?php
  /*
  Copyright (C) 2006 Samuel Abels, <spam debain org>
                     Robert Weidlich, <tefinch xenim de>
  
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
  define('SMARTY_DIR',            '../libs/smarty');
  define('ADODB_DIR',             '../libs/adodb');
  define('LIBSPIFFACL_DIR',       '../libs/libspiffacl');
  define('LIBSPIFFEXTENSION_DIR', '../libs/libspiffextension');
  define('LIBUSEFUL_DIR',         '../libs/libuseful');
  define('SPIFF_PLUGIN_DIR',      '../plugins');
  
  // Load libs.
  require_once SMARTY_DIR .            '/Smarty.class.php';
  require_once ADODB_DIR .             '/adodb.inc.php';
  require_once LIBSPIFFACL_DIR .       '/SpiffAclDB.class.php5';
  //require_once LIBSPIFFEXTENSION_DIR . '/SpiffExtensionDB.class.php5';
  include_once LIBUSEFUL_DIR .         '/SqlQuery.class.php5';
  include_once LIBUSEFUL_DIR .         '/EventBus.class.php5';
  include_once LIBUSEFUL_DIR .         '/assert.inc.php';
  include_once LIBUSEFUL_DIR .         '/string.inc.php';
  include_once LIBUSEFUL_DIR .         '/httpquery.inc.php';
  include_once LIBUSEFUL_DIR .         '/files.inc.php';

  // Load internal stuff.
  include_once 'functions/config.inc.php';
  include_once 'functions/language.inc.php';
  
  include_once 'config.inc.php';
  include_once 'error.inc.php';
  
  include_once 'objects/url.class.php';
  include_once 'objects/user.class.php';
  include_once 'objects/group.class.php';
  
  include_once 'actions/printer_base.class.php';
  include_once 'actions/breadcrumbs_printer.class.php';
  include_once 'actions/content_printer.class.php';
  include_once 'actions/login_printer.class.php';
  include_once 'actions/header_printer.class.php';
  include_once 'actions/footer_printer.class.php';
  include_once 'actions/registration_printer.class.php';
  include_once 'actions/user_manager_printer.class.php';
  include_once 'actions/permission_tree_printer.class.php';
  
  include_once 'services/plugin_registry.class.php';
  
  
  class Spiff {
    var $db;
    var $registry;
    var $eventbus;
    var $smarty;
    var $acldb;
    
    function Spiff() {
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
      
      $this->eventbus = &new EventBus;

      // Connect to the DB.
      $this->db = &ADONewConnection(cfg('db_dbn'))
        or die('Spiff::Spiff(): Error: Can\'t connect.'
             . ' Please check username, password and hostname.');

      $this->registry = &new PluginRegistry();
      $this->registry->read_plugins(SPIFF_PLUGIN_DIR);
      $this->registry->activate_plugins($this); //FIXME: Make activation configurable.

      /* Plugin hook: on_construct
       *   Called from within the Spiff() constructor before any
       *   other output is produced.
       *   The return value of the callback is ignored.
       *   Args: None.
       */
      $this->eventbus->emit('on_construct');
      
      // Init Smarty.
      $this->smarty = &new Smarty();
      $this->smarty->template_dir = "templates/";
      $this->smarty->compile_dir  = "../libs/smarty/templates_c";
      $this->smarty->cache_dir    = "../libs/smarty/cache";
      $this->smarty->config_dir   = "../libs/smarty/configs";
      $this->smarty->register_function('lang', 'smarty_lang');
      
      $this->acldb = new SpiffAclDB($this->db);
      
      $this->_handle_cookies();
    }
    
    
    function _handle_cookies() {
      if (get_magic_quotes_gpc()) {
        $_GET    = array_map('stripslashes_deep', $_GET);
        $_POST   = array_map('stripslashes_deep', $_POST);
        $_COOKIE = array_map('stripslashes_deep', $_COOKIE);
      }
    }
    
    
    // Changes a cookie only if necessary.
    function _set_cookie($_name, $_value) {
      if ($_COOKIE[$_name] != $_value) {
        setcookie($_name, $_value);
        $_COOKIE[$_name] = $_value;
      }
    }
    
    
    // Prints the navigation path of the page.
    function _print_breadcrumbs($_message) {
      $forumurl = &new URL('?');
      $forumurl->set_var('list',     1);
      $forumurl->set_var('forum_id', $_GET[forum_id]);
      
      $breadcrumbs = &new BreadCrumbsPrinter($this);
      $breadcrumbs->add_item(lang("forum"), $forumurl);
      
      if ($_GET[read] || $_GET[llist]) {
        if (!$_message)
          $breadcrumbs->add_item(lang("noentrytitle"));
        elseif (!$_message->is_active())
          $breadcrumbs->add_item(lang("blockedtitle"));
        else
          $breadcrumbs->add_item($_message->get_subject());
      }
      
      $breadcrumbs->show();
    } 
    
    
    function _print_content() {
      $content = &new ContentPrinter($this);
      $content->show('admin.tpl');
    } 
    
    
    function _print_user_manager() {
      $man = &new UserManagerPrinter($this);
      $man->show();
    } 
    
    
    function _print_permission_tree() {
      $printer = &new PermissionTreePrinter($this);
      $printer->show();
    } 


    function _register() {
      $registration = &new RegistrationPrinter($this);
      $registration->show();
      //$group     = &new Group;
      //$accountdb = &new AccountDB($this->db);
      //$accountdb->foreach_user(-1, 0, -1, array(&$this, "_user_print"), '');
    }


    function &get_registry() {
      return $this->registry;
    }


    function &get_eventbus() {
      return $this->eventbus;
    }


    function &get_smarty() {
      return $this->smarty;
    }


    function &get_acldb() {
      return $this->acldb;
    }


    function append_content(&$_content) {
      $this->content .= $_content . "\n";
    }


    function print_header() {
      if (!headers_sent())
        header("Content-Type: text/html; charset=utf-8");
      $this->content = "";
      $header = &new HeaderPrinter($this);
      $header->show();
      
      /* Plugin hook: on_header_print_before
       *   Called before the HTML header is sent.
       *   Args: $html: A reference to the HTML header.
       */
      $this->eventbus->emit("on_header_print_before", $this->content);
      print($this->content);
      
      /* Plugin hook: on_header_print_after
       *   Called after the HTML header was sent.
       *   Args: none
       */
      $this->eventbus->emit("on_header_print_after");
    }
    
    
    function print_footer() {
      if (!headers_sent())
        header("Content-Type: text/html; charset=utf-8");
      $this->content = "";
      $footer = &new FooterPrinter($this);
      $footer->show();
      
      /* Plugin hook: on_footer_print_before
       *   Called before the footer of the page is sent.
       *   Args: $html: A reference to the footer html.
       */
      $this->eventbus->emit("on_footer_print_before", $this->content);
      print($this->content);
      
      /* Plugin hook: on_footer_print_after
       *   Called after the footer of the page is sent.
       *   Args: none
       */
      $this->eventbus->emit("on_footer_print_after");
    }
    
    
    function show() {
      $this->content = "";
      
      if (isset($_GET['manage_users']))
        $this->_print_user_manager();
      elseif (isset($_GET['permission_tree']))
        $this->_print_permission_tree();
      else
        $this->_print_content();

      /* Plugin hook: on_content_print_before
       *   Called before the HTML content is sent.
       *   Args: $html: A reference to the content.
       */
      $this->eventbus->emit("on_content_print_before", $this->content);
      print($this->content);

      /* Plugin hook: on_content_print_after
       *   Called after the HTML content was sent.
       *   Args: none.
       */
      $this->eventbus->emit("on_content_print_after");
    }
    
    
    // Prints an RSS page.
    function print_rss($_forum_id,
                       $_title,
                       $_descr,
                       $_off,
                       $_n_entries) {
      $this->content = "";
      $rss = &new RSSPrinter($this);
      $rss->set_base_url(cfg("rss_url"));
      $rss->set_title($_title);
      $rss->set_description($_descr);
      $rss->set_language(lang("countrycode"));
      $rss->show($_forum_id, $_off, $_n_entries);
      print($this->content);
    } 
    
    
    function destroy() {
      unset($this->content);
      $this->db->Close();
      /* Plugin hook: on_destroy
       *   Called from within Spiff->destroy().
       *   The return value of the callback is ignored.
       *   Args: None.
       */
      $this->eventbus->emit("on_destroy");
    }
  }


  function dieDebug($sError)
  {
     echo "<hr /><div>".$sError."<br /><table border='1'>";
     $sOut=""; $aCallstack=debug_backtrace();
    
     echo "<thead><tr><th>file</th><th>line</th><th>function</th>".
         "</tr></thead>";
     foreach($aCallstack as $aCall)
     {
         if (!isset($aCall['file'])) $aCall['file'] = '[PHP Kernel]';
         if (!isset($aCall['line'])) $aCall['line'] = '';

         echo "<tr><td>{$aCall["file"]}</td><td>{$aCall["line"]}</td>".
             "<td>{$aCall["function"]}</td></tr>";
     }
     echo "</table></div><hr /></p>";
     die();
  }
?>
