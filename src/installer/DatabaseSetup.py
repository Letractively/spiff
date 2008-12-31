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
import config, util
from sqlalchemy import create_engine
from Step       import Step

class DatabaseSetup(Step):
    def show(self, **kwargs):
        self.render('DatabaseSetup.tmpl',
                    db_host     = self.state.get('db_host'),
                    db_user     = self.state.get('db_user'),
                    db_password = self.state.get('db_password'),
                    db_name     = self.state.get('db_name'),
                    errors      = kwargs.get('errors'),
                    success     = not kwargs.get('errors'))


    def _get_dbn(self, **kwargs):
        return '%s://%s:%s@%s/%s' % (kwargs.get('db_type'),
                                     kwargs.get('db_user'),
                                     kwargs.get('db_password'),
                                     kwargs.get('db_host'),
                                     kwargs.get('db_name'))

    def check(self):
        state = self.state
        state.db_host     = self.request.post_data().get_str('db_host')
        state.db_user     = self.request.post_data().get_str('db_user')
        state.db_password = self.request.post_data().get_str('db_password')
        state.db_name     = self.request.post_data().get_str('db_name')
        state.dbn         = self._get_dbn(db_type = 'mysql', **state.__dict__)

        # Check the syntax.
        if self.state.db_host.strip() == '':
            self.show()
            return False
        if self.state.db_user.strip() == '':
            self.show()
            return False
        if self.state.db_password.strip() == '':
            self.show()
            return False
        if self.state.db_name.strip() == '':
            self.show()
            return False

        # Check the database.
        checks = [util.check_db_connection(state.dbn),
                  util.check_db_supports_constraints(state.dbn)]
        errors = [result for result in checks if not result[1]]
        if len(errors) > 0:
            self.show(errors = errors)
            return False

        # Success!
        return True
