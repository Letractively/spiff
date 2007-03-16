from distutils.core import setup
setup(name             = 'Spiff WikiMarkup',
      version          = '0.1',
      description      = 'A library for converting between HTML and Wiki text',
      long_description = \
"""
Spiff WikiMarkup is a library that bidirectionally converts between HTML and
Wiki markup language.
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'GPLv2',
      packages         = [''],
      requires         = ['Plex'],
      provides         = ['WikiMarkup'],
      url              = 'http://code.google.com/p/spiff/',
      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
