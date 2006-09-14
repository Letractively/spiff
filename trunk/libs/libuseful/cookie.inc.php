<?
function set_cookie($_name, $_value) {
  if ($_COOKIE[$_name] == $_value)
    return FALSE;
  setcookie($_name, $_value);
  $_COOKIE[$_name] = $_value;
  return TRUE;
}
?>
