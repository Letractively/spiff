<form action='{$smarty.server.REQUEST_URI}' method='POST'>
<table id='login' cellspacing='10' cellpadding='0'>
{if $error}
  <tr>
    <td colspan='2'><font class='error'>{$error}</font></td>
  </tr>
{/if}
  <tr>
    <td>{gettext text="Username:"}</td>
    <td><input type='text'     name='username' value='{$smarty.post.username}' /></td>
  </tr>
  <tr>
    <td>{gettext text="Password:"}</td>
    <td><input type='password' name='password' value='' /></td>
  </tr>
  <tr>
    <td colspan='2' align='right'><input type='submit' name='login' /></td>
  </tr>
</table>
</form>
