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
import MySQLdb, Integrator
import sys, cgi, os.path
sys.path.append('..')
from sqlalchemy   import *
from ConfigParser import RawConfigParser
from Task         import Task
from Form         import Form
from StockButton  import StockButton
from Guard        import ResourceSection
from ExtensionApi import ExtensionApi
from Login        import Login
import Guard

class SetUserPassword(Task):
    def __init__(self, handle):
        assert handle is not None
        Task.__init__(self, 'Setting password for \'%s\' user' % handle)
        self.__handle = handle


    def __setup(self):
        # Read config.
        cfg = RawConfigParser()
        cfg.read('../data/spiff.cfg')
        dbn = cfg.get('database', 'dbn')
        assert dbn is not None

        # Connect to MySQL and set up.
        db              = create_engine(dbn)
        self.guard      = Guard.DB(db)
        get_data        = cgi.parse_qs(os.environ["QUERY_STRING"])
        post_data       = cgi.FieldStorage()
        self.integrator = Integrator.Manager(self.guard,
                                             ExtensionApi,
                                             requested_page = None,
                                             guard_mod      = Guard,
                                             get_data       = get_data,
                                             post_data      = post_data)
        self.integrator.set_extension_dir('../data/repo')


    #FIXME: This should be elsewhere.
    def __hash_password(self, password):
        import sha, time
        return sha.new(password).hexdigest()


    def __show_form(self, environment, username, error = ''):
        '''
        Generates a form for entering the password.
        '''
        markup = error
        markup += '{title "Please choose a default password."}'
        markup += '{label "User:"} {label "%s"}\n' % username
        markup += '{label "Password:"}          {pass_entry password1}\n'
        markup += '{label "Password (repeat):"} {pass_entry password2}\n'
        form = Form(markup, [StockButton('next_button')])
        environment.render_markup(form)


    def install(self, environment):
        self.__setup()
        user = self.guard.get_resource_from_handle(self.__handle, 'users')
        assert user is not None

        result = environment.get_interaction_result()
        if not result:
            self.__show_form(environment, user.get_name())
            return Task.interact

        elif result.get('password1') != result.get('password2'):
            error = 'The passwords did not match!'
            self.__show_form(environment, user.get_name(), error)
            return Task.interact

        elif len(result.get('password1')) < 5:
            error = 'The password is too short! (5 characters minimum)'
            self.__show_form(environment, user.get_name(), error)
            return Task.interact

        password = result.get('password1')
        user.set_attribute('password', self.__hash_password(password))
        section = ResourceSection('users')
        self.guard.save_resource(user, section)
        return Task.success


    def uninstall(self, environment):
        # Not implemented.
        return Task.success

