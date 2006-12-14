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
import re

class Callback:
    def  __init__(self, func, event_uri = None):
        """
        @type  func: function
        @param func: The function to be called when the event is sent.
        @type  event_uri: string
        @param event_uri: The URI of the signal. Might be a regular expression.
        """
        assert func is not None
        self.__func      = func
        self.__event_uri = event_uri
        self.__event_re  = None
        if event_uri is not None:
            self.__event_re  = re.compile(event_uri)

    def get_function(self):
        return self.__func

    def get_event_uri(self):
        return self.__event_uri

    def matches_uri(self, uri):
        assert uri is not None
        if self.__event_re is None:
            return True
        return self.__event_re.match(uri)


if __name__ == '__main__':
    import unittest

    class CallbackTest(unittest.TestCase):
        def callback_function(self):
            pass
            
        def runTest(self):
            event_uri = 'test:/my/uri/should/work/'
            callback = Callback(self.callback_function)
            assert callback.get_function()  == self.callback_function
            assert callback.get_event_uri() == None
            assert callback.matches_uri(event_uri)
            assert callback.matches_uri('asdasd')
            
            callback = Callback(self.callback_function, event_uri)
            assert callback.get_function()  == self.callback_function
            assert callback.get_event_uri() == event_uri
            assert callback.matches_uri(event_uri)
            assert not callback.matches_uri('asdasd')

    testcase = CallbackTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
