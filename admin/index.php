<?php
  /*
  Copyright (C) 2003 Samuel Abels, <spam debain org>
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
  
  require_once '../libs/smarty/Smarty.class.php';
  require_once '../libs/adodb/adodb.inc.php';
  require_once '../libs/phpgacl-v3.3.6/gacl.class.php';
  require_once '../libs/phpgacl-v3.3.6/gacl_api.class.php';
  
  include_once 'functions/config.inc.php';
  include_once 'functions/language.inc.php';
  include_once 'functions/table_names.inc.php';
  include_once 'functions/string.inc.php';
  include_once 'functions/httpquery.inc.php';
  include_once 'functions/files.inc.php';
  
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
  
  include_once 'services/sql_query.class.php';
  include_once 'services/trackable.class.php';
  include_once 'services/plugin_registry.class.php';
  
  
  class Spiff {
    var $db;
    var $registry;
    var $eventbus;
    var $smarty;
    var $gacl;
    
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
      
      // (Ab)use a Trackable as an eventbus.
      $this->eventbus = &new Trackable;

      // Connect to the DB.
      $this->db    = &ADONewConnection(cfg('db_dbn'))
        or die('Spiff::Spiff(): Error: Can\'t connect.'
             . ' Please check username, password and hostname.');

      $this->registry = &new PluginRegistry();
      $this->registry->read_plugins('plugins');
      $this->registry->activate_plugins($this); //FIXME: Make activation configurable.

      /* Plugin hook: on_construct
       *   Called from within the Spiff() constructor before any
       *   other output is produced.
       *   The return value of the callback is ignored.
       *   Args: None.
       */
      $this->eventbus->emit("on_construct");
      
      // Init Smarty.
      $this->smarty = &new Smarty();
      $this->smarty->template_dir = "templates/";
      $this->smarty->compile_dir  = "../libs/smarty/templates_c";
      $this->smarty->cache_dir    = "../libs/smarty/cache";
      $this->smarty->config_dir   = "../libs/smarty/configs";
      $this->smarty->register_function('lang', 'smarty_lang');
      
      $this->gacl = new gacl_api();
      
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
    
    
    function _show_login() {
      $login = &new LoginPrinter($this);
      $login->show();
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


    function &get_gacl() {
      return $this->gacl;
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
      $this->eventbus->emit("on_header_print_before", &$this->content);
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
      $this->eventbus->emit("on_footer_print_before", &$this->content);
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
      elseif (isset($_GET['login']))
        $this->_print_login();   // Write an answer.
      else
        $this->_print_content();

      /* Plugin hook: on_content_print_before
       *   Called before the HTML content is sent.
       *   Args: $html: A reference to the content.
       */
      $this->eventbus->emit("on_content_print_before", &$this->content);
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

  $spiff = new Spiff();
  $spiff->print_header();
  $spiff->show();
  $spiff->print_footer();
?>
