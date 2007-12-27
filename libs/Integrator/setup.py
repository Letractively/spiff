from setuptools import setup, find_packages
setup(name             = 'Spiff Integrator',
      version          = '0.1',
      description      = 'A package/plugin manager implemented in Python',
      long_description = \
"""
Spiff Integrator is a small but powerful package manager that was written
for adding plugin support into applications. It handles packing/unpacking,
installation/updates/removal, and dependency management and provides a bus
over which plugins may communicate.
It was designed to provide a clean API, high security and high scalability.

For documentation please refer to the `README file`_ or the tests included
with the package. You may also look at the `API documentation`_.

.. _README file: http://spiff.googlecode.com/svn/trunk/libs/Guard/README
.. _API documentation: http://spiff.debain.org/static/docs/spiff_integrator/index.html
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'GPLv2',
      packages         = [''],
      requires         = ['sqlalchemy'],
      provides         = ['Integrator'],
      url              = 'http://code.google.com/p/spiff/',
      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
