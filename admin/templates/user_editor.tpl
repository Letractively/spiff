<form action="?manage_users=1&amp;parent_gid={$parent_gid}&amp;uid={$user->get_id()}" method="post">
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
    <td width='14' style='background: url(img/line_left.png);'></td>
    <td valign="top">
    <table class="menu" width="100%" cellpadding="0">
      <tr><td align='center'><i>Member Of:</i></td></tr>
{foreach from=$groups item=current}
      <tr><td><a href="?manage_users=1&gid={$current->get_id()}"><img src="img/group.png" alt="Group:" /> {$current->get_name()}</a></td></tr>
{/foreach}
    </table>
    </td>
    <td width='14' style='background: url(img/line_right.png)'></td>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
    <td width='14' style='background: url(img/line_left.png);'></td>
    <td>
{if $user->get_id() == 0}
    <h2>Create A New User</h2>
{else}
    <h2>{$user->get_name()}</h2>
{/if}
    <table width='100%' cellpadding="0" cellspacing="0"><tr><td height="1" bgcolor="#000000"></td></tr></table>
    <h3>Public User Information</h3>
    <table class="indent" width="100%" cellpadding="0" cellspacing="5">
      <tr><td class="nowrap">User Name:</td><td width="100%"><input type="text" class="field" name="name" value="{$user->get_name()}" /></td></tr>
      <tr><td class="nowrap" valign="top">Description:</td><td width="100%"><textarea name="description">{$user->get_attribute('description')}</textarea></td></tr>
    </table>

    <h3>Defaults</h3>
    <table class="indent" cellpadding="0">
      <tr>
        <td>Content created this user is by default owned by:</td>
        <td>
        <select name="use_group_rights">
          <option value=1{if $user->get_attribute('use_group_rights')} selected{/if}>Group</option>
          <option value=0{if !$user->get_attribute('use_group_rights')} selected{/if}>User</option>
        </select>
        </td>
      </tr>
    </table>

{assign var=uid value=$user->get_id()}
{assign var=perm_url value="?edit_permissions=1&amp;uid=$uid"}

    <h3>Things This User May Do</h3>
    <iframe id='permission_tree' src="index_noheader.php?permission_tree=1&amp;actor_id={$user->get_id()}" border="0" width="100%" height="30">
    </iframe>

    <h3>Unconfirmed Permission Changes</h3>
    <div id='changelog'><i>No permissions changed.</i></div>
    </td>
    <td width='14' style='background: url(img/line_right.png)'></td>
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
{if $user->get_id() != 0}
    <table width="100%">
      <tr>
        <td><input type="submit" class="button" name="cancel_membership" value="Cancel Membership" /></td>
        <td>&nbsp;</td>
        <td><input type="submit" class="button" name="add_membership" value="Add Membership" /></td>
      </tr>
    </table>
{/if}
    </td>
    <td></td>
    <td colspan="3" align="right">
    <table>
      <tr>
        <td><input type="submit" class="button" name="delete" value="Delete User" /></td>
        <td>&nbsp;</td>
        <td><input type="submit" class="button" name="save" value="Apply Changes" /></td>
      </tr>
    </table>
    </td>
  </tr>
</table>
</form>
