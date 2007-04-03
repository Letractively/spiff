class Extension:
   def __init__(self, api):
      api.emit('render_start')
      api.emit('render_end')
