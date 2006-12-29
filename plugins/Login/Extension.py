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
signal:       render_start
              render_end
"""
import os
from Cookie import SimpleCookie

class Extension:
    login_done,     \
    login_success,  \
    login_failure,  \
    login_open = range(4)

    def __init__(self, api):
        self.api    = api
        self.status = self.login_open


    def __get_current_user(self):
        sid  = SimpleCookie(os.environ['HTTP_COOKIE'])['sid'].value
        user = self.api.acldb.get_resource_from_attribute('sid', sid)
        return user


    def __generate_session_id(self):
        import sha, time
        return sha.new(str(time.time())).hexdigest()


    def __do_login(self, user, password):
        if user is None or password is None:
            return self.login_failure
        user = self.api.acldb.get_resource_from_name(user, 'users')
        if user is None:
            return self.login_failure
        user.set_attribute('sid', sid)
        headers['Set-Cookie'] = 'sid=%s;' % sid
        self.api.acldb.save_resource(user)
        return self.login_success


    def on_page_open(self):
        # A user is trying to log in.
        if cgi.get('login') is not None:
           user        = cgi.get('username')
           password    = cgi.get('password')
           self.status = self.__do_login(user, password)
           return

        # No user is currently logged in.
        current = self.__get_current_user()
        if current is None or current.get_handle() == 'anonyomous':
            self.status = self.login_open

        # A user is already logged in.
        else:
            self.status = self.login_done


    def on_render_request(self):
        self.api.emit('render_start')

        if self.status == self.login_success:
            # Render the same page that is currently opened.
            self.api.rerender() #FIXME

        elif self.status == self.login_done:
            return self.api.genshi.render('login_done.tmpl') #FIXME

        elif self.status == self.login_open:
            return self.api.genshi.render('login_form.tmpl') #FIXME

        elif self.status == self.login_failure:
            return self.api.genshi.render('login_form.tmpl',
                                          error = 'Login failed.') #FIXME
        self.api.emit('render_end')
