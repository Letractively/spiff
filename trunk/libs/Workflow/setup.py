from setuptools import setup, find_packages
print ['Spiff.' + p for p in find_packages('src', exclude=['ez_setup'])]
setup(name             = 'Spiff Workflow',
      version          = '0.1.0',
      description      = 'A workflow framework based on www.workflowpatterns.com',
      long_description = \
"""
Spiff Workflow is a library implementing workflows in pure Python.
It was designed to provide a clean API, and tries to be very easy to use.

You can find a list of supported workflow patterns in the `README file`_
included with the package.

WARNING! Use in a production environment is NOT RECOMMENDED at this time -
this release is meant for development only. Don't blame us if something breaks
because of this software!

.. _README file: http://spiff.googlecode.com/svn/trunk/libs/Workflow/README
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'lGPLv2',
      packages         = ['Spiff.' + p for p in find_packages('src')],
      package_dir      = {'Spiff': 'src'},
      data_files       = [('Spiff', ['src/__init__.py'])],
      requires         = ['Guard'],
      keywords         = 'spiff guard acl acls security authentication object storage',
      url              = 'http://code.google.com/p/spiff/',
      classifiers      = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
