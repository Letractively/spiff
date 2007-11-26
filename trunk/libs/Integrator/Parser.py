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
from genshi.input import XML
from Package      import Package


class Parser:
    def __init__(self):
        self.package      = None
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

        # Fetch general info and instantiate a new Package.
        handle  = str(xml.select('package/attribute::handle')).strip()
        name    = str(xml.select('package/name/').select('text()')).strip()
        release = str(xml.select('package/release/text()')).strip()
        descr   = str(xml.select('package/description[@lang=""]/text()'))
        package    = Package(name, handle, release)
        package.set_description(descr.strip())

        # Author information.
        author = str(xml.select('package/authors/person/name/text()'))
        email  = str(xml.select('package/authors/person/email/text()'))
        package.set_attribute('author',       author.strip())
        package.set_attribute('author-email', email.strip())

        # Signals sent by this package.
        list = xml.select('package/behavior/signal/attribute::uri')
        self.signals = [item.strip() for item in list]

        # Signals retrieved by this package.
        list      = xml.select('package/behavior/listen/attribute::uri')
        self.listeners = [item.strip() for item in list]

        # Runtime dependencies.
        list = xml.select('package/depends/runtime/text()')
        for kind, data, pos in list:
            package.add_dependency(data.strip(), 'runtime')

        # Installtime dependencies.
        list = xml.select('package/depends/installtime/text()')
        for kind, data, pos in list:
            package.add_dependency(data.strip(), 'installtime')

        # Attributes.
        prefix = 'package/attributes/attribute'
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
            package.set_attribute(name, value)

        self.package = package
