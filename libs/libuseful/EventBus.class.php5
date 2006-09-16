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
include_once 'Trackable.class.php5';

class EventBus extends Trackable {
  public function emit() {
    $args        = func_get_args();
    $signal_name = array_shift($args);
    $signal      = $this->__get($signal_name);
    if (isset($signal))
      return $signal->emit($args);
    return FALSE;
  }


  public function register_callback() {
    $args        = func_get_args();
    $signal_name = array_shift($args);
    $func        = array_shift($args);
    $this->add_signal($signal_name);
    $signal = $this->__get($signal_name);
    $signal->connect($func, $args, TRUE);
  }
}
?>
