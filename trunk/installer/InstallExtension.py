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
import sys, cgi, os.path
import MySQLdb
sys.path.append('..')
import Guard
from sqlalchemy   import *
from ConfigParser import RawConfigParser
from Task         import Task
from ExtensionApi import ExtensionApi
from Session      import Session
from PageDB       import PageDB
from Integrator   import PackageManager

class InstallExtension(Task):
    def __init__(self, filename):
        assert filename is not None
        name = os.path.basename(filename)
        Task.__init__(self, 'Installing \'%s\' Extension' % name)
        self.__filename = filename


    def __setup(self):
        # Read config.
        cfg = RawConfigParser()
        cfg.read('../data/spiff.cfg')
        dbn = cfg.get('database', 'dbn')
        assert dbn is not None

        # Connect to MySQL and set up.
        db            = create_engine(dbn)
        self.guard    = Guard.DB(db)
        page_db       = PageDB(self.guard)
        session       = Session(self.guard, requested_page = None)
        get_data      = cgi.parse_qs(os.environ["QUERY_STRING"])
        post_data     = cgi.FieldStorage()
        extension_api = ExtensionApi(session   = session,
                                     guard     = self.guard,
                                     page_db   = page_db,
                                     get_data  = get_data,
                                     post_data = post_data)
        self.integrator = PackageManager(self.guard, extension_api)
        self.integrator.set_package_dir('../data/repo')


    def install(self, environment):
        self.__setup()
        extension_id = self.integrator.add_package(self.__filename)
        if extension_id <= 0:
            return Task.failure
        return Task.success


    def uninstall(self, environment):
        # Not implemented.
        return Task.success
