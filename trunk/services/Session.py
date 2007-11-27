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
from Cookie import SimpleCookie
from User   import User

class Session(object):
    def __init__(self, guard_db):
        assert guard_db is not None
        self.__guard_db     = guard_db
        self.__current_user = None
        try:
            sid = SimpleCookie(os.environ['HTTP_COOKIE'])['sid'].value
        except:
            sid = None
        self.__sid = sid


    def __generate_session_id(self):
        import sha, time
        return sha.new(str(time.time())).hexdigest()


    def get_user(self):
        if self.__current_user is not None:
            return self.__current_user
        guard = self.__guard_db
        if self.__sid is None:
            return None
        user = guard.get_resource(attribute = {'sid': self.__sid},
                                  type      = User)
        if user is None:
            return None
        self.__current_user = user
        return self.__current_user


    def login(self, username, password):
        """
        Returns a dictionary that contains the headers that need to be added
        to the HTTP header on success. Returns None on otherwise.
        """
        #print "Login requested for user '%s'." % username
        if username is None or password is None:
            return None
        user = self.__guard_db.get_resource(handle = username,
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
        self.__guard_db.save_resource(user)
        self.__current_user = user
        headers = {'Set-Cookie': 'sid=%s; path=/' % self.__sid}
        return headers


    def logout(self):
        self.__current_user = None
        self.__sid          = None
        return {'Set-Cookie': 'sid=''; expires=Thu, 01-JAN-1970 00:00:00 GMT;'}
