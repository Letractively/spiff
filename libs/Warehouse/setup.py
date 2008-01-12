from setuptools import setup, find_packages
setup(name             = 'Spiff Warehouse',
      version          = '0.1',
      description      = 'A library for storing revisioned files in a database',
      long_description = \
"""
Spiff Warehouse is a library that stores revisioned files in a database
and provides an API for getting a diff between documents (if the
document format is supported).
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'GPLv2',
      package_dir      = {'': 'src'},
      packages         = ['Warehouse'],
      #provides         = ['Warehouse'],
      keywords         = 'spiff warehouse object storage revisioning',
      url              = 'http://code.google.com/p/spiff/',
      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
