# Copyright (C) 2008 Samuel Abels, http://debain.org
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
from Url import Url

class Request(object):
    def __init__(self):
        self.status       = 200;
        self.content_type = 'text/html; charset=utf-8'
        self.data         = ''


    def set_status(self, status):
        """
        Defines the HTTP status value (e.g. 404 for File not found).
        """
        self.status = status


    def set_content_type(self, type):
        self.content_type = type


    def write(self, data):
        """
        Write into the  output buffer. This is not actually sent until
        flush() is called.
        """
        self.data += data


    def flush(self):
        """
        Flush the output buffer, and send it to the client. Also,
        if HTTP headers were not already sent, send them first.
        """
        raise Exception('flush() not implemented...')


    def get_url(self, path = ''):
        return Url(self, path)


    def get_current_url(self, **kwargs):
        # Extract variables from the current URL.
        url = self.get_url()
        for key, value in self.get_get_data().iteritems():
            url.set_var(key, value)
        for key, value in kwargs.iteritems():
            url.set_var(key, value)
        return url


    def get_env(self, key):
        """
        Returns the value of the given key from the environment.
        """
        raise Exception('get_env() not implemented...')


    def has_get_data(self, key, value = None):
        """
        Returns True if the variable with the given name is set, False
        otherwise.
        """
        raise Exception('has_get_data() not implemented...')


    def get_get_data(self, key = None, default = None):
        """
        Always returns a list with values of the variable with the given name.
        """
        raise Exception('get_get_data() not implemented...')


    def has_post_data(self, key = None, value = None):
        """
        If a key is not given, this function returns True if ANY post data
        exists.
        If a key was given, this function returns True if the variable with
        the given name is set, False otherwise.
        """
        raise Exception('has_post_data() not implemented...')


    def get_post_data(self, key = None, default = None):
        """
        Always returns a list with values of the variable with the given name.
        """
        raise Exception('post_data() not implemented...')


    def set_cookie(self, key, value, expires = None):
        """
        Set a cookie with the given key/value and optionally with an
        expiration time (as returned by time.time()).
        """
        raise Exception('set_cookie() not implemented...')


    def get_cookie(self, key = None, default = None):
        """
        Always returns a list with values of the variable with the given name.
        """
        raise Exception('get_cookie() not implemented...')
