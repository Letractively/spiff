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
import os

class Extension:
    login_done,     \
    login_success,  \
    login_failure,  \
    login_open = range(4)

    def __init__(self, api):
        self.__api    = api
        self.__login  = api.get_login()
        self.__status = self.login_open


    def on_spiff_page_open(self, args):
        # A user is trying to log in.
        if self.__api.get_post_data('login') is not None:
            user     = self.__api.get_post_data('username')
            password = self.__api.get_post_data('password')
            headers  = self.__login.do(user, password)
            if headers is not None:
                self.__api.append_http_headers(**headers)
                self.__status = self.login_success
                self.__api.emit('login_done')
            return
        elif self.__api.get_get_data('logout') is not None:
            headers = self.__login.logout()
            assert headers is not None
            self.__api.append_http_headers(**headers)
            self.__status = self.login_open
            self.__api.emit('logout_done')
            return

        # No user is currently logged in.
        current = self.__login.get_current_user()
        if current is None:
            self.__status = self.login_open

        # A user is already logged in.
        else:
            self.__status = self.login_done


    def on_render_request(self):
        self.__api.emit('render_start')

        if self.__status == self.login_done:
            user = self.__login.get_current_user()
            assert user is not None
            return self.__api.render('login_done.tmpl', user = user)

        elif self.__status == self.login_open:
            return self.__api.render('login_form.tmpl')

        elif self.__status == self.login_failure:
            return self.__api.render('login_form.tmpl',
                                     error = 'Login failed.')
        self.__api.emit('render_end')
