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
import os, re, sha, smtplib, functions, random

class Extension:
    def __init__(self, api):
        self.__api      = api
        self.i18n       = api.get_i18n()
        self.__login    = api.get_login()
        self.__guard    = api.get_guard()
        self.__guard_db = api.get_guard_db()
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
            res = self.__guard_db.get_resource_from_handle(handle, 'users')
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
        section  = self.__guard_db.get_resource_section_from_handle('users')
        users    = self.__guard_db.get_resource_from_handle('users', 'users')
        resource = self.__guard.Resource(name, handle)
        pwd_hash = self.__login.hash_password(password1)
        resource.set_attribute('password',       pwd_hash)
        resource.set_attribute('inactive',       True)
        resource.set_attribute('activation_key', key)
        self.__guard_db.add_resource(users.get_id(), resource, section)

        # Format activation email.
        #FIXME: Make configurable.
        domain    = 'http://' + os.environ['HTTP_HOST']
        vars      = functions.get_request_uri(confirm = [1], key = [key])
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
        kname   = 'activation_key'
        section = self.__guard_db.get_resource_section_from_handle('users')
        users   = self.__guard_db.get_resource_list_from_attribute(kname, key)
        if users is None or len(users) != 1:
            self.__api.render('register.tmpl', error = 'Invalid key')
            return

        # Activate the account.
        user = users[0]
        user.remove_attribute('inactive')
        user.remove_attribute('activation_key')
        self.__guard_db.save_resource(user, section)

        self.__api.render('complete.tmpl', user = user)


    def on_render_request(self):
        self.__api.emit('render_start')

        # If the user is already logged in do nothing.
        user = self.__login.get_current_user()
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
