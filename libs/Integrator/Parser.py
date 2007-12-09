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
import os, sys, re
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from genshi.input import XML
from Package      import Package

whitespace = re.compile(r'\s+')

class Parser(object):
    def __init__(self):
        pass


    def parse_file(self, filename):
        infile = open(filename, 'r')
        xml    = infile.read()
        infile.close()
        return self.parse_string(xml)


    def parse_string(self, xml):
        assert xml is not None
        xml = XML(xml)

        # Fetch general info and instantiate a new Package.
        handle  = str(xml.select('package/attribute::handle')).strip()
        name    = str(xml.select('package/name/').select('text()')).strip()
        release = str(xml.select('package/release/text()')).strip()
        descr   = str(xml.select('package/description[@lang=""]/text()'))
        package = Package(name, handle, release)
        package.set_description(whitespace.sub(' ', descr.strip()))

        # Author information.
        author = str(xml.select('package/authors/person/name/text()'))
        email  = str(xml.select('package/authors/person/email/text()'))
        package.set_author(author.strip())
        package.set_author_email(email.strip())

        # Behavioral flags.
        if str(xml.select('package/behavior/cacheable')) != '':
            package.set_attribute('cacheable', True)
        if str(xml.select('package/behavior/recursive')) != '':
            package.set_attribute('recursive', True)

        # Signals sent by this package.
        list = xml.select('package/behavior/signal/attribute::uri')
        for item in list:
            package.add_signal(item.strip())

        # Signals retrieved by this package.
        list = xml.select('package/behavior/listen/attribute::uri')
        for item in list:
            package.add_listener(item.strip())

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

        return package
