<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=iso-8859-1" />
  <title>Spiff&trade; Installer</title>
  <link rel=stylesheet type="text/css" href="style.css" />
</head>

<body>
<table class="header" width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td class="banner_left" width="50"><a class="title" href="."><img class="logo" src="img/logo_medium.png" alt="" border="0" /></a></td>
    <td class="banner_left"><a class="title" href="."><span class="title">Spiff</span><span class="trade">&trade;</span><span class="title"> Web Installer</span></a></td>
    <td class="banner_right" align="right" width="482"></td>
  </tr>
</table>

<div align='center'>
<table cellpadding='10'>
  <tr>
    <td>
    <h2>Install Spiff&trade; Now?</h2>
    </td>
  </tr>
  <tr>
    <td align='center' bgcolor='#f2f2ff'>
    <font color='red' size='+2'>Caution!</font><br/><br/>
    <font color='red'>Installing Spiff&trade; will <b>erase
    any data</b> (users, content) from previous installations!<br/><br/>
    Do you really want to proceed?</font><br/>
    </td>
  </tr>
  <tr>
    <td align='right' bgcolor='#fffefe'>
    <form action='setup_now.php5' method=POST>
    <br/><?=gettext('New Administrator Password:')?> <input type='password' name='admin_pwd' /><br/><br/>
    <input type='submit' name='do' value='Delete Data And Install Now!' />
    </form>
    </td>
  </tr>
</table>
</div>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr><td height="1" bgcolor="#888888"></td></tr>
  <tr>
    <td align="right"><table class="footer"><tr><td><img src="img/logo_small.png" alt="" /></td><td>powered by spiff</td></tr></table></td>
  </tr>
</table>

</body>
</html>
