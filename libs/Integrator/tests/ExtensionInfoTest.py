import sys, unittest, re
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

def suite():
    tests = ['testExtensionInfo']
    return unittest.TestSuite(map(ExtensionInfoTest, tests))

from ExtensionInfo import ExtensionInfo

class ExtensionInfoTest(unittest.TestCase):
    def testExtensionInfo(self):
        name      = 'Test Extension'
        handle    = 'Test Handle'
        version   = '0.1.2'
        author    = 'Test Author'
        descr     = 'let me test this'
        filename  = '/my/filename.tgz'
        context   = 'Test Context'
        extension = ExtensionInfo(name, handle, version)
        assert extension.get_name()    == name
        assert extension.get_handle()  == handle
        assert extension.get_version() == version

        extension = ExtensionInfo(name)
        assert extension.get_name()    == name
        assert extension.get_handle()  == 'test_extension'
        assert extension.get_version() == '0'

        extension.set_version(version)
        extension.set_author(author)
        extension.set_description(descr)
        extension.set_filename(filename)
        assert extension.get_version()     == version
        assert extension.get_author()      == author
        assert extension.get_description() == descr
        assert extension.get_filename()    == filename

        # Test empty context list.
        context_list = extension.get_dependency_context_list()
        assert len(context_list) == 0

        # Test non-empty context list.
        descriptor = 'spiff>=1.0'
        extension.add_dependency(descriptor)
        context_list = extension.get_dependency_context_list()
        assert context_list[0] == 'default'
        assert len(context_list) == 1

        # Test dependency list.
        dep_list = extension.get_dependency_list('default')
        assert dep_list[0] == descriptor
        assert len(dep_list) == 1

        # Test non-default context.
        context     = 'runtime'
        descriptor1 = 'mydep=0.1.2'
        descriptor2 = 'mydep2>=2'
        extension.add_dependency(descriptor1, context)
        extension.add_dependency(descriptor2, context)
        context_list = extension.get_dependency_context_list()
        assert context_list[0] == 'default'
        assert context_list[1] == context
        assert len(context_list) == 2

        dep_list = extension.get_dependency_list('default')
        assert dep_list[0] == descriptor
        assert len(dep_list) == 1
        dep_list = extension.get_dependency_list(context)
        assert dep_list[0] == descriptor1
        assert dep_list[1] == descriptor2
        assert len(dep_list) == 2

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
