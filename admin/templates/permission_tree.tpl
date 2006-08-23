<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<title>Spiff&trade; Live Demo</title>
<link rel="stylesheet" type="text/css" href="style.css" />
{literal}
<script language="javascript" type="text/javascript">
<!--
function setHeight()
{
  var iframe = parent.document.getElementById('permission_tree');
  var table  = document.getElementById('permission_table');
  var height = document.body.scrollHeight;
  table.style.visibility = "visible";
  iframe.setAttribute('height', height);
}

function getLogEntry(actionName, resourceName, value)
{
  if (value == -1)
    return 'Give the same <i>' + actionName + '</i> permissions'
         + ' on ' + resourceName + ' as the parent group.';
  else if (value == 1)
    return 'Grant <i>' + actionName + '</i> permissions on ' + resourceName + '.';
  else
    return 'Deny <i>' + actionName + '</i> permissions on ' + resourceName + '.';
}

function incrementItemCount()
{
  var input = parent.document.getElementById('changelog_length');
  if (!input) {
    var changelog = parent.document.getElementById('changelog');
    changelog.innerHTML = '';

    input = parent.document.createElement('input');
    input.setAttribute('type',  'hidden');
    input.setAttribute('id',    'changelog_length');
    input.setAttribute('value', 1);
    changelog.appendChild(input);
    
    ol = parent.document.createElement('ol');
    ol.setAttribute('id', 'changelog_list');
    changelog.appendChild(ol);
    return 1;
  }
  var count = parseInt(input.getAttribute('value'), 10);
  input.setAttribute('value', count + 1);
  return count + 1;
}

/**
 * Stores the given permission of the given resourceId/action in an
 * input field in the parent document. Will re-use existing input
 * fields if they already exist.
 */
function changePerm(element,
                    actionId,
                    actionName,
                    resourceId,
                    resourceName)
{
  var permit       = element.value;
  var li_name      = 'changelog_li_'
                   + resourceId
                   + '_' + actionId;
  var input_prefix = 'changelog_input_'
                   + resourceId
                   + '_' + actionId;
  var editor            = parent.document;
  var li_item           = editor.getElementById(li_name);
  var input_item_action = editor.getElementById(input_prefix + '_action');
  var input_item_permit = editor.getElementById(input_prefix + '_permit');

  if (!li_item) {
    // Create one element containing an array of all changed properties.
    var count     = incrementItemCount().toString();
    var changelog = parent.document.getElementById('changelog_list');

    li_item = parent.document.createElement('li');
    li_item.setAttribute('id', li_name);
    changelog.appendChild(li_item);

    input_item = parent.document.createElement('input');
    input_item.setAttribute('type', 'hidden');
    input_item.setAttribute('name', 'changelog_entries[' + count + ']');
    input_item.setAttribute('id',   'changelog_entries_' + count);
    input_item.setAttribute('value', input_prefix);
    changelog.appendChild(input_item);

    input_item_action = parent.document.createElement('input');
    input_item_action.setAttribute('name', input_prefix + '_action');
    input_item_action.setAttribute('id',   input_prefix + '_action');
    input_item_action.setAttribute('type', 'hidden');
    changelog.appendChild(input_item_action);

    input_item_permit = parent.document.createElement('input');
    input_item_permit.setAttribute('name', input_prefix + '_permit');
    input_item_permit.setAttribute('id',   input_prefix + '_permit');
    input_item_permit.setAttribute('type', 'hidden');
    changelog.appendChild(input_item_permit);
  }

  input_item_action.setAttribute('value', actionId);
  input_item_permit.setAttribute('value', permit);
  li_item.innerHTML = getLogEntry(actionName, resourceName, permit);
}
// -->
</script>
{/literal}
</head>

<body onload='setHeight()'>
<table class="permissions" id='permission_table' style="visibility: hidden" border="0" cellpadding="0" cellspacing="3">
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
{if $resource}
  <tr>
    <td>
    <a href="?permission_tree=1&amp;actor_id={$actor_id}{if $parent_id}&amp;resource_id={$parent_id}{/if}">&lt;- Parent Group</a>
    </td>
    <td colspan="5"></td>
  </tr>
{/if}
{foreach from=$groups item=current_group}
  <tr>
    <td>
    <a href="?permission_tree=1&amp;actor_id={$actor_id}&amp;{if $resource}parent_id={$resource->get_id()}&amp;{/if}resource_id={$current_group->get_id()}"><img src="img/group.png" alt="Group:" /> {$current_group->get_name()}</a>
    </td>
    {assign var=actions value=$current_group->permission}
    {assign var=perm value=$actions.users_administer}
    {if $current_group->get_id() == $actor_id && !$perm->permit}
    <td colspan='5'></td>
    {else}
    <td align='center'>
    {assign var=perm value=$actions.users_view}
    {if $perm}
      {assign var=action    value=$perm->action}
      {assign var=action_id value=$action->get_id()}
      {assign var=permit    value=$perm->permit}
    {/if}
    <select name='view' onchange="changePerm(this,
                                             0{$action_id},
                                             'View',
                                             {$current_group->get_id()},
                                             '{$current_group->get_name()}');">
      <option value="-1">Default</option>
      <option value="1"{if $permit == "1"} selected="selected"{/if}>Allow</option>
      <option value="0"{if $permit == "0"} selected="selected"{/if}>Deny</option>
    </select>
    </td>
    <td align='center'>
    {assign var=perm value=$actions.users_edit}
    {if $perm}
      {assign var=action    value=$perm->action}
      {assign var=action_id value=$action->get_id()}
      {assign var=permit    value=$perm->permit}
    {/if}
    <select name='edit' onchange="changePerm(this,
                                             0{$action_id},
                                             'Edit',
                                             {$current_group->get_id()},
                                             '{$current_group->get_name()}');">
      <option value="-1">Default</option>
      <option value="1"{if $permit == "1"} selected="selected"{/if}>Allow</option>
      <option value="0"{if $permit == "0"} selected="selected"{/if}>Deny</option>
    </select>
    </td>
    <td align='center'>
    {assign var=perm value=$actions.users_delete}
    {if $perm}
      {assign var=action    value=$perm->action}
      {assign var=action_id value=$action->get_id()}
      {assign var=permit    value=$perm->permit}
    {/if}
    <select name='delete' onchange="changePerm(this,
                                               0{$action_id},
                                               'Delete',
                                               {$current_group->get_id()},
                                               '{$current_group->get_name()}');">
      <option value="-1">Default</option>
      <option value="1"{if $permit == "1"} selected="selected"{/if}>Allow</option>
      <option value="0"{if $permit == "0"} selected="selected"{/if}>Deny</option>
    </select>
    </td>
    <td align='center'>
    {assign var=perm value=$actions.users_create}
    {if $perm}
      {assign var=action    value=$perm->action}
      {assign var=action_id value=$action->get_id()}
      {assign var=permit    value=$perm->permit}
    {/if}
    <select name='create' onchange="changePerm(this,
                                               0{$action_id},
                                               'Create',
                                               {$current_group->get_id()},
                                               '{$current_group->get_name()}');">
      <option value="-1">Default</option>
      <option value="1"{if $permit == "1"} selected="selected"{/if}>Allow</option>
      <option value="0"{if $permit == "0"} selected="selected"{/if}>Deny</option>
    </select>
    </td>
    <td align='center'>
    {assign var=perm value=$actions.users_administer}
    {if $perm}
      {assign var=action    value=$perm->action}
      {assign var=action_id value=$action->get_id()}
      {assign var=permit    value=$perm->permit}
    {/if}
    <select name='administer' onchange="changePerm(this,
                                                   0{$action_id},
                                                   'Administer',
                                                   {$current_group->get_id()},
                                                   '{$current_group->get_name()}');">
      <option value="-1">Default</option>
      <option value="1"{if $permit == "1"} selected="selected"{/if}>Allow</option>
      <option value="0"{if $permit == "0"} selected="selected"{/if}>Deny</option>
    </select>
    </td>
    {/if}
  </tr>
{/foreach}

{foreach from=$items item=current}
  <tr>
    <td>
      <img src="img/user.png" alt="User:" /> {$current->get_name()}
    </td>
    <td align='center'>
    {assign var=actions value=$current->permission}
    {assign var=perm value=$actions.users_view}
    {if $perm}
      {assign var=action    value=$perm->action}
      {assign var=action_id value=$action->get_id()}
      {assign var=permit    value=$perm->permit}
    {/if}
    <select name='view' onchange="changePerm(this,
                                             0{$action_id},
                                             'view',
                                             {$current->get_id()},
                                             '{$current->get_name()}');">
      <option value="-1">Default</option>
      <option value="1"{if $permit == "1"} selected="selected"{/if}>Allow</option>
      <option value="0"{if $permit == "0"} selected="selected"{/if}>Deny</option>
    </select>
    </td>
    <td align='center'>
    {assign var=perm value=$actions.users_edit}
    {if $perm}
      {assign var=action    value=$perm->action}
      {assign var=action_id value=$action->get_id()}
      {assign var=permit    value=$perm->permit}
    {/if}
    <select name='edit' onchange="changePerm(this,
                                             0{$action_id},
                                             'edit',
                                             {$current->get_id()},
                                             '{$current->get_name()}');">
      <option value="-1">Default</option>
      <option value="1"{if $permit == "1"} selected="selected"{/if}>Allow</option>
      <option value="0"{if $permit == "0"} selected="selected"{/if}>Deny</option>
    </select>
    </td>
    <td align='center'>
    {assign var=perm value=$actions.users_delete}
    {if $perm}
      {assign var=action    value=$perm->action}
      {assign var=action_id value=$action->get_id()}
      {assign var=permit    value=$perm->permit}
    {/if}
    <select name='delete' onchange="changePerm(this,
                                               0{$action_id},
                                               'delete',
                                               {$current->get_id()},
                                               '{$current->get_name()}');">
      <option value="-1">Default</option>
      <option value="1"{if $permit == "1"} selected="selected"{/if}>Allow</option>
      <option value="0"{if $permit == "0"} selected="selected"{/if}>Deny</option>
    </select>
    </td>
    <td align='center'>
    </td>
    <td align='center'>
    {assign var=perm value=$actions.users_administer}
    {if $perm}
      {assign var=action    value=$perm->action}
      {assign var=action_id value=$action->get_id()}
      {assign var=permit    value=$perm->permit}
    {/if}
    <select name='administer' onchange="changePerm(this,
                                                   0{$action_id},
                                                   'administer',
                                                   {$current->get_id()},
                                                   '{$current->get_name()}');">
      <option value="-1">Default</option>
      <option value="1"{if $permit == "1"} selected="selected"{/if}>Allow</option>
      <option value="0"{if $permit == "0"} selected="selected"{/if}>Deny</option>
    </select>
    </td>
  </tr>
{/foreach}
</table>
</body>
</html>
