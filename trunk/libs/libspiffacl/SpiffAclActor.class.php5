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
define('SPIFF_ACL_ACTOR_AUTH_STRING_SALT_LEN', 4);
define('SPIFF_ACL_ACTOR_AUTH_STRING_SALT',
       substr(base64_encode(pack("H*",
                                 sha1(mt_rand()))),
                                 0,
                                 SPIFF_ACL_ACTOR_AUTH_STRING_SALT_LEN));

class SpiffAclActor extends SpiffAclResource {
  public function __construct($name, $handle = NULL) {
    parent::__construct($name, $handle);
    $this->set_auth_string('');
  }
  
  public function is_actor() {
    return TRUE;
  }

  public function set_auth_string($auth) {
    $salt = SPIFF_ACL_ACTOR_AUTH_STRING_SALT;
    $this->set_attribute('auth_string', sha1($auth . $salt) . $salt);
  }

  public function has_auth_string($auth) {
    $salt   = substr($this->get_attribute('auth_string'),
                     SPIFF_ACL_ACTOR_AUTH_STRING_SALT_LEN * -1);
    $string = substr($this->get_attribute('auth_string'),
                     0,
                     SPIFF_ACL_ACTOR_AUTH_STRING_SALT_LEN * -1);
    return (sha1($auth . $salt) == $string);
  }
}
?>
