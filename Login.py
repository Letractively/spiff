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
from Guard  import ResourceSection
from Cookie import SimpleCookie

class Login:
    def __init__(self, guard_db):
        assert guard_db is not None
        self.__guard_db     = guard_db
        self.__current_user = None


    def __generate_session_id(self):
        import sha, time
        return sha.new(str(time.time())).hexdigest()


    def hash_password(self, password):
        import sha
        return sha.new(password).hexdigest()


    def get_current_user(self):
        if self.__current_user is not None:
            return self.__current_user
        try:
            sid = SimpleCookie(os.environ['HTTP_COOKIE'])['sid'].value
        except:
            sid = None
        guard = self.__guard_db
        if sid is None:
            return None
        users = guard.get_resource_list_from_attribute('sid', sid)
        if users is None:
            return None
        assert len(users) == 1
        self.__current_user = users[0]
        return self.__current_user


    def do(self, username, password):
        """
        Returns a dictionary that contains the headers that need to be added
        to the HTTP header on success. Returns None on otherwise.
        """
        #print "Login requested for user '%s'." % username
        if username is None or password is None:
            return None
        user = self.__guard_db.get_resource_from_handle(username, 'users')
        if user is None:
            return None
        if user.get_attribute('password') != self.hash_password(password):
            return None
        sid = self.__generate_session_id()
        #print "Logging in with sid %s..." % sid
        user.set_attribute('sid', sid)
        section = ResourceSection('users')
        self.__guard_db.save_resource(user, section)
        self.__current_user = user
        headers = {'Set-Cookie': 'sid=%s;' % sid}
        return headers
