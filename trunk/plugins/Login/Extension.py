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
from urllib import quote

class Extension:
    login_done,     \
    login_success,  \
    login_failure,  \
    login_open = range(4)

    def __init__(self, api):
        self.__api     = api
        self.__session = api.get_session()
        self.__status  = self.login_open


    def __perform_login(self):
        user     = self.__api.get_post_data('username')
        password = self.__api.get_post_data('password')

        # A user is trying to log in.
        if self.__api.get_post_data('login') is not None and user is not None:
            headers = self.__session.login(user, password)
            if headers is None:
                self.__status = self.login_failure
                return
            self.__api.append_http_headers(**headers)
            self.__status = self.login_success
            return
        elif self.__api.get_get_data('logout') is not None:
            headers = self.__session.logout()
            assert headers is not None
            self.__api.append_http_headers(**headers)
            self.__status = self.login_open
            return

        # No user is currently logged in.
        current = self.__session.get_user()
        if current is None:
            self.__status = self.login_open

        # A user is already logged in.
        else:
            self.__status = self.login_done


    def on_render_request(self):
        self.__perform_login()
        request_uri = self.__api.get_requested_uri(login = None)

        if self.__status == self.login_done:
            user = self.__session.get_user()
            assert user is not None
            return self.__api.render('login_done.tmpl', user = user)

        elif self.__status == self.login_open:
            return self.__api.render('login_form.tmpl',
                                     refer_to = quote(request_uri))

        elif self.__status == self.login_failure:
            return self.__api.render('login_form.tmpl',
                                     refer_to = quote(request_uri),
                                     error    = 'Login failed.')
        elif self.__status == self.login_success:
            refer_to = self.__api.get_get_data('refer_to')
            return self.__api.render('login_success.tmpl',
                                     refer_to = refer_to)
