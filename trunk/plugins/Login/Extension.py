"""
extension:    Login
handle:       spiff_core_login
version:      0.1
author:       Samuel Abels
author-email: spam2@debain.org
description:  This core extension implements the login form that lets
              users log into Spiff.
dependency:   spiff
listener:     spiff:page_open
signal:       login_done
              logout_done
              render_start
              render_end
"""
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
        api.add_listener(self.on_page_open, 'spiff:page_open')


    def on_page_open(self, args):
        # A user is trying to log in.
        if self.__api.get_post_data('login') is not None:
            user     = self.__api.get_post_data('username')
            password = self.__api.get_post_data('password')
            headers  = self.__login.do(user, password)
            if headers is not None:
                self.__api.send_headers('text/html', headers)
                self.__status = self.login_success
                self.__api.emit('login_done')
            return
        elif self.__api.get_post_data('logout') is not None:
            headers = self.__login.logout()
            assert headers is not None
            self.__api.send_headers('text/html', headers)
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
        self.__api.send_headers()

        if self.__status == self.login_done:
            user = self.__login.get_current_user()
            assert user is not None
            return self.__api.render('login_done.tmpl', user = user)

        elif self.__status == self.login_open:
            return self.__api.render('login_form.tmpl') #FIXME

        elif self.__status == self.login_failure:
            return self.__api.render('login_form.tmpl',
                                     error = 'Login failed.') #FIXME
        self.__api.emit('render_end')
