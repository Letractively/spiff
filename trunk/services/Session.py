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
from Cookie     import SimpleCookie
from User       import User
from PageAction import PageAction

class Session(object):
    def __init__(self, guard, **kwargs):
        assert kwargs.has_key('requested_page')
        assert guard is not None
        self.__guard          = guard
        self.__current_user   = None
        self.__requested_page = kwargs['requested_page']
        try:
            sid = SimpleCookie(os.environ['HTTP_COOKIE'])['sid'].value
        except:
            sid = None
        self.__sid = sid


    def __generate_session_id(self):
        import sha, time
        return sha.new(str(time.time())).hexdigest()


    def __get_action(self):
        return self.__guard.get_action(handle = 'view',
                                       type   = PageAction)


    def set_requested_page(self, page):
        self.__requested_page = page


    def get_requested_page(self):
        return self.__requested_page


    def get_user(self):
        if self.__current_user is not None:
            return self.__current_user
        if self.__sid is None:
            return None
        user = self.__guard.get_resource(attribute = {'sid': self.__sid},
                                         type      = User)
        if user is None:
            self.__sid = None
            return None
        self.__current_user = user
        return self.__current_user


    def may(self, action_handle, page = None):
        if page is None:
            page = self.__requested_page

        # If the page is publicly available there's no need to ask the DB.
        private = page.get_attribute('private') or False
        if action_handle == 'view' and not private:
            return True

        # Get the currently logged in user.
        user = self.get_user()
        if user is None:
            return False

        # Ask the DB whether permission shall be granted.
        action = self.__guard.get_action(type   = PageAction,
                                         handle = action_handle)
        if self.__guard.has_permission(user, action, page):
            return True
        return False 


    def login(self, username, password):
        """
        Returns a dictionary that contains the headers that need to be added
        to the HTTP header on success. Returns None on otherwise.
        """
        #print "Login requested for user '%s'." % username
        if username is None or password is None:
            return None
        user = self.__guard.get_resource(handle = username,
                                         type   = User)
        if user is None:
            return None
        if not user.has_password(password):
            return None
        if user.is_inactive():
            return None
        self.__sid = self.__generate_session_id()
        #print "Logging in with sid %s..." % self.__sid
        user.set_attribute('sid', self.__sid)
        self.__guard.save_resource(user)
        self.__current_user = user
        headers = {'Set-Cookie': 'sid=%s; path=/' % self.__sid}
        return headers


    def logout(self):
        self.__current_user = None
        self.__sid          = None
        return {'Set-Cookie': 'sid=''; expires=Thu, 01-JAN-1970 00:00:00 GMT;'}
