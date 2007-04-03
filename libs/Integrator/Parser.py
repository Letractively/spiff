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
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from genshi.input  import XML
from ExtensionInfo import ExtensionInfo


class Parser:
    def __init__(self):
        self.info      = None
        self.signals   = []
        self.listeners = []


    def parse_file(self, filename):
        infile = open(filename, 'r')
        xml    = infile.read()
        infile.close()
        self.parse_string(xml)


    def parse_string(self, xml):
        assert xml is not None
        xml = XML(xml)

        # Fetch general info instantiate a new ExtensionInfo.
        handle  = str(xml.select('extension/attribute::handle')).strip()
        name    = str(xml.select('extension/name/').select('text()')).strip()
        release = str(xml.select('extension/release/text()')).strip()
        descr   = str(xml.select('extension/description[@lang=""]/text()'))
        info    = ExtensionInfo(name, handle, release)
        info.set_description(descr.strip())

        # Author information.
        author = str(xml.select('extension/authors/person/name/text()'))
        email  = str(xml.select('extension/authors/person/email/text()'))
        info.set_attribute('author',       author.strip())
        info.set_attribute('author-email', email.strip())

        # Signals sent by this extension.
        list = xml.select('extension/behavior/signal/attribute::uri')
        self.signals = [item.strip() for item in list]

        # Signals retrieved by this extension.
        list      = xml.select('extension/behavior/listen/attribute::uri')
        self.listeners = [item.strip() for item in list]

        # Runtime dependencies.
        list = xml.select('extension/depends/runtime/text()')
        for kind, data, pos in list:
            info.add_dependency(data.strip(), 'runtime')

        # Installtime dependencies.
        list = xml.select('extension/depends/installtime/text()')
        for kind, data, pos in list:
            info.add_dependency(data.strip(), 'installtime')

        # Attributes.
        prefix = 'extension/attributes/attribute'
        list   = xml.select(prefix + '/attribute::name')
        for name in list:
            type  = xml.select(prefix + '[@name="%s"]/attribute::type' % name)
            value = xml.select(prefix + '[@name="%s"]/text()' % name)
            type  = str(type)
            value = str(value)
            if type == 'boolean':
                value = value == 'True' and True or False
            elif type == 'integer':
                value = int(value)
            elif type == 'string':
                pass
            else:
                assert False # Unknown attribute type.
            info.set_attribute(name, value)

        self.info = info


if __name__ == '__main__':
    import unittest

    class ParserTest(unittest.TestCase):
        def runTest(self):
            filename = 'samples/SpiffExtension/Extension.xml'
            parser   = Parser()
            parser.parse_file(filename)
            assert parser.info.get_name() == 'My Spiff Extension'

    testcase = ParserTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
