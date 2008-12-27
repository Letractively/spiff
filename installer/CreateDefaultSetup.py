# Copyright (C) 2008 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import config, util, os.path
from services   import PageDB
from objects    import UserAction, PageAction
from sqlalchemy import create_engine
from Step       import Step

class CreateDefaultSetup(Step):
    def __init__(self, id, request, state):
        Step.__init__(self, id, request, state)
        # Install files and directories.
        self.result1 = [util.create_dir(config.package_dir),
                        util.create_dir(config.upload_dir),
                        util.create_dir(config.warehouse_dir),
                        util.create_dir(config.cache_dir),
                        util.merge_rawconfig_file('spiff.cfg.tmpl',
                                                  config.cfg_file)]

        # Set up Python modules.
        self.result2 = [util.create_dir(config.package_dir),
                        self._connect_db(),
                        self._install_guard(),
                        self._install_integrator(),
                        self._install_warehouse(),
                        self._install_cache()]

        # Install extensions.
        extensions = ['Spiff',
                      'Login',
                      'Register',
                      'AdminCenter',
                      'UserManager',
                      'PageEditor',
                      'ExtensionManager',
                      'WikiPage']
        self.result3 = [self._install_extension(e) for e in extensions]

        # Define permission types.
        permissions = [(UserAction, 'administer',   'Administer User'),
                       (UserAction, 'view',         'View User'),
                       (UserAction, 'edit',         'Edit User'),
                       (UserAction, 'moderate',     'Moderate User'),
                       (PageAction, 'create',       'Create Page'),
                       (PageAction, 'view',         'View Page'),
                       (PageAction, 'edit',         'Edit Page'),
                       (PageAction, 'edit_content', 'Edit Page Content'),
                       (PageAction, 'delete',       'Delete Page')]
        self.result4 = [self._create_permission(*p) for p in permissions]

        # Create users and pages.
        resources = {
            'Group|everybody|Everybody|': {
                'Group|administrators|Administrators|': {
                    'User|admin|Administrator|': {}
                },
                'Group|users|Users|': {
                    'User|anonymous|Anonymous George|': {}
                }
            },
            'Page|default|Wiki|': {},
            'Page|admin|Admin Center|': {
                'Page|admin/register|User Registration|': {},
                'Page|admin/login|System Login|': {},
                'Page|admin/users|User Manager|private=1': {},
                'Page|admin/page|Page Editor|private=1': {},
                'Page|admin/extensions|Extension Manager|private=1': {}
            }
        }
        self.result5 = self._create_resource_tree(None, None, resources)

        # Assign extensions to pages.
        extensions = [
            ('default',          'spiff_core_wiki_page',         True),
            ('admin',            'spiff_core_admin_center',      True),
            ('admin/register',   'spiff_core_register',          False),
            ('admin/login',      'spiff_core_login',             False),
            ('admin/users',      'spiff_core_user_manager',      True),
            ('admin/page',       'spiff_core_page_editor',       False),
            ('admin/extensions', 'spiff_core_extension_manager', False)
        ]
        self.result6 = self._assign_extensions(extensions)

        # Assign default permissions.
        permissions = {
            'Deny: Group|everybody -> Group|everybody':
                [(UserAction, 'administer'),
                 (UserAction, 'view'),
                 (UserAction, 'edit'),
                 (UserAction, 'moderate')],
            'Deny: Group|everybody -> Page|default,Page|admin':
                [(PageAction, 'create'),
                 (PageAction, 'view'),
                 (PageAction, 'edit'),
                 (PageAction, 'edit_content'),
                 (PageAction, 'delete')],
            'Grant: Group|administrators -> Group|everybody':
                [(UserAction, 'administer'),
                 (UserAction, 'view'),
                 (UserAction, 'edit'),
                 (UserAction, 'moderate')],
            'Grant: Group|administrators -> Page|default,Page|admin':
                [(PageAction, 'create'),
                 (PageAction, 'view'),
                 (PageAction, 'edit'),
                 (PageAction, 'edit_content'),
                 (PageAction, 'delete')],
            'Grant: Group|users -> Group|everybody':
                [(UserAction, 'view')],
            'Grant: Group|users -> Page|default':
                [(PageAction, 'view')]
        }
        self.result7 = self._assign_permissions(permissions)

        # Done.
        all_results  = self.result1 \
                     + self.result2 \
                     + self.result3 \
                     + self.result4 \
                     + self.result5 \
                     + self.result6 \
                     + self.result7
        self.failed  = False in [r for n, r, e in all_results]

        if not self.failed:
            name, result, hint = self._save_config()
            self.failed        = not result
            self.result1.append((name, result, hint))


    def _save_config(self):
        name = 'Writing final configuration file'
        try:
            from ConfigParser import RawConfigParser
            parser = RawConfigParser()
            parser.read(config.cfg_file)
            parser.set('database',  'dbn',     self.state.dbn)
            parser.set('installer', 'version', config.__version__)
            parser.write(open(config.cfg_file, 'w'))
        except Exception, e:
            return name, False, str(e)
        return name, True, None


    def _connect_db(self):
        name = 'Connecting to the database'
        try:
            self.db = create_engine(self.state.dbn)
        except Exception, e:
            return name, False, str(e)
        return name, True, None


    def _install_guard(self):
        name = 'Installing database tables for SpiffGuard'
        try:
            from SpiffGuard import DB as GuardDB
            self.guard = GuardDB(self.db)
            if not self.guard.install():
                raise Exception('install() returned False')

            # Register Spiff's object types.
            from services import PageDB  # Import required to resolve Page.
            from objects  import User
            from objects  import Group
            from objects  import Page
            from objects  import UserAction
            from objects  import PageAction
            self.guard.register_type([User,
                                      Group,
                                      Page,
                                      UserAction,
                                      PageAction])
        except Exception, e:
            return name, False, str(e)
        return name, True, None


    def _install_integrator(self):
        name = 'Installing database tables for SpiffIntegrator'
        try:
            from SpiffIntegrator import PackageManager, Api
            from services        import PageDB  # Required to resolve Page.
            from objects         import SpiffPackage
            pm = PackageManager(self.guard, Api(), package = SpiffPackage)
            if not pm.install():
                raise Exception('install() returned False')
        except Exception, e:
            return name, False, str(e)
        return name, True, None


    def _install_warehouse(self):
        name = 'Installing database tables for SpiffWarehouse'
        try:
            from SpiffWarehouse import DB as WarehouseDB
            warehouse = WarehouseDB(self.db)
            if not warehouse.install():
                raise Exception('install() returned False')
        except Exception, e:
            return name, False, str(e)
        return name, True, None


    def _install_cache(self):
        name = 'Installing database tables for internal caching'
        try:
            from services import Session
            from services import CacheDB
            session = Session(self.guard,
                              request        = self.request,
                              requested_page = object)
            cache   = CacheDB(self.guard, session)
            if not cache.install():
                raise Exception('install() returned False')
        except Exception, e:
            return name, False, str(e)
        return name, True, None


    def _install_extension(self, filename):
        from SpiffIntegrator import PackageManager
        from services        import ExtensionApi
        from services        import Session
        from services        import PageDB
        from objects         import SpiffPackage
        name = 'Installing extension "%s"' % filename
        try:
            page_db       = PageDB(self.guard)
            session       = Session(self.guard,
                                    request        = self.request,
                                    requested_page = None)
            extension_api = ExtensionApi(session = session,
                                         guard   = self.guard,
                                         page_db = page_db,
                                         request = self.request)
            integrator    = PackageManager(self.guard,
                                           extension_api,
                                           package = SpiffPackage)
            integrator.set_package_dir(config.package_dir)
            filename = os.path.join(config.plugin_dir, filename)
            package  = integrator.read_package(filename)
            integrator.install_package(package)
        except Exception, e:
            return name, False, str(e)
        return name, True, None


    def _get_resource_from_handle(self, type, handle):
        # Load the corresponding class.
        try:
            cls = __import__('objects.' + type,
                             globals(),
                             locals()).__dict__[type]
        except Exception, e:
            raise Exception('Failed to load parent class: %s' % str(e))

        # Find the resource.
        resource = self.guard.get_resource(handle = handle, type = cls)
        if not resource:
            raise Exception('Required resource "%s" not found.' % handle)
        return resource


    def _get_resource_id_from_handle(self, type, handle):
        if handle is None:
            return None
        return self._get_resource_from_handle(type, handle).get_id()


    def _create_resource(self,
                         parent_type,
                         parent_handle,
                         resource_type,
                         resource_handle,
                         resource_name,
                         **kwargs):
        """
        @type  kwargs: dict
        @param kwargs: May contain attributes for the new resource.
        """
        name = 'Creating %s "%s"' % (resource_type, resource_name)

        # Load the corresponding class.
        try:
            resource_cls = __import__('objects.' + resource_type,
                                      globals(),
                                      locals()).__dict__[resource_type]
        except Exception, e:
            return name, False, str(e)

        # Check whether the resource already exists.
        try:
            resource = self.guard.get_resource(handle = resource_handle,
                                               type   = resource_cls)
        except Exception, e:
            return name, False, str(e)
        if resource:
            return name, True, 'Skipped because it already exists.'

        # Create an instance of the resource.
        resource = resource_cls(resource_name, resource_handle)
        for key, value in kwargs.iteritems():
            resource.set_attribute(key, value)

        # Find the parent resource.
        try:
            parent_id = self._get_resource_id_from_handle(parent_type,
                                                          parent_handle)
        except Exception, e:
            return name, False, str(e)

        # Save the resource.
        self.guard.add_resource(parent_id, resource)
        try:
            self.guard.add_resource(parent_id, resource)
        except Exception, e:
            return name, False, str(e)
        return name, True, None


    def _create_resource_tree(self, parent_type, parent_handle, root):
        results = []
        for node, children in root.iteritems():
            # Parse the descriptor.
            type, handle, name, other = node.split('|')
            if other != '':
                attribs = dict([pair.split('=') for pair in other.split(',')])
            else:
                attribs = {}

            # Create the resource.
            result = self._create_resource(parent_type,
                                           parent_handle,
                                           type,
                                           handle,
                                           name)
            results.append(result)
            results += self._create_resource_tree(type, handle, children)
        return results


    def _create_permission(self, action_cls, action_handle, action_name):
        name = 'Creating permission type "%s"' % action_name

        # Check whether the permission type already exists.
        try:
            action = self.guard.get_action(handle = action_handle,
                                           type   = action_cls)
        except Exception, e:
            return name, False, str(e)
        if action:
            return name, True, 'Skipped because it already exists.'

        # Create the action.
        action = action_cls(action_name, action_handle)
        try:
            self.guard.add_action(action)
        except Exception, e:
            return name, False, str(e)
        return name, True, None


    def _get_action_from_handle(self, cls, handle):
        action = self.guard.get_action(handle = handle, type = cls)
        if not action:
            raise Exception('Required action "%s" not found.' % handle)
        return action


    def _get_resources_from_descriptor(self, descriptor):
        resources = []
        for descr in descriptor.split(','):
            resource_type, resource_handle = descr.split('|')
            resource = self._get_resource_from_handle(resource_type,
                                                      resource_handle)
            resources.append(resource)
        return resources


    def _get_actions_from_permissions(self, permissions):
        actions = []
        for action_cls, action_handle in permissions:
            action = self._get_action_from_handle(action_cls, action_handle)
            actions.append(action)
        return actions


    def _assign_permissions(self, permissions):
        results = []
        for descriptor, permissions in permissions.iteritems():
            # Parse the given descriptor string.
            grantdeny,     relation        = descriptor.split(': ')
            actor_descr,   resource_descr  = relation.split(' -> ')
            actor_type,    actor_handle    = actor_descr.split('|')
            permit                         = grantdeny == 'Grant'

            # Fetch the associated objects from the database.
            name = 'Assigning permission %s -> %s' % (actor_descr, resource_descr)
            try:
                actors    = self._get_resources_from_descriptor(actor_descr)
                resources = self._get_resources_from_descriptor(resource_descr)
                actions   = self._get_actions_from_permissions(permissions)
            except Exception, e:
                results.append((name, False, str(e)))
                continue

            # Assign the permission.
            try:
                self.guard.grant(actors, actions, resources)
            except Exception, e:
                results.append((name, False, str(e)))
                continue
            results.append((name, True, None))
        return results


    def _assign_extensions(self, extensions):
        results = []
        for page_handle, extension_handle, recursive in extensions:
            name = 'Assigning %s to %s' % (extension_handle, page_handle)
            page = self._get_resource_from_handle('Page', page_handle)
            page.assign_extension(extension_handle)
            if recursive:
                page.set_attribute('recursive', True)
            try:
                if not self.guard.save_resource(page):
                    raise Exception('Failed to save the resource.')
            except Exception, e:
                results.append((name, False, str(e)))
                continue
            results.append((name, True, None))
        return results


    def show(self):
        self.render('CreateDefaultSetup.tmpl',
                    results1 = self.result1,
                    results2 = self.result2,
                    results3 = self.result3,
                    results4 = self.result4,
                    results5 = self.result5,
                    results6 = self.result6,
                    results7 = self.result7,
                    success  = not self.failed)


    def check(self):
        if self.failed:
            self.show()
            return False
        return True
