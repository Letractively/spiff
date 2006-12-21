import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import Python

# Parse a Python file.
reader = Python.Reader()
file   = reader.read('Python/testfile.py')

# Print the extracted API documentation of one test method.
my_class      = file.get_child('class', 'TestClass')
constructor   = my_class.get_child('function', '__init__')
documentation = constructor.get_child('api_doc', '')
print documentation.get_data()

# Modify the description of the API doc element.
documentation.set_description("My Description")
print documentation.get_data()
