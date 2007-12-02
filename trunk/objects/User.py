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
import sha
from Guard import ResourceGroup

class User(ResourceGroup):
    def _hash_password(self, password):
        return sha.new(password).hexdigest()


    def set_password(self, password):
        self.set_attribute('password', self._hash_password(password))


    def has_password(self, password):
        return self.get_attribute('password') == self._hash_password(password)


    def set_inactive(self, status = True):
        if status == True:
            self.set_attribute('inactive', True)
        else:
            self.remove_attribute('inactive')


    def is_inactive(self):
        return self.get_attribute('inactive') == True


    def set_activation_key(self, key):
        if key is None:
            self.remove_attribute('activation_key')
        self.set_attribute('activation_key', key)
