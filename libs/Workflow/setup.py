from setuptools import setup, find_packages
setup(name             = 'Spiff Workflow',
      version          = '0.0.1',
      description      = 'A workflow framework based on www.workflowpatterns.com',
      long_description = \
"""
Spiff Workflow is a library implementing generic workflows in pure Python.
It was designed to provide a clean API, and is very easy to use.

You can find a list of supported workflow patterns in the `README file`_
included with the package.

.. _README file: http://spiff.googlecode.com/svn/trunk/libs/Workflow/README
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'lGPLv2',
      packages         = [''],
      requires         = [''],
      provides         = ['Workflow'],
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
