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
from Step import Step

class CreateDefaultUser(Step):
    def show(self, **kwargs):
        self.render('CreateDefaultUser.tmpl',
                    username = 'Administrator',
                    errors   = kwargs.get('errors'))


    def check(self):
        password1 = self.request.post_data().get_str('password1', '').strip()
        password2 = self.request.post_data().get_str('password2', '').strip()
        if password1 == '':
            error = ('Checking password length', False, None)
            self.show(errors = [error])
            return False
        if password1 != password2:
            error = ('Checking whether passwords match', False, None)
            self.show(errors = [error])
            return False

        # Save the password.
        try:
            from sqlalchemy import create_engine
            from SpiffGuard import DB
            from objects    import User
            db    = create_engine(self.state.dbn)
            guard = DB(db)
            guard.register_type(User)
            user  = guard.get_resource(handle = 'admin', type = User)
            user.set_password(password1)
            guard.save_resource(user)
        except Exception, e:
            self.show(errors = [('Saving the password', False, str(e))])
            return False
        return True
