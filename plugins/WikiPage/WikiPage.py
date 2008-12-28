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
import SpiffWarehouse

class WikiPage(object):
    def __init__(self, parent, alias, **kwargs):
        self.parent = parent
        self.item   = kwargs.get('item')
        if self.item is None:
            self.item = SpiffWarehouse.Item(alias)


    def get_revision(self):
        return self.item.get_revision()


    def get_datetime(self):
        return self.item.get_datetime()


    def set_username(self, name):
        self.item.set_attribute(user_name = name)


    def get_username(self):
        return self.item.get_attribute('user_name') or 'System'


    def set_content(self, content):
        self.item.set_content(content)


    def get_content(self):
        return unicode(self.item.get_content(), 'utf-8')


    def get_html(self):
        self.parent.wiki2html.read(self.item.get_filename())
        return unicode(self.parent.wiki2html.html, 'utf-8')
