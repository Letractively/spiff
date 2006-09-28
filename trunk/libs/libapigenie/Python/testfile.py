import sys
sys.exit()
# Testfile for the Python parser.
import me
import me.maybe.someday
from me import something
from some_module import *

# A comment.

class TestClass:
    """
    This is a simple test class, it is only read by the Python parser to
    make sure that this documentation can be read correctly.

    I, for one, like multi line comments.
    So I use them.
    """
    def __init__(self, blah):
        """
        Test of a constructor API description. This Description might span
        over multiple lines.

        It also might not. Or it might use @variable names.

        @type  blah: SomeObject
        @param blah: Whatever it may be.
        @type  blah2: AnotherObject
        @param blah2: An object with a description that is a little longer
                      than just one line.
        @rtype:  Boolean
        @return: True if the action existed, False otherwise.
        """
        return False

class SecondClass(TestClass):
    def do_something1(self,
                      var_a,
                      var_b,
                      var_c):
        """
        Comment 1, simple, single line.
        """
        return False
        
    def do_something2(self, var_a, var_b, var_c):
        """
        Comment 2, simple, multi line without any further information
        regarding the argument types.
        """
        pass

    def do_something3(self, var_a, var_b, var_c):
        """
        @type  blah: SomeObject
        @param blah: Whatever it may be.
        """
        return beer

    def do_something3(self, var_a, var_b, var_c):
        """
        @param blah: Whatever it may be, in some nice multiple lines of
                     useful, or not useful, information.
        """
        return beer

    def do_something4(self, var_a):
        """
        @type  blah: SomeObject
        @param blah: Whatever it may be.
        @rtype:  Boolean
        @return: True if the action existed, False otherwise. TrueFalse
                 if the developer was braindead.
        """
        return beer
