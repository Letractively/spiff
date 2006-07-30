<table class="container" width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td width="14"><img src="img/corner_top_left.png" alt="" height="14" width="14" /></td>
    <td><img src="img/line_top.png" alt="" height="14" width="100%" /></td>
    <td width="14"><img src="img/corner_top_right.png" alt="" height="14" width="14" /></td>
    <td></td>
    <td><img src="img/corner_top_left.png" alt="" height="14" width="14" /></td>
    <td width="100%"><img src="img/line_top.png" alt="" height="14" width="100%" /></td>
    <td><img src="img/corner_top_right.png" alt="" height="14" width="14" /></td>
  </tr>
  <tr>
    <td><img src="img/line_left.png" alt="" height="100%" width="14" /></td>
    <td valign="top">
    <table class="menu" width="100%" cellpadding="0">
{foreach from=$groups item=group}
      <tr><td><img src="img/group.png" alt="Group:" /> {$group.name} ({$group.count})</td></tr>
{/foreach}
{if $users}
      <tr><td height="1" bgcolor="#aaaaaa"></td></tr>
{/if}
{foreach from=$users item=user}
      <tr><td><img src="img/user.png" alt="User:" /> {$user}</td></tr>
{/foreach}
    </table>
    </td>
    <td><img src="img/line_right.png" alt="" height="100%" width="14" /></td>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
    <td><img src="img/line_left.png" alt="" height="100%" width="14" /></td>
    <td>
    <form action="?submit=1" method="POST">
    <h2>Group "Everybody"</h2>
    <table width='100%' cellpadding="0" cellspacing="0"><tr><td height="1" bgcolor="#000000"></td></tr></table>
    <h3>Public Group Information</h3>
    <table class="indent" width="100%" cellpadding="0" cellspacing="5">
      <tr><td class="nowrap">Group Name:</td><td width="100%"><input type="text" class="field" name="name" value="Everybody" /></td></tr>
      <tr><td class="nowrap" valign="top">Description:</td><td width="100%"><textarea name="description">People</textarea></td></tr>
    </table>

    <h3>Defaults</h3>
    <table class="indent" cellpadding="0">
      <tr>
        <td>Content created by users in this group is by default owned by:</td>
        <td><select name="select"><option>Group</option><option>User</option></td>
      </tr>
    </table>

    <h3>Grant Access To This Group</h3>
    <table class="indent" cellpadding="3">
      <tr>
        <td class="nowrap">Specify users who may</td>
        <td class="nowrap"><input type="checkbox" class="check" name="group_view" checked="checked" />view,</td>
        <td class="nowrap"><input type="checkbox" class="check" name="group_create" checked="checked" />add,</td>
      </tr>
      <tr>
        <td></td>
        <td><img src="img/0.png" alt="" width="180" height="1" /><select name="select" class="multiple" multiple><option>Administrators</option><option>User</option></td>
        <td><img src="img/0.png" alt="" width="180" height="1" /><select name="select" class="multiple" multiple><option>Group</option><option>User</option></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td class="nowrap"><input type="checkbox" class="check" name="group_edit" />edit, or</td>
        <td class="nowrap" colspan="2"><input type="checkbox" class="check" name="group_delete" />delete the members in this group.</td>
      </tr>
      <tr>
        <td></td>
        <td><img src="img/0.png" alt="" width="180" height="1" /><select name="select" class="multiple" multiple><option>Group</option><option>User</option></td>
        <td><img src="img/0.png" alt="" width="180" height="1" /><select name="select" class="multiple" multiple><option>Group</option><option>User</option></td>
        <td width="100%">&nbsp;</td>
        <td></td>
      </tr>
    </table>
    </form>
    </td>
    <td><img src="img/line_right.png" alt="" height="100%" width="14" /></td>
  </tr>
  <tr>
    <td><img src="img/corner_bottom_left.png" alt="" height="14" width="14" /></td>
    <td><img src="img/line_bottom.png" alt="" height="14" width="100%" /></td>
    <td><img src="img/corner_bottom_right.png" alt="" height="14" width="14" /></td>
    <td></td>
    <td><img src="img/corner_bottom_left.png" alt="" height="14" width="14" /></td>
    <td><img src="img/line_bottom.png" alt="" height="14" width="100%" /></td>
    <td><img src="img/corner_bottom_right.png" alt="" height="14" width="14" /></td>
  </tr>
  <tr>
    <td colspan="3">
    <table width="100%">
      <tr>
        <td><input type="button" class="button" name="group_add" value="Add New Group" /></td>
        <td>&nbsp;</td>
        <td><input type="button" class="button" name="user_add" value="Add New User" /></td>
      </tr>
    </table>
    </td>
    <td></td>
    <td colspan="3" align="right">
    <table>
      <tr>
        <td><input type="button" class="button" name="delete" value="Delete Group" /></td>
        <td>&nbsp;</td>
        <td><input type="button" class="button" name="save" value="Apply Changes" /></td>
      </tr>
    </table>
    </td>
  </tr>
</table>
