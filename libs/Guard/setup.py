from setuptools import setup, find_packages
setup(name             = 'Spiff Guard',
      version          = '1.9.0',
      description      = 'A Generic Access List Library',
      long_description = \
"""
Spiff Guard is a library implementing generic access lists for Python.
It was designed to provide a clean API, high security and high
scalability. Working with an ACL is as simple as this:

::

    from Guard import *
    guard   = DB(db_connection)
    group   = ResourceGroup("My Group")
    user    = Resource("My User")
    website = ResourceGroup("My Website")
    view    = Action("View")
    write   = Action("Edit")
    guard.add_action([view, write])
    guard.add_resource([user, group, website])
    guard.grant(group, view, website)
    guard.grant(user,  edit, website)
    if guard.has_permission(user, view, website):
        print 'Permission granted.'

Spiff Guard's features include recursion, groups, Python type awareness,
inverse lookup, and a lot more. For a more complete example, have a look
into the `README file`_ included with the package.

.. _README file: http://spiff.googlecode.com/svn/trunk/libs/Guard/README
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'GPLv2',
      packages         = [''],
      requires         = ['sqlalchemy'],
      provides         = ['Guard'],
      url              = 'http://code.google.com/p/spiff/',
      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
