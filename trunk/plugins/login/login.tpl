<form action='?login=1' method='POST'>
<table id='login' cellspacing='10' cellpadding='0'>
  <tr>
    <td>{gettext text="Username:"}</td>
    <td><input type='text'     name='username' value='{$username}' /></td>
  </tr>
  <tr>
    <td>{gettext text="Password:"}</td>
    <td><input type='password' name='password' value='{$password}' /></td>
  </tr>
  <tr>
    <td colspan='2' align='right'><input type='submit' /></td>
  </tr>
</table>
</form>
