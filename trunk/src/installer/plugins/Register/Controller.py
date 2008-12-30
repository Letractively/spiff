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
import gettext
_ = gettext.gettext
import os, re, sha, smtplib, random
from services import ExtensionController
from objects  import User

class Controller(ExtensionController):
    def __init__(self, api, api_key):
        ExtensionController.__init__(self, api, api_key)
        self.__api      = api
        self.__guard    = api.get_guard()
        self.server     = 'mail.speedpartner.de' #FIXME: Make configurable
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
        if handle == "":
            error = _("Invalid login name!")
        elif firstname == "":
            error = _("Invalid first name!")
        elif lastname == "":
            error = _("Invalid last name!")
        elif not re.match(r'\w+\@\w+\.\w+', email):
            error = _("Invalid email address!")
        elif password1 == "":
            error = _("Please enter a password!")
        elif password1 != password2:
            error = _("Passwords do not match!")
        else:
            # Check whether the username is already taken.
            res = self.__guard.get_resource(handle = handle,
                                            type   = User)
            if res is not None and res.is_group():
                error = _("A group with the given name already exists.")
            elif res is not None:
                error = _("A user with the given name already exists.")

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
        vars      = self.__api.get_requested_uri(confirm = [1], key = [key])
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


    def index(self, **kwargs):
        # If the user is already logged in do nothing.
        user = self.api.get_current_user()
        if user is not None:
            self.__api.render('complete.tmpl', user = user)
            return

        # If the link in the confirmation email was clicked, try
        # to activate the account.
        confirm = self.__api.get_get_data('confirm')
        if confirm:
            self.confirm()
            return

        # If the registration form was submitted, attempt to create
        # the account.
        register = self.__api.get_post_data('register')
        if register:
            self.register()
            return

        # Else just show the registration form.
        self.__api.render('register.tmpl')
