<?php
# sig.php, Simple Signaling System.
#
# This is a very simple implementation of a signal system, inspired
# loosely by sigc++ and glib signals.
#
# Copyright (C) 2006 - Steve Frécinaux <steve at istique dot net>
#
# sig.php is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301  USA

class Signal
{
    private $name;            # Name of the signal (default handler will be do_$name)
    private $object;          # Owner of the current signal
    private $expected_args;   # Amount of expected args for the signal emission
    private $run_last;        # Signal runs last by default

    private $callbacks;       # Array containing the callbacks
    private $first_key;       # Lowest key (first signal emitted)
    private $last_key;        # Highest key (last signal emitted)
    private $sorted;          # Is the callback array sorted?

    private $blocked;         # Is the signal currently blocked?

    /**
     * Constructor
     * @param string  $name            The signal name
     * @param object  $object          The parent object
     * @param integer $expected_args   The amount of expected args on emit()
     * @param boolean $run_last        Does the default handler run last?
     */
    function __construct($name,
                         $object = null,
                         $expected_args = -1,
                         $run_last = true)
    {
        $this->name = $name;
        $this->object = $object;
        $this->expected_args = $expected_args;
        $this->run_last = $run_last;
        $this->blocked = false;

        # Reset the callback array
        $this->first_key = 0;
        $this->last_key = 0;
        $this->clear();
    }

    private function connect_real($callback, $args, $before = true)
    {
        $key = $before ? --$this->first_key : ++$this->last_key;
        $this->callbacks[$key] = array($callback, $args);
        $this->sorted = false;
        return $key;
    }

    private function emit_real($args)
    {
        if ($this->expected_args != -1 && count($args) != $this->expected_args)
            throw new Exception(sprintf("Wrong argument count for signal '%s'. " .
                                        "Expected: %d, given: %d",
                                        $this->name,
                                        $this->expected_args,
                                        count($args)));

        if ($this->blocked)
            return;

        if (!$this->sorted) {
            ksort($this->callbacks, SORT_NUMERIC);
            $this->sorted = true;
        }

        foreach ($this->callbacks as $id => $data)
        {
            list($callback, $cargs) = $data;
            $all_args = array_merge($args, $cargs);
          
            # do not prepend the object if it's the default handler
            # (it's the same as $this for this particular case).
            if ($id != 0)
                array_unshift($all_args, $this->object);

            $r = call_user_func_array($callback, $all_args);

            # if the function returned TRUE, we stop emission.
            if ($r) break;
        }
        
        return $r;
    }

    /**
     * Connect a handler to the signal.
     * If the signal is run_last, then the handler will be ran before the
     * default one, otherwise it will be ran after it (like connect_after).
     * @param  string   $callback The handler name
     * @param  variant* $args     Zero or more additional args
     * @return integer            The handler id
     */
    public function connect()
    {
        $args = func_get_args();
        $callback = array_shift($args);
        $this->connect_real($callback, $args, $this->run_last);
    }

    /**
     * Connect a handler to the signal (will be ran last)
     * @param  string   $callback The handler name
     * @param  variant* $args     Zero or more additional args
     * @return integer            The handler id
     */
    public function connect_after()
    {
        $args = func_get_args();
        $callback = array_shift($args);
        $this->connect_real($callback, $args, false);
    }

    /**
     * Emit the signal.
     * This will cause any connected handler to be run
     * @param  variant* $args     Zero or more additional args to be passed to
     *                            the handlers
     */
    public function emit()
    {
        $args = func_get_args();
        return $this->emit_real($args);
    }

    /**
     * Block the signal emission
     * @return boolean            Was the signal blocked?
     */
    public function block()
    {
        $tmp = $this->blocked;
        $this->blocked = true;
        return $tmp;
    }

    /**
     * Unblock the signal emission
     */
    public function unblock()
    {
        $this->blocked = false;
    }

    /**
     * Clear the handler list
     * Note: key_first and key_last are not resetted to avoid deleting newly
     * connected handlers by mistake.
     */
    public function clear()
    {
        $this->callbacks = array();
        $handler = 'do_' . $this->name;
        if (!is_null($this->object) && method_exists($this->object, $handler)) {
            $handler = array($this->object, $handler);
            $this->callbacks[0] = array($handler, array());
        }
    }

    /**
     * Return whether handler_id is the id of a handler connected to instance
     * @param  integer $handler_id  The handler id
     * @return boolean              Whether it is the id of a connected handler
     */
    public function is_connected($handler_id)
    {
        return isset($this->callbacks[$handler_id]);
    }

    /**
     * Disconnect a handler to the signal
     * @param  integer $handler_id  The id of the handler to disconnect
     */
    public function disconnect($handler_id)
    {
        unset($this->callbacks[$handler_id]);
    }
}

/**
 * This class handles the registering and access of signals. It's better,
 * but not required, to use it as a parent class for your own classes.
 *
 * Note: be careful when overwriting __get, __set or __isset.
 */
abstract class Trackable
{
    private $signals = array();

    /**
     * Define a new signal for the class.
     * The new signal can be accessed with $object->$name.
     * @param  string   $name           The signal name
     * @param  integer  $expected_args  The amount of expected args on emit()
     * @param  boolean  $run_last       Does the default handler run last?
     */
    protected function set_signal($name, $expected_args = -1, $run_last = true)
    {
        if (!preg_match('/[a-z_][a-z0-9_]/i', $name))
            throw new Exception("Bad name for signal: $name");
      
        $this->signals[$name] = new Signal($name, $this,
                                           $expected_args, $run_last);
    }

    /**
     * Does the current class have a signal with that name ?
     * @param  string   $name           The signal name
     */
    protected function has_signal($name)
    {
        return isset($this->signals[$name]);
    }

    public function __get($name)
    {
        if (isset($this->signals[$name]))
            return $this->signals[$name];
    }

    public function __set($name, $value)
    {
        if (isset($this->signals[$name]))
            throw new Exception("Can't override signals.");
        else
            $this->$name = $value; # restore the default PHP behaviour
    }

    public function __isset($name)
    {
        return isset($this->signals[$name]);
    }
}
?>
