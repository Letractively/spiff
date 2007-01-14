import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import Python

# Parse a Python file.
reader = Python.Reader()
#reader.debug = 2
file   = reader.read('Python/testfile.py')
print "Original file:"
print "--------------"
print file.get_data()

# Get the extracted API documentation of one test method.
class1        = file.get_child('class', 'TestClass')
function1     = class1.get_child('function', '__init__')
documentation = function1.get_child('api_doc')

# Modify the documentation.
documentation.set_introduction("My Introduction")
documentation.set_description("My Description is decidedly a little\nlonger.")


# Modify the documentation of another test method.
class2        = file.get_child('class', 'SecondClass(TestClass)')
function1     = class2.get_child('function', 'do_something2')
documentation = function1.get_child('api_doc')
documentation.set_description("My Description")

# Print the entire file, including the changed documentation.
print "Changed file:"
print "-------------"
print file.get_data()
