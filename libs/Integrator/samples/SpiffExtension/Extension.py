class Extension:
    def __init__(self, api):
        api.emit('render_start')
        api.emit('render_end')

    def on_spiff_page_open(self, **args):
        pass

    def on_spiff_header_send_before(self, **args):
        pass
