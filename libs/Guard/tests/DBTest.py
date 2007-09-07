import sys, unittest, re
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

def suite():
    tests = ['testActionSection',
             'testResourceSection',
             'testAction',
             'testActor',
             'testActorGroup',
             'testResource',
             'testResourceGroup',
             'testAcl']
    return unittest.TestSuite(map(DBTest, tests))

from DBReaderTest    import DBReaderTest
from DB              import DB
from ActionSection   import ActionSection
from ResourceSection import ResourceSection
from Action          import Action
from Actor           import Actor
from ActorGroup      import ActorGroup
from Resource        import Resource
from ResourceGroup   import ResourceGroup

def dump_acl_list(acls):
    for acl in acls:
        id          = acl.get_id()
        actor_id    = acl.get_actor_id()
        action_name = acl.get_action().get_name()
        res_id      = acl.get_resource_id()
        permit      = acl.get_permit()
        inh         = acl.get_inherited()
        print 'ACL:', id, actor_id, action_name, res_id, permit, inh

class DBTest(DBReaderTest):
    def setUp(self):
        DBReaderTest.setUp(self)
        self.db = DB(self.engine)
        self.assert_(self.db.install())


    def tearDown(self):
        self.assert_(self.db.clear_database())
        self.assert_(self.db.uninstall())


    def testActionSection(self):
        action_section = ActionSection('user permissions')
        self.assert_(self.db.add_action_section(action_section))
        assert action_section.get_id() >= 0
        action_section.set_name('User Permissions')
        self.assert_(self.db.save_action_section(action_section))
        self.assert_(self.db.delete_action_section(action_section))
        self.assert_(self.db.add_action_section(action_section))


    def testResourceSection(self):
        resource_section = ResourceSection('users')
        self.assert_(self.db.add_resource_section(resource_section))
        assert resource_section.get_id() >= 0
        resource_section.set_name('Users')
        self.assert_(self.db.save_resource_section(resource_section))
        self.assert_(self.db.delete_resource_section(resource_section))
        self.assert_(self.db.add_resource_section(resource_section))


    def testAction(self):
        action_section = ActionSection('user permissions')
        self.assert_(self.db.add_action_section(action_section))

        action = Action('view user')
        self.assert_(self.db.add_action(action, action_section))
        assert action.get_id() >= 0
        action.set_name('View a User')
        self.assert_(self.db.save_action(action, action_section))
        self.assert_(self.db.delete_action_from_id(action.get_id()))

        self.assert_(self.db.add_action(action, action_section))
        handle         = action.get_handle()
        section_handle = action_section.get_handle()
        self.assert_(self.db.delete_action_from_handle(handle, section_handle))

        self.assert_(self.db.add_action(action, action_section))
        self.assert_(self.db.delete_action(action))
        assert action.get_id() < 0
        self.assert_(self.db.add_action(action, action_section))


    def testActor(self):
        resource_section = ResourceSection('users')
        self.assert_(self.db.add_resource_section(resource_section))

        actor = Actor('Admin')
        self.assert_(self.db.add_resource(None, actor, resource_section))
        assert actor.get_id() >= 0
        actor.set_name('Admin User')
        self.assert_(self.db.save_resource(actor, resource_section))
        self.assert_(self.db.delete_resource_from_id(actor.get_id()))
        self.assert_(self.db.add_resource(None, actor, resource_section))


    def testActorGroup(self):
        resource_section = ResourceSection('users')
        self.assert_(self.db.add_resource_section(resource_section))

        # Test ActorGroup.
        actor = ActorGroup('Administrators')
        self.assert_(self.db.add_resource(None, actor, resource_section))
        assert actor.get_id() >= 0
        actor.set_name('Admin Users')
        self.assert_(self.db.save_resource(actor, resource_section))

        sub_resource = Actor('Admin')
        assert self.db.add_resource(actor.get_id(),
                                    sub_resource,
                                    resource_section)
        assert sub_resource.get_id() >= 0
        sub_resource.set_name('Admin User')
        self.assert_(self.db.save_resource(sub_resource, resource_section))
        self.assert_(self.db.delete_resource_from_id(sub_resource.get_id()))
        assert self.db.add_resource(actor.get_id(),
                                    sub_resource,
                                    resource_section)

    def testResource(self):
        resource_section = ResourceSection('websites')
        self.assert_(self.db.add_resource_section(resource_section))

        website = Resource('my website')
        self.assert_(self.db.add_resource(None, website, resource_section))
        assert website.get_id() >= 0
        website.set_name('Homepage')
        self.assert_(self.db.save_resource(website, resource_section))
        self.assert_(self.db.get_resource_from_id(website.get_id()))
        assert self.db.get_resource_from_handle(website.get_handle(),
                                                resource_section.get_handle())
        self.assert_(self.db.delete_resource_from_id(website.get_id()))

        self.assert_(self.db.add_resource(None, website, resource_section))
        handle         = website.get_handle()
        section_handle = resource_section.get_handle()
        self.assert_(self.db.delete_resource_from_handle(handle, section_handle))

        self.assert_(self.db.add_resource(None, website, resource_section))
        self.assert_(self.db.delete_resource(website))
        assert website.get_id() < 0


    def testResourceGroup(self):
        resource_section = ResourceSection('websites')
        self.assert_(self.db.add_resource_section(resource_section))

        homepage = ResourceGroup('my website')
        self.assert_(self.db.add_resource(None, homepage, resource_section))
        assert homepage.get_id() >= 0
        homepage.set_name('Homepage')
        self.assert_(self.db.save_resource(homepage, resource_section))

        child_page = Resource('my child site')
        assert self.db.add_resource(homepage.get_id(),
                                    child_page,
                                    resource_section)
        assert child_page.get_id() >= 0
        child_page.set_name('Child Page')
        self.assert_(self.db.save_resource(child_page, resource_section))
        self.assert_(self.db.delete_resource_from_id(child_page.get_id()))
        assert self.db.add_resource(homepage.get_id(),
                                    child_page,
                                    resource_section)

        children = self.db.get_resource_children_from_id(homepage.get_id())
        assert children is not None
        assert len(children) == 1
        children = self.db.get_resource_children(homepage)
        assert children is not None
        assert len(children) == 1

        parents = self.db.get_resource_parents_from_id(child_page.get_id())
        assert parents is not None
        assert len(parents) == 1
        parents = self.db.get_resource_parents(child_page)
        assert parents is not None
        assert len(parents) == 1


    def testAcl(self):
        # Set up sections.
        action_section  = ActionSection('user permissions')
        user_section    = ResourceSection('Users')
        content_section = ResourceSection('Content')
        self.assert_(self.db.add_action_section(action_section))
        self.assert_(self.db.add_resource_section(user_section))
        self.assert_(self.db.add_resource_section(content_section))

        # Set up actions.
        view = Action('View Content')
        self.assert_(self.db.add_action(view, action_section))
        edit = Action('Edit Content')
        self.assert_(self.db.add_action(edit, action_section))
        delete = Action('Delete Content')
        self.assert_(self.db.add_action(delete, action_section))
        
        view_user = Action('View User')
        self.assert_(self.db.add_action(view_user, action_section))
        edit_user = Action('Edit User')
        self.assert_(self.db.add_action(edit_user, action_section))
        delete_user = Action('Delete User')
        self.assert_(self.db.add_action(delete_user, action_section))

        # Set up content.
        homepage         = ResourceGroup('Homepage')
        sub_page_1       = ResourceGroup('Sub Page 1')
        sub_page_1_1     = ResourceGroup('Sub Page 1.1')
        sub_page_1_1_1   = ResourceGroup('Sub Page 1.1.1')
        sub_page_1_1_1_1 = ResourceGroup('Sub Page 1.1.1.1')
        sub_page_1_2     = ResourceGroup('Sub Page 1.2')
        sub_page_2       = ResourceGroup('Sub Page 2')
        self.assert_(self.db.add_resource(None, homepage, content_section))
        assert self.db.add_resource(homepage.get_id(),
                                    sub_page_1,
                                    content_section)
        assert self.db.add_resource(sub_page_1.get_id(),
                                    sub_page_1_1,
                                    content_section)
        assert self.db.add_resource(sub_page_1_1.get_id(),
                                    sub_page_1_1_1,
                                    content_section)
        assert self.db.add_resource(sub_page_1_1_1.get_id(),
                                    sub_page_1_1_1_1,
                                    content_section)
        assert self.db.add_resource(sub_page_1.get_id(),
                                    sub_page_1_2,
                                    content_section)
        assert self.db.add_resource(homepage.get_id(),
                                    sub_page_2,
                                    content_section)
        
        # Test child counter.
        page = self.db.get_resource_from_id(sub_page_1.get_id())
        assert page.get_n_children() == 2
        page = self.db.get_resource_from_id(sub_page_1_1_1.get_id())
        assert page.get_n_children() == 1
        page = self.db.get_resource_from_id(sub_page_1_1_1_1.get_id())
        assert page.get_n_children() == 0

        # Set up groups.
        users  = ActorGroup('Users')
        guys   = ActorGroup('Guys')
        admins = ActorGroup('Admins')
        self.assert_(self.db.add_resource(None,           users,  user_section))
        self.assert_(self.db.add_resource(users.get_id(), guys,   user_section))
        self.assert_(self.db.add_resource(None,           admins, user_section))
        
        # Set up users.
        user = Actor('Normal User')
        self.assert_(self.db.add_resource(guys.get_id(),   user,  user_section))
        anon = Actor('Anonymous User')
        self.assert_(self.db.add_resource(users.get_id(),  anon,  user_section))
        admin = Actor('Administrator')
        self.assert_(self.db.add_resource(admins.get_id(), admin, user_section))
        
        # Set up ACLs.
        self.db.grant(admins, [view_user, edit_user, delete_user], users)
        self.db.grant(admins, [view, edit, delete], homepage)
        self.db.grant(users,  view,                 homepage)
        self.db.grant(user,   edit,                 sub_page_1)
        self.db.grant(guys,   delete,               homepage)
        self.db.deny(anon,    view,                 sub_page_1)

        # Test Acl.
        self.assert_(self.db.has_permission(admin, view, homepage))
        self.assert_(self.db.has_permission(admin, view, sub_page_1))
        self.assert_(self.db.has_permission(admin, view, sub_page_1_1))
        self.assert_(self.db.has_permission(admin, view, sub_page_1_1_1))
        self.assert_(self.db.has_permission(admin, view, sub_page_1_1_1_1))
        self.assert_(self.db.has_permission(admin, view, sub_page_1_2))
        self.assert_(self.db.has_permission(admin, view, sub_page_2))

        self.assert_(self.db.has_permission(admin, edit, homepage))
        self.assert_(self.db.has_permission(admin, edit, sub_page_1))
        self.assert_(self.db.has_permission(admin, edit, sub_page_1_1))
        self.assert_(self.db.has_permission(admin, edit, sub_page_1_1_1))
        self.assert_(self.db.has_permission(admin, edit, sub_page_1_1_1_1))
        self.assert_(self.db.has_permission(admin, edit, sub_page_1_2))
        self.assert_(self.db.has_permission(admin, edit, sub_page_2))

        self.assert_(self.db.has_permission(admin, delete, homepage))
        self.assert_(self.db.has_permission(admin, delete, sub_page_1))
        self.assert_(self.db.has_permission(admin, delete, sub_page_1_1))
        self.assert_(self.db.has_permission(admin, delete, sub_page_1_1_1))
        self.assert_(self.db.has_permission(admin, delete, sub_page_1_1_1_1))
        self.assert_(self.db.has_permission(admin, delete, sub_page_1_2))
        self.assert_(self.db.has_permission(admin, delete, sub_page_2))

        self.assert_(self.db.has_permission(user, view, homepage))
        self.assert_(self.db.has_permission(user, view, sub_page_1))
        self.assert_(self.db.has_permission(user, view, sub_page_1_1))
        self.assert_(self.db.has_permission(user, view, sub_page_1_1_1))
        self.assert_(self.db.has_permission(user, view, sub_page_1_1_1_1))
        self.assert_(self.db.has_permission(user, view, sub_page_1_2))
        self.assert_(self.db.has_permission(user, view, sub_page_2))

        self.assert_(not self.db.has_permission(user, edit, homepage))
        self.assert_(self.db.has_permission(user, edit, sub_page_1))
        self.assert_(self.db.has_permission(user, edit, sub_page_1_1))
        self.assert_(self.db.has_permission(user, edit, sub_page_1_1_1))
        self.assert_(self.db.has_permission(user, edit, sub_page_1_1_1_1))
        self.assert_(self.db.has_permission(user, edit, sub_page_1_2))
        self.assert_(not self.db.has_permission(user, edit, sub_page_2))

        self.assert_(self.db.has_permission(user, delete, homepage))
        self.assert_(self.db.has_permission(user, delete, sub_page_1))
        self.assert_(self.db.has_permission(user, delete, sub_page_1_1))
        self.assert_(self.db.has_permission(user, delete, sub_page_1_1_1))
        self.assert_(self.db.has_permission(user, delete, sub_page_1_1_1_1))
        self.assert_(self.db.has_permission(user, delete, sub_page_1_2))
        self.assert_(self.db.has_permission(user, delete, sub_page_2))

        self.assert_(self.db.has_permission(anon, view, homepage))
        self.assert_(not self.db.has_permission(anon, view, sub_page_1))
        self.assert_(not self.db.has_permission(anon, view, sub_page_1_1))
        self.assert_(not self.db.has_permission(anon, view, sub_page_1_1_1))
        self.assert_(not self.db.has_permission(anon, view, sub_page_1_1_1_1))
        self.assert_(not self.db.has_permission(anon, view, sub_page_1_2))
        self.assert_(self.db.has_permission(anon, view, sub_page_2))

        self.assert_(not self.db.has_permission(anon, edit, homepage))
        self.assert_(not self.db.has_permission(anon, edit, sub_page_1))
        self.assert_(not self.db.has_permission(anon, edit, sub_page_1_1))
        self.assert_(not self.db.has_permission(anon, edit, sub_page_1_1_1))
        self.assert_(not self.db.has_permission(anon, edit, sub_page_1_1_1_1))
        self.assert_(not self.db.has_permission(anon, edit, sub_page_1_2))
        self.assert_(not self.db.has_permission(anon, edit, sub_page_2))

        self.assert_(not self.db.has_permission(anon, delete, homepage))
        self.assert_(not self.db.has_permission(anon, delete, sub_page_1))
        self.assert_(not self.db.has_permission(anon, delete, sub_page_1_1))
        self.assert_(not self.db.has_permission(anon, delete, sub_page_1_1_1))
        self.assert_(not self.db.has_permission(anon, delete, sub_page_1_1_1_1))
        self.assert_(not self.db.has_permission(anon, delete, sub_page_1_2))
        self.assert_(not self.db.has_permission(anon, delete, sub_page_2))

        # Get permissions one one specific resource.
        pageid = sub_page_1_1_1.get_id()
        perms  = self.db.get_permission_list_from_id(guys.get_id(),
                                                     resource_id = pageid)
        #dump_acl_list(perms)

        # Get recursive permissions one one specific resource.
        perms  = self.db.get_permission_list_from_id_with_inheritance(
                                            actor_id    = guys.get_id(),
                                            resource_id = pageid)
        #dump_acl_list(perms)

        # Get permissions one all resources.
        perms = self.db.get_permission_list_from_id_with_inheritance()

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
