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
import os, cgi
from Request import Request

class CgiRequest(Request):
    def __init__(self):
        Request.__init__(self)
        from Cookie import SimpleCookie
        self.headers      = []
        self.headers_sent = False
        self.get_data     = cgi.parse_qs(self.get_env('QUERY_STRING'))
        self.post_data    = cgi.FieldStorage()


    def __unpack_get_value(self, value):
        if type(value) == type(''):
            return value
        elif type(value) == type([]):
            return value[0]
        assert False # No such type.


    def __unpack_get_data(self, input):
        output = {}
        for key in input:
            output[key] = self.__unpack_get_value(input[key])
        return output


    def __unpack_post_value(self, value):
        if type(value) == type(''):
            return value
        elif type(value) != type([]):
            return value.value
        return [self.__unpack_post_value(v) for v in value]


    def __unpack_post_data(self, input):
        output = {}
        for key in input:
            output[key] = self.__unpack_post_value(input[key])
        return output


    def get_env(self, key):
        return os.environ[key]


    def has_get_data(self, key, value = None):
        if value is None:
            return self.get_data.has_key(key)
        return self.get_data.get(key) == value


    def get_get_data(self, key = None, default = None):
        if key is None:
            return self.__unpack_get_data(self.get_data)
        return self.get_data.get(key, default)


    def has_post_data(self, key = None, value = None):
        if key is None:
            raise Exception(self.post_data)
            return len(self.post_data) > 0
        if value is None:
            self.post_data.has_key(key)
        return self.post_data.get(key) == value


    def get_post_data(self, key = None, default = None):
        if key is None:
            return self.__unpack_post_data(self.post_data)
        if not self.post_data.has_key(key):
            return default
        field = self.post_data[key]
        if type(field) != type([]):
            return [field.value]
        values = []
        for item in field:
            values.append(item.value)
        return values


    def set_cookie(self, key, value, expires = None):
        self.headers.append(('Set-Cookie', '%s=%s; path=/' % (key, value)))


    def get_cookie(self, key = None, default = None):
        return [SimpleCookie(os.environ['HTTP_COOKIE'])['sid'].value]


    def send_headers(self):
        self.headers_sent = True
        if self.status != 200:
            print "HTTP/1.1 %s unknown\r\n" % self.status
        print "Content-Type: %s\r\n" % self.content_type
        for key, value in self.headers:
            print "%s: %s\r\n" % (key, value)
        print


    def flush(self):
        if not self.headers_sent:
            self.send_headers()
        print self.data
        self.data = ''
