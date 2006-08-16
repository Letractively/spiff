<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<title>Spiff&trade; Live Demo</title>
<link rel="stylesheet" type="text/css" href="style.css" />
{literal}
<script language="javascript" type="text/javascript">
<!--
function getChangeLogDiv()
{
  return parent.document.getElementById('changelog');
}

function changePerm(element,
                    actorId,
                    actionName,
                    actionSysname,
                    resourceId,
                    resourceName)
{
  var value     = element.value;
  var changelog = getChangeLogDiv();
  var item      = parent.document.createElement('li');
  //FIXME: Also append using hidden form values, so that we can retrieve it later.
  if (value == -1)
    item.innerHTML += 'Give the same <i>' + actionName + '</i> permissions'
                   +  ' on ' + resourceName + ' as the parent group.';
  else if (value == 1)
    item.innerHTML += 'Grant <i>' + actionName + '</i> permissions'
                   +  ' on ' + resourceName + '.';
  else
    item.innerHTML += 'Deny <i>' + actionName + '</i> permissions'
                   +  ' on ' + resourceName + '.';
  changelog.appendChild(item);
}
// -->
</script>
{/literal}
</head>

<body>
<table class="permissions" border="0" cellpadding="0" cellspacing="3">
  <tr>
    <th></th>
    <th>View</th>
    <th>Edit</th>
    <th>Delete</th>
    <th>Create new<br/>Users</th>
    <th>Administer</th>
    {foreach from=$titles item=title}
      <th align='left'>{$title}</th>
    {/foreach}
    </tr>
{if $parent}
  <tr>
    <td>
    <a href="?permission_tree=1&amp;actor_gid={$actor_gid}&amp;resource_gid={$parent->get_id()}">&lt;- Parent Group</a>
    </td>
    <td colspan="5"></td>
  </tr>
{/if}
{foreach from=$groups item=current_group}
    <tr>
      <td><a href="?permission_tree=1&amp;actor_gid={$actor_gid}&amp;resource_gid={$current_group->get_id()}"><img src="img/group.png" alt="Group:" /> {$current_group->get_name()}</a>
      </td>
      {assign var=perms value=$current_group->permission}
      <td align='center'>
      {assign var=perm value=$perms.view}
      {assign var=action value=$perm->action}
      <select name='view' onchange="changePerm(this,
                                               {$actor_gid},
                                               'view',
                                               'view',
                                               {$current_group->get_id()},
                                               '{$current_group->get_name()}');">
        <option value="-1">Default</option>
        <option value="1"{if $perm->allow == "1"} selected="selected"{/if}>Allow</option>
        <option value="0"{if $perm->allow == "0"} selected="selected"{/if}>Deny</option>
      </select>
      </td>
      <td align='center'>
      {assign var=perm value=$perms.edit}
      {assign var=action value=$perm->action}
      <select name='edit' onchange="changePerm(this,
                                               {$actor_gid},
                                               'edit',
                                               'edit',
                                               {$current_group->get_id()},
                                               '{$current_group->get_name()}');">
        <option value="-1">Default</option>
        <option value="1"{if $perm->allow == "1"} selected="selected"{/if}>Allow</option>
        <option value="0"{if $perm->allow == "0"} selected="selected"{/if}>Deny</option>
      </select>
      </td>
      <td align='center'>
      {assign var=perm value=$perms.delete}
      {assign var=action value=$perm->action}
      <select name='delete' onchange="changePerm(this,
                                                 {$actor_gid},
                                                 'delete',
                                                 'delete',
                                                 {$current_group->get_id()},
                                                 '{$current_group->get_name()}');">
        <option value="-1">Default</option>
        <option value="1"{if $perm->allow == "1"} selected="selected"{/if}>Allow</option>
        <option value="0"{if $perm->allow == "0"} selected="selected"{/if}>Deny</option>
      </select>
      </td>
      <td align='center'>
      {assign var=perm value=$perms.create}
      {assign var=action value=$perm->action}
      <select name='create' onchange="changePerm(this,
                                                 {$actor_gid},
                                                 'create',
                                                 'create',
                                                 {$current_group->get_id()},
                                                 '{$current_group->get_name()}');">
        <option value="-1">Default</option>
        <option value="1"{if $perm->allow == "1"} selected="selected"{/if}>Allow</option>
        <option value="0"{if $perm->allow == "0"} selected="selected"{/if}>Deny</option>
      </select>
      </td>
      <td align='center'>
      {assign var=perm value=$perms.administer}
      {assign var=action value=$perm->action}
      <select name='administer' onchange="changePerm(this,
                                                     {$actor_gid},
                                                     'administration',
                                                     'administer',
                                                     {$current_group->get_id()},
                                                     '{$current_group->get_name()}');">
        <option value="-1">Default</option>
        <option value="1"{if $perm->allow == "1"} selected="selected"{/if}>Allow</option>
        <option value="0"{if $perm->allow == "0"} selected="selected"{/if}>Deny</option>
      </select>
      </td>
    </tr>
  {/foreach}
</table>
</body>
</html>
