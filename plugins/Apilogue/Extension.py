# Copyright (C) 2006 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
from ApiGenie import ApiDB

class Extension:
    def __init__(self, api):
        self.api    = api
        self.db     = api.get_db()
        self.i18n   = api.get_i18n()
        self.api_db = ApiDB(self.db)


    def install(self):
        return self.api_db.install()


    def __show(self, errors = []):
        page = self.api.get_requested_page()
        assert page is not None

        self.api.render('home.tmpl',
                        name       = page.get_name(),
                        errors     = errors)


    def on_render_request(self):
        self.api.emit('render_start')

        self.__show()

        self.api.emit('render_end')
