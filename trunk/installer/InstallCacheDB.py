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
from Task    import Task
from Session import Session
from CacheDB import CacheDB

class InstallCacheDB(Task):
    def __init__(self):
        Task.__init__(self, 'Installing cache database')


    def install(self, environment):
        guard = environment.get_attribute('guard_db')
        assert guard is not None
        session = Session(guard, requested_page = object)
        cache   = CacheDB(guard, session)
        try:
            cache.install()
        except:
            return Task.failure
        return Task.success


    def uninstall(self, environment):
        guard = environment.get_attribute('guard_db')
        assert guard is not None
        session = Session(guard, requested_page = object)
        cache   = CacheDB(guard, session)
        try:
            cache.uninstall()
        except:
            pass
        return Task.success
