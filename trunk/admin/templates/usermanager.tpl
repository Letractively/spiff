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
{foreach from=$groups item=current key=gid}
      <tr><td><a href="?manage_users=1&gid={$gid}"><img src="img/group.png" alt="Group:" /> {$current.name}</a> ({$current.count})</td></tr>
{/foreach}
{if $groups and $users}
      <tr><td height="1" bgcolor="#aaaaaa"></td></tr>
{/if}
{foreach from=$users item=current}
      <tr><td><img src="img/user.png" alt="User:" /> {$current.name}</td></tr>
{/foreach}
    </table>
    </td>
    <td><img src="img/line_right.png" alt="" height="100%" width="14" /></td>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
    <td><img src="img/line_left.png" alt="" height="100%" width="14" /></td>
    <td>
    <form action="?submit=1" method="POST">
    <h2>{$group.name}</h2>
    <table width='100%' cellpadding="0" cellspacing="0"><tr><td height="1" bgcolor="#000000"></td></tr></table>
    <h3>Public Group Information</h3>
    <table class="indent" width="100%" cellpadding="0" cellspacing="5">
      <tr><td class="nowrap">Group Name:</td><td width="100%"><input type="text" class="field" name="name" value="{$group.name}" /></td></tr>
      <tr><td class="nowrap" valign="top">Description:</td><td width="100%"><textarea name="description">{$group.description}</textarea></td></tr>
    </table>

    <h3>Defaults</h3>
    <table class="indent" cellpadding="0">
      <tr>
        <td>Content created by users in this group is by default owned by:</td>
        <td>
        <select name="use_group_rights">
          <option{if $group.use_group_rights} selected{/if}>Group</option>
          <option{if !$group.use_group_rights} selected{/if}>User</option>
        </select>
        </td>
      </tr>
    </table>

    <h3>Things This Group May Do</h3>
    <table class="indent" cellpadding="0">
      <tr>
        <td><b>Administrate users</b> in the following groups:</td>
        <td>&nbsp;</td>
        <td>
        {if count($may_admin) == 0}
          <i>(None)</i>
        {else}
          {foreach from=$may_admin item=current key=current_id}
          {$current.name}
          {/foreach}
        {/if}
        </td>
        <td>&nbsp;</td>
        <td><input type="button" name="change" value="Change..." /></td>
      </tr>
      <tr>
        <td><b>Create new users</b> in the following groups:</td>
        <td>&nbsp;</td>
        <td>
        {if count($may_create) == 0}
          <i>(None)</i>
        {else}
          {foreach from=$may_create item=current key=current_id}
          {$current.name}
          {/foreach}
        {/if}
        </td>
        <td>&nbsp;</td>
        <td><input type="button" name="change" value="Change..." /></td>
      </tr>
      <tr>
        <td><b>Modify existing users</b> in the following groups:</td>
        <td>&nbsp;</td>
        <td>
        {if count($may_edit) == 0}
          <i>(None)</i>
        {else}
          {foreach from=$may_edit item=current key=current_id}
          {$current.name}
          {/foreach}
        {/if}
        </td>
        <td>&nbsp;</td>
        <td><input type="button" name="change" value="Change..." /></td>
      </tr>
      <tr>
        <td><b>Delete existing users</b> in the following groups:</td>
        <td>&nbsp;</td>
        <td>
        {if count($may_delete) == 0}
          <i>(None)</i>
        {else}
          {foreach from=$may_delete item=current key=current_id}
          {$current.name}
          {/foreach}
        {/if}
        </td>
        <td>&nbsp;</td>
        <td><input type="button" name="change" value="Change..." /></td>
      </tr>
    </table>

    <h3>Things This Group Is Not Allowed To Do</h3>
    <table class="indent" cellpadding="0">
      <tr>
        <td><b>Create new users</b> in the following groups:</td>
        <td>&nbsp;</td>
        <td><i>(Any)</i></td>
        <td>&nbsp;</td>
        <td><input type="button" name="change" value="Change..." /></td>
      </tr>
      <tr>
        <td><b>Modify existing users</b> in the following groups:</td>
        <td>&nbsp;</td>
        <td><i>(Any)</i></td>
        <td>&nbsp;</td>
        <td><input type="button" name="change" value="Change..." /></td>
      </tr>
      <tr>
        <td><b>Delete existing users</b> in the following groups:</td>
        <td>&nbsp;</td>
        <td><i>(Any)</i></td>
        <td>&nbsp;</td>
        <td><input type="button" name="change" value="Change..." /></td>
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
