import sys, unittest, re
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

def suite():
    tests = ['testAction',
             'testResource',
             'testAcl']
    return unittest.TestSuite(map(DBTest, tests))

import datetime
from DBReaderTest  import DBReaderTest
from DB            import DB
from DBObject      import DBObject
from Action        import Action
from Resource      import Resource
from ResourceGroup import ResourceGroup

class User(Resource):
    pass

class Group(User):
    def is_group(self):
        return True

class Content(ResourceGroup):
    pass

def dump_acl_list(acls):
    for acl in acls:
        id          = acl.get_id()
        actor_id    = acl.get_actor_id()
        action_name = repr(acl.get_action().get_name())
        res_id      = acl.get_resource_id()
        permit      = acl.get_permit()
        inh         = acl.get_inherited()
        print 'ACL:', id, actor_id, action_name, res_id, permit, inh

class DBTest(DBReaderTest):
    def setUp(self):
        DBReaderTest.setUp(self)
        self.db = DB(self.engine)
        self.assert_(self.db.uninstall())
        self.assert_(self.db.install())
        self.assert_(self.db.clear_database())
        self.db.register_type(Content)
        self.db.register_type([DBObject, User, Group])


    def tearDown(self):
        #self.assert_(self.db.uninstall())
        pass


    def testAction(self):
        # Test creating a new action.
        action = Action('view user')
        self.assertRaises(AttributeError, self.db.add_action, action)
        self.db.register_type(Action)
        self.assert_(self.db.add_action(action))
        self.assert_(action.get_id() is not None)
        self.assert_(self.db.delete_action(action))
        self.assert_(action.get_id() is None)

        # Test modify.
        action = Action('view user')
        self.assert_(self.db.add_action(action))
        self.assert_(action.get_id() is not None)
        action.set_name('View a User')
        self.assert_(self.db.save_action(action))
        self.assert_(action.get_id() is not None)
        self.assert_(self.db.delete_action_from_match(id = action.get_id()) == 1)
        self.assert_(self.db.get_action(id = action.get_id()) is None)

        # Test del_from_handle (typeless)
        action = Action('view user')
        handle = action.get_handle()
        self.assert_(self.db.add_action(action))
        self.assert_(action.get_id() is not None)
        self.assert_(self.db.delete_action_from_match(handle = handle))
        self.assert_(self.db.get_action(id = action.get_id()) is None)

        # Test del_from_handle (wrong type)
        self.assert_(self.db.add_action(action))
        self.assert_(action.get_id() is not None)
        self.assert_(self.db.delete_action_from_match(handle = handle,
                                                      type   = Content) == 0)
        self.assert_(self.db.get_action(id = action.get_id()) is not None)

        # Test del_from_handle (a base type)
        self.assert_(action.get_id() is not None)
        self.assert_(self.db.delete_action_from_match(handle = handle,
                                                      type   = DBObject) == 1)
        self.assert_(self.db.get_action(id = action.get_id()) is None)

        # Test del_from_handle (exact type)
        self.assert_(self.db.add_action(action))
        self.assert_(action.get_id() is not None)
        self.assert_(self.db.delete_action_from_match(handle = handle,
                                                      type   = Action) == 1)
        self.assert_(self.db.get_action(id = action.get_id()) is None)


    def testResource(self):
        # Create.
        website = Content('my website')
        self.assert_(self.db.add_resource(None, website))
        self.assert_(website.get_id() is not None)

        # Modify.
        website.set_name('Homepage')
        self.assert_(self.db.save_resource(website))
        self.assert_(self.db.get_resource(id     = website.get_id()))
        self.assert_(self.db.get_resource(handle = website.get_handle()))

        # Add a child to a non-parent.
        foo = Resource('no children')
        bar = Resource('child')
        self.assertRaises(AttributeError, self.db.add_resource, foo, bar)
        self.assert_(self.db.add_resource(None, foo))
        self.assertRaises(AttributeError, self.db.add_resource, foo, bar)

        # Delete.
        self.assert_(self.db.delete_resource_from_match(id = website.get_id()))
        self.assert_(self.db.get_resource(id = website.get_id()) is None)

        # Test del_from_handle (typeless)
        website = Content('my website')
        handle  = website.get_handle()
        self.assert_(self.db.add_resource(None, website))
        self.assert_(website.get_id() is not None)
        self.assert_(self.db.delete_resource_from_match(handle = handle))
        self.assert_(self.db.get_resource(id = website.get_id()) is None)

        # Test the type system.
        user = User('sam')
        self.assert_(self.db.add_resource(None, user))
        resource = self.db.get_resource(id = user.get_id())
        self.assert_(resource.__class__.__name__ == 'User')

        # Test parents.
        website1     = Content('my website1')
        website1_1   = Content('my website1_1')
        website1_2   = Content('my website1_2')
        website1_1_1 = Content('my website1_1_1')
        self.assert_(self.db.add_resource(None,       website1))
        self.assert_(self.db.add_resource(website1,   website1_1))
        self.assert_(self.db.add_resource(website1,   website1_2))
        self.assert_(self.db.add_resource(website1_1, website1_1_1))
        self.assert_(website1.get_id()     is not None)
        self.assert_(website1_1.get_id()   is not None)
        self.assert_(website1_2.get_id()   is not None)
        self.assert_(website1_1_1.get_id() is not None)

        # Test get_resource_children().
        children = self.db.get_resource_children(website1)
        self.assert_(len(children) == 2, children)
        self.assert_(children[0].get_id() == website1_1.get_id())
        self.assert_(children[1].get_id() == website1_2.get_id())

        # Test deletion of a node that has children.
        res = self.db.delete_resource_from_match(handle = website1_1.get_handle())
        self.assert_(res == 2, res)
        self.assert_(self.db.get_resource(id = website1.get_id()))
        self.assert_(not self.db.get_resource(id = website1_1.get_id()))
        self.assert_(self.db.get_resource(id = website1_2.get_id()))
        self.assert_(not self.db.get_resource(id = website1_1_1.get_id()))

        # Make sure that the parent is still there and check the child count.
        website1   = self.db.get_resource(id = website1.get_id())
        website1_2 = self.db.get_resource(id = website1_2.get_id())
        self.assert_(website1   is not None)
        self.assert_(website1_2 is not None)
        self.assert_(website1.get_n_children()   == 1)
        self.assert_(website1_2.get_n_children() == 0)


    def testAcl(self):
        # Set up actions.
        view = Action('View Content')
        self.db.register_type(Action)
        self.assert_(self.db.add_action(view))
        edit = Action('Edit Content')
        self.assert_(self.db.add_action(edit))
        delete = Action('Delete Content')
        self.assert_(self.db.add_action(delete))
        
        view_user = Action('View User')
        self.assert_(self.db.add_action(view_user))
        edit_user = Action('Edit User')
        self.assert_(self.db.add_action(edit_user))
        delete_user = Action('Delete User')
        self.assert_(self.db.add_action(delete_user))

        # Set up content.
        homepage         = Content('Homepage')
        sub_page_1       = Content('Sub Page 1')
        sub_page_1_1     = Content('Sub Page 1.1')
        sub_page_1_1_1   = Content('Sub Page 1.1.1')
        sub_page_1_1_1_1 = Content('Sub Page 1.1.1.1')
        sub_page_1_2     = Content('Sub Page 1.2')
        sub_page_2       = Content('Sub Page 2')
        self.assert_(self.db.add_resource(None, homepage))
        self.assert_(self.db.add_resource(homepage.get_id(),
                                          sub_page_1))
        self.assert_(self.db.add_resource(sub_page_1.get_id(),
                                          sub_page_1_1))
        self.assert_(self.db.add_resource(sub_page_1_1.get_id(),
                                          sub_page_1_1_1))
        self.assert_(self.db.add_resource(sub_page_1_1_1.get_id(),
                                          sub_page_1_1_1_1))
        self.assert_(self.db.add_resource(sub_page_1.get_id(),
                                          sub_page_1_2))
        self.assert_(self.db.add_resource(homepage.get_id(),
                                          sub_page_2))
        
        # Test child counter.
        page = self.db.get_resource(id = sub_page_1.get_id())
        self.assert_(page.get_n_children() == 2)
        page = self.db.get_resource(id = sub_page_1_1_1.get_id())
        self.assert_(page.get_n_children() == 1)
        page = self.db.get_resource(id = sub_page_1_1_1_1.get_id())
        self.assert_(page.get_n_children() == 0)

        # Set up groups.
        users  = Group('Users')
        guys   = Group('Guys')
        admins = Group('Admins')
        self.assert_(self.db.add_resource(None,  users))
        self.assert_(self.db.add_resource(users, guys))
        self.assert_(self.db.add_resource(None,  admins))
        
        # Set up users.
        user = User('Normal User')
        self.assert_(self.db.add_resource(guys,   user))
        anon = User('Anonymous User')
        self.assert_(self.db.add_resource(users,  anon))
        admin = User('Administrator')
        self.assert_(self.db.add_resource(admins, admin))
        
        # Set up ACLs.
        self.db.grant(admins, [view_user, edit_user, delete_user], users)
        self.db.grant(admins, [view, edit, delete], homepage)
        self.db.grant(users,  view,                 homepage)
        self.db.grant(user,   edit,                 sub_page_1)
        self.db.grant(guys,   delete,               homepage)
        self.db.grant(anon,   view,                 sub_page_1)
        self.db.deny(anon,    view,                 sub_page_1)

        # Get the time of the last change.
        last_change = self.db.get_last_permission_change(actor_id = user.get_id())
        self.assert_(last_change is not None and last_change > 0)
        #FIXME: Assert with MySQLdb > 1.2.2: and last_change < datetime.datetime.now())
        #print "Last change:", last_change

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

        # Get permissions of one specific resource.
        pageid = homepage.get_id()
        perms  = self.db.get_permission_list_from_id(guys.get_id(),
                                                     resource_id = pageid)
        #dump_acl_list(perms)
        self.assert_(len(perms) == 1)

        # Get permissions of one specific resource (no match).
        pageid = sub_page_1_1_1.get_id()
        perms  = self.db.get_permission_list_from_id(guys.get_id(),
                                                     resource_id = pageid)
        #dump_acl_list(perms)
        self.assert_(len(perms) == 0)

        # Get recursive permissions of one specific resource.
        pageid = sub_page_1_1_1.get_id()
        perms  = self.db.get_permission_list_from_id_with_inheritance(
                                            actor_id    = guys.get_id(),
                                            resource_id = pageid)
        self.assert_(len(perms) == 2)
        #dump_acl_list(perms)

        # Get recursive permissions of another specific resource.
        perms = self.db.get_permission_list_from_id_with_inheritance(actor_id = user.get_id())
        self.assert_(len(perms) == 3)
        #dump_acl_list(perms)

        # Get permissions of all resources.
        perms = self.db.get_permission_list_from_id_with_inheritance()
        self.assert_(len(perms) == 9)
        #dump_acl_list(perms)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
