"""
extension:    HelloWorldExtension
handle:       hello_world
version:      0.1
author:       Samuel Abels
author-email: spam2@debain.org
description:  A simple extension for the tests.
              It is also intended that the description
              is a multi line string to have that tested.
dependency:   spiff>=0.5
listener:     spiff:render_start
signal:       render_start
              render_end
"""

class Extension:
   def __init__(self, api):
      api.emit('render_start')
      api.append_content('Hello World!')
      api.emit('render_end')
