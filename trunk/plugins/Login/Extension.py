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

class Extension:
    login_done,     \
    login_success,  \
    login_failure,  \
    login_open = range(4)

    def __init__(self, api):
        self.api            = api
        self.__current_user = None
        self.status         = self.login_open
        api.add_listener(self.on_page_open, 'spiff:page_open')


    def __generate_session_id(self):
        import sha, time
        return sha.new(str(time.time())).hexdigest()


    def __get_current_user(self):
        if self.__current_user is not None:
            return self.__current_user
        try:
            sid = SimpleCookie(os.environ['HTTP_COOKIE'])['sid'].value
        except:
            sid = None
        acldb = self.api.get_acldb()
        if sid:
            user = acldb.get_resource_from_attribute('sid', sid)
        else:
            user = acldb.get_resource_from_handle('anonymous', 'users')
        self.__current_user = user
        return user


    def __do_login(self, username, password):
        #print "Login requested for user '%s'." % username
        if username is None or password is None:
            return self.login_failure
        acldb = self.api.get_acldb()
        user  = acldb.get_resource_from_handle(username, 'users')
        if user is None:
            return self.login_failure
        sid = self.__generate_session_id()
        #print "Logging in with sid %s..." % sid
        user.set_attribute('sid', sid)
        headers['Set-Cookie'] = 'sid=%s;' % sid
        acldb.save_resource(user)
        return self.login_success


    def on_page_open(self, args):
        # A user is trying to log in.
        if self.api.get_form_value('login') is not None:
            user        = self.api.get_form_value('username')
            password    = self.api.get_form_value('password')
            self.status = self.__do_login(user, password)
            return

        # No user is currently logged in.
        current = self.api.get_current_user()
        assert current is not None
        if current.get_handle() == 'anonymous':
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
            return self.api.render('login_done.tmpl') #FIXME

        elif self.status == self.login_open:
            return self.api.render('login_form.tmpl') #FIXME

        elif self.status == self.login_failure:
            return self.api.render('login_form.tmpl',
                                   error = 'Login failed.') #FIXME
        self.api.emit('render_end')
