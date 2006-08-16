{literal}
<script>
<!-- Start Hide

function change_members() {
  document.writeln('<font face="Arial" size="4">' + output_text + '</font><Br><Br>');
}

// End Hide-->
</script>
{/literal}
<form action="?manage_users=1&amp;{if $parent_gid != $group->get_id()}parent_gid={$parent_gid}&amp;{/if}gid={$group->get_id()}" method="post">
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
      <tr><td align='center'><i>Members</i></td></tr>
{foreach from=$groups item=current}
      <tr><td><a href="?manage_users=1&amp;parent_gid={$group->get_id()}&amp;gid={$current->get_id()}"><img src="img/group.png" alt="Group:" /> {$current->get_name()}</a> ({$current->get_n_children()})</td></tr>
{/foreach}
{if $groups and $users}
      <tr><td height="3"></td></tr>
      <tr><td height="1" bgcolor="#aaaaaa"></td></tr>
      <tr><td height="3"></td></tr>
{/if}
{foreach from=$users item=current}
      <tr><td><a href="?manage_users=1&amp;parent_gid={$group->get_id()}&amp;uid={$current->get_id()}"><img src="img/user.png" alt="User:" /> {$current->get_name()}</a></td></tr>
{/foreach}
    </table>
    </td>
    <td width='14' style='background: url(img/line_right.png)'></td>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
    <td width='14' style='background: url(img/line_left.png)'></td>
    <td>
{if $group->get_id() == 0}
    <h2>Create A New Group</h2>
{else}
    <h2>{$group->get_name()}</h2>
{/if}
    <table width='100%' cellpadding="0" cellspacing="0"><tr><td height="1" bgcolor="#000000"></td></tr></table>
    <h3>Public Group Information</h3>
    <table class="indent" width="100%" cellpadding="0" cellspacing="5">
      <tr><td class="nowrap">Group Name:</td><td width="100%"><input type="text" class="field" name="name" value="{$group->get_name()}" /></td></tr>
      <tr><td class="nowrap" valign="top">Description:</td><td width="100%"><textarea name="description" rows="3" cols="80">{$group->get_attribute('description')}</textarea></td></tr>
    </table>

    <h3>Defaults</h3>
    <table class="indent" cellpadding="0">
      <tr>
        <td>Content created by users in this group is by default owned by:</td>
        <td>
        <select name="use_group_rights">
          <option value="1"{if $group->get_attribute('use_group_rights')} selected="selected"{/if}>Group</option>
          <option value="0"{if !$group->get_attribute('use_group_rights')} selected="selected"{/if}>User</option>
        </select>
        </td>
      </tr>
    </table>

{assign var=gid value=$group->get_id()}
{assign var=perm_url value="?edit_permissions=1&amp;gid=$gid"}

    <h3>Things That The Users In This Group May Do</h3>
    <iframe id='permission_tree' src="index_noheader.php?permission_tree=1&amp;actor_gid={$group->get_id()}" border="0" width="100%" height="30">
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
{if $group->get_id() != 0}
    <table width="100%">
      <tr>
        <td><input type="submit" class="button" name="group_add" value="Add New Group" /></td>
        <td>&nbsp;</td>
        <td><input type="submit" class="button" name="user_add" value="Add New User" /></td>
      </tr>
    </table>
{/if}
    </td>
    <td></td>
    <td colspan="3" align="right">
    <table>
      <tr>
        <td><input type="submit" class="button" name="delete" value="Delete Group" /></td>
        <td>&nbsp;</td>
        <td><input type="submit" class="button" name="save" value="Apply Changes" /></td>
      </tr>
    </table>
    </td>
  </tr>
</table>
</form>
