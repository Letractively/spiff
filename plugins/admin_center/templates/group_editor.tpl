<form action="{$url}&amp;manage_users=1&amp;{if $parent_id != $group->get_id()}parent_id={$parent_id}&amp;{/if}id={$group->get_id()}" method="post">
<table class="container" width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td width='230' valign="top">
    <table class="menu" cellpadding="0">
      <tr><td align='center'><i>Members</i></td></tr>
{foreach from=$groups item=current}
      <tr><td><a href="{$url}&amp;manage_users=1&amp;parent_id={$group->get_id()}&amp;id={$current->get_id()}"><img src="{$plugin_dir}/img/group.png" alt="Group:" /> {$current->get_name()}</a> ({$current->get_n_children()})</td></tr>
{/foreach}
{if $groups and $users}
      <div class='seperator'></div>
{/if}
{foreach from=$users item=current}
      <tr><td><a href="{$url}&amp;manage_users=1&amp;parent_id={$group->get_id()}&amp;id={$current->get_id()}"><img src="{$plugin_dir}/img/user.png" alt="User:" /> {$current->get_name()}</a></td></tr>
{/foreach}
    </table>
    </td>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
    <td width='100%'>
{if $group->get_id() <= 0}
    <h2>Create A New Group</h2>
{else}
    <h2>{$group->get_name()}</h2>
{/if}
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

{assign var=id value=$group->get_id()}
{assign var=perm_url value="?edit_permissions=1&amp;id=$id"}

    <h3>Things That The Users In This Group May Do</h3>
    <iframe id='permission_tree' src="{$url}&amp;permission_tree=1&amp;actor_id={$group->get_id()}" style='border: 0' width="100%" height="30">
    </iframe>

    <h3>Unconfirmed Permission Changes</h3>
    <div id='changelog'><i>No permissions changed.</i></div>
    </td>
  </tr>
  <tr>
    <td>
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
    <td align="right">
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
