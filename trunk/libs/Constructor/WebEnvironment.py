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
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from genshi.template import TextTemplate
from genshi.template import TemplateLoader

from Environment       import Environment
from Form              import Form
from InteractionResult import InteractionResult

class WebEnvironment(Environment):
    __type_section, \
    __type_task = range(2)

    def __init__(self, cgi_form_data, genshi_template = None):
        assert cgi_form_data is not None
        Environment.__init__(self)
        self.__cgi_form_data = cgi_form_data
        self.__level         = 1
        self.__tmpl          = genshi_template
        self.__init_data()
        if not genshi_template:
            # Load default template from a file.
            loader = TemplateLoader([os.path.dirname(__file__)])
            self.__tmpl = loader.load('setup.tmpl', None, TextTemplate)


    def __init_data(self):
        self.__tmpl_data = {
          'data':      [],
          'buttons':   [Form.caption[Form.next_button]],
          'task_path': self.get_task_path()
        }


    def __flush_template(self, force = False):
        if len(self.__tmpl_data['data']) == 0 and not force:
            return
        stream = self.__tmpl.generate(app_name    = self._app_name,
                                      app_version = self._app_version,
                                      **self.__tmpl_data)
        print stream.render('text')
        self.__init_data()


    def set_task_path(self, path):
        if not self.__cgi_form_data.has_key('task_path'):
            return
        if len(path) == 0:
            self.__cgi_form_data['task_path'].value = '0'
            return
        #print "Setting path:", path
        path = '.'.join([repr(i) for i in path])
        self.__cgi_form_data['task_path'].value = path
        self.__tmpl_data['task_path'] = path


    def get_task_path(self):
        if not self.__cgi_form_data.has_key('task_path'):
            return [0]
        path = []
        for item in self.__cgi_form_data['task_path'].value.split('.'):
            path.append(int(item))
        return path


    def end(self):
        self.__flush_template()


    def section_start(self, name):
        section = dict(level = self.__level,
                       type  = self.__type_section,
                       name  = name)
        self.__tmpl_data['data'].append(section)
        self.__level += 1


    def section_end(self):
        self.__level -= 1
        if self.__level == 1:
            self.__flush_template()


    def task_done(self, message, result, hint = ''):
        task = dict(level   = self.__level,
                    type    = self.__type_task,
                    message = message,
                    result  = result,
                    hint    = hint)
        self.__tmpl_data['data'].append(task)


    def show_form(self, form):
        tmpl   = TextTemplate(form.get_markup())
        stream = tmpl.generate()
        self.__tmpl_data['content'] = stream.render('text')
        for button in form.get_buttons():
            self.__tmpl_data['buttons'].append(Form.caption[button])
        self.__flush_template(True)
        return False


    def get_form_data(self):
        if len(self.__cgi_form_data.keys()) == 0:
            return None
        result = InteractionResult()
        for key in self.__cgi_form_data.keys():
            result.set(key, self.__cgi_form_data[key].value)
        return result
