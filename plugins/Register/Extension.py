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
import os, re, sha, smtplib, random
from urlutil import get_request_uri
from User    import User

class Extension:
    def __init__(self, api):
        self.__api      = api
        self.i18n       = api.get_i18n()
        self.__session  = api.get_session()
        self.__guard    = api.get_guard()
        self.server     = 'mail.speedpartner.de'
        self.mail_from  = 'no-reply@debain.org'


    def register(self):
        handle    = self.__api.get_post_data('handle')    or ''
        firstname = self.__api.get_post_data('firstname') or ''
        lastname  = self.__api.get_post_data('lastname')  or ''
        email     = self.__api.get_post_data('email')     or ''
        password1 = self.__api.get_post_data('password1') or ''
        password2 = self.__api.get_post_data('password2') or ''

        # Perform some checks on the input values.
        error = None
        i18n  = self.i18n
        if handle == "":
            error = i18n("Invalid login name!")
        elif firstname == "":
            error = i18n("Invalid first name!")
        elif lastname == "":
            error = i18n("Invalid last name!")
        elif not re.match(r'\w+\@\w+\.\w+', email):
            error = i18n("Invalid email address!")
        elif password1 == "":
            error = i18n("Please enter a password!")
        elif password1 != password2:
            error = i18n("Passwords do not match!")
        else:
            # Check whether the username is already taken.
            res = self.__guard.get_resource(handle = handle,
                                            type   = User)
            if res is not None and res.is_group():
                error = i18n("A group with the given name already exists.")
            elif res is not None:
                error = i18n("A user with the given name already exists.")

        # Bail out if an error was found.
        if error is not None:
            self.__api.render('register.tmpl',
                              handle    = handle,
                              firstname = firstname,
                              lastname  = lastname,
                              email     = email,
                              password1 = password1,
                              password2 = password2,
                              error     = error)
            return False

        # Create the user with status "inactive".
        rand     = random.randint(0, 123456789) # no need to be strong
        string   = handle + password1 + firstname + lastname + str(rand)
        key      = sha.new(string).hexdigest()
        name     = firstname + ' ' + lastname
        users    = self.__guard.get_resource(handle = 'users', type = Group)
        user = User(name, handle)
        user.set_password(password1)
        user.set_inactive()
        user.set_activation_key(key)
        self.__guard.add_resource(users, user)

        # Format activation email.
        #FIXME: Make configurable.
        domain    = 'http://' + os.environ['HTTP_HOST']
        vars      = get_request_uri(confirm = [1], key = [key])
        url       = domain + vars
        filename  = os.path.join(os.path.dirname(__file__), 'confirmation.txt')
        file      = open(filename)
        mail_text = file.read().replace('$url', url).replace('$email', email)
        file.close()

        # Send email.
        server = smtplib.SMTP(self.server)
        #server.set_debuglevel(1)
        server.sendmail(self.mail_from, email, mail_text)
        server.quit()

        self.__api.render('mail_sent.tmpl', email = email)

        return True


    def confirm(self):
        # Find the user from the key.
        key     = self.__api.get_get_data('key')
        attribs = {'activation_key': key}
        user    = self.__guard.get_resource(attribute = attribs)
        if user is None:
            self.__api.render('register.tmpl', error = 'Invalid key')
            return

        # Activate the account.
        user.set_inactive(False)
        user.set_activation_key(None)
        self.__guard.save_resource(user)

        self.__api.render('complete.tmpl', user = user)


    def on_render_request(self):
        self.__api.emit('render_start')

        # If the user is already logged in do nothing.
        user = self.__session.get_user()
        if user is not None:
            self.__api.render('complete.tmpl', user = user)
            self.__api.emit('render_end')
            return

        # If the link in the confirmation email was clicked, try
        # to activate the account.
        confirm = self.__api.get_get_data('confirm')
        if confirm:
            self.confirm()
            self.__api.emit('render_end')
            return

        # If the registration form was submitted, attempt to create
        # the account.
        register = self.__api.get_post_data('register')
        if register:
            self.register()
            self.__api.emit('render_end')
            return

        # Else just show the registration form.
        self.__api.render('register.tmpl')
        self.__api.emit('render_end')
