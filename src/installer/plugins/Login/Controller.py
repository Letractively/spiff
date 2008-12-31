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
from services import ExtensionController
from urllib   import quote  # That's urllib from Python's stdlib

class Controller(ExtensionController):
    login_done,     \
    login_success,  \
    login_failure,  \
    login_open = range(4)

    def __init__(self, api, api_key):
        ExtensionController.__init__(self, api, api_key)
        self.__status = self.login_open


    def __perform_login(self):
        username = self.api.post_data().get_first('username')
        password = self.api.post_data().get_first('password')

        # A user is trying to log in.
        if self.api.post_data().get_bool('login') and username is not None:
            user = self.api.login(username, password)
            if user is None:
                self.__status = self.login_failure
                return
            self.__status = self.login_success
            return
        elif self.api.get_data().get_bool('logout'):
            self.api.logout()
            self.__status = self.login_open
            return

        # No user is currently logged in.
        current = self.api.get_current_user()
        if current is None:
            self.__status = self.login_open

        # A user is already logged in.
        else:
            self.__status = self.login_done


    def index(self, **kwargs):
        self.__perform_login()
        request_uri = self.api.get_requested_uri(login = None)

        if self.__status == self.login_done:
            user = self.api.get_current_user()
            assert user is not None
            return self.api.render('login_done.tmpl', user = user)

        elif self.__status == self.login_open:
            return self.api.render('login_form.tmpl',
                                   username = '',
                                   refer_to = quote(request_uri))

        elif self.__status == self.login_failure:
            return self.api.render('login_form.tmpl',
                                   username = '',
                                   refer_to = quote(request_uri),
                                   error    = 'Login failed.')
        elif self.__status == self.login_success:
            refer_to = self.api.get_data().get_first('refer_to')
            return self.api.render('login_success.tmpl', refer_to = refer_to)
