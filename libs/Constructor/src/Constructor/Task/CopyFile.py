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
import os.path, shutil
from Task import Task

class CopyFile(Task):
    def __init__(self, source, destination):
        assert source      is not None
        assert destination is not None
        Task.__init__(self, 'Copying file \'%s\'' % source)
        self.__source      = source
        self.__destination = destination


    def install(self, environment):
        if os.path.exists(self.__destination):
            return Task.success
        shutil.copy(self.__source, self.__destination)
        return Task.success


    def uninstall(self, environment):
        return Task.success
