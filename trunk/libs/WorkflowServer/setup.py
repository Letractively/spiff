from setuptools import setup, find_packages
setup(name             = 'Spiff WorkflowServer',
      version          = '0.0.1',
      description      = 'A library for managing workflows based on Spiff Workflow',
      long_description = \
"""
Spiff WorkflowServer is a library that wraps Spiff Workflow to provide
a simple API for storing and retrieving workflows.
It was designed to provide a clean API, and tries to be very easy to use.

.. _README file: http://spiff.googlecode.com/svn/trunk/libs/WorkflowServer/README
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'lGPLv2',
      packages         = [''],
      requires         = ['Workflow'],
      provides         = ['WorkflowServer'],
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
