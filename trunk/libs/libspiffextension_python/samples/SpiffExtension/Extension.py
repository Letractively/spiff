"""
extension:    SpiffExtension
handle:       spiff
version:      1.1
author:       Samuel Abels
author-email: spam2@debain.org
description:  A simple extension serving as a dependency for the tests.
signal:       render_start
              render_end
"""

class Extension:
   def __init__(self, api):
      api.emit('render_start')
      api.emit('render_end')
