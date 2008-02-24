import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Integrator'))

def suite():
    tests = ['testPackage']
    return unittest.TestSuite(map(PackageTest, tests))

from Package import Package

class PackageTest(unittest.TestCase):
    def testPackage(self):
        name     = 'Test Package'
        handle   = 'Test Handle'
        version  = '0.1.2'
        author   = 'Test Author'
        descr    = 'let me test this'
        filename = '/my/filename.tgz'
        context  = 'Test Context'
        package  = Package(name, handle, version)
        assert package.get_name()    == name
        assert package.get_handle()  == handle
        assert package.get_version() == version

        package = Package(name)
        assert package.get_name()    == name
        assert package.get_handle()  == 'test_package'
        assert package.get_version() == '0'

        package.set_version(version)
        package.set_author(author)
        package.set_description(descr)
        assert package.get_version()     == version
        assert package.get_author()      == author
        assert package.get_description() == descr

        # Test empty context list.
        context_list = package.get_dependency_context_list()
        assert len(context_list) == 0

        # Test non-empty context list.
        descriptor = 'spiff>=1.0'
        package._add_dependency(descriptor)
        context_list = package.get_dependency_context_list()
        assert context_list[0] == 'default'
        assert len(context_list) == 1

        # Test dependency list.
        dep_list = package.get_dependency_list('default')
        assert dep_list[0] == descriptor
        assert len(dep_list) == 1

        # Test non-default context.
        context     = 'runtime'
        descriptor1 = 'mydep=0.1.2'
        descriptor2 = 'mydep2>=2'
        package._add_dependency(descriptor1, context)
        package._add_dependency(descriptor2, context)
        context_list = package.get_dependency_context_list()
        assert context_list[0] == 'default'
        assert context_list[1] == context
        assert len(context_list) == 2

        dep_list = package.get_dependency_list('default')
        assert dep_list[0] == descriptor
        assert len(dep_list) == 1
        dep_list = package.get_dependency_list(context)
        assert dep_list[0] == descriptor1
        assert dep_list[1] == descriptor2
        assert len(dep_list) == 2

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())