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
import re
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from genshi.template import TextTemplate
from genshi.template import TemplateLoader

from Environment       import Environment
from Form              import Form
from StockButton       import StockButton
from InteractionResult import InteractionResult

class WebEnvironment(Environment):
    def __init__(self, cgi_data, genshi_template = None):
        assert cgi_data is not None
        Environment.__init__(self)
        self.__tmpl      = genshi_template
        self.__cgi_data  = cgi_data
        self.__task_path = self.__get_path_from_cgi_data(cgi_data)
        self.__init_data()
        if not genshi_template:
            # Load default template from a file.
            loader = TemplateLoader([os.path.dirname(__file__)])
            self.__tmpl = loader.load('setup.tmpl', None, TextTemplate)


    def __path2string(self, path):
        if len(path) == 0:
            path = '0'
        else:
            path = '.'.join([repr(i) for i in path])
        return path


    def __get_path_from_cgi_data(self, cgi_data):
        if not cgi_data.has_key('task_path'):
            return [0]
        path = []
        for item in cgi_data['task_path'].value.split('.'):
            path.append(int(item))
        return path


    def __init_data(self):
        self.__tmpl_data = {
          'content':     '',
          'buttons':     [StockButton('next_button')]
        }


    def __flush_template(self):
        task_path = self.__path2string(self.__task_path)
        stream = self.__tmpl.generate(app_name    = self._app_name,
                                      app_version = self._app_version,
                                      task_path   = task_path,
                                      **self.__tmpl_data)
        print stream.render('text')
        self.__init_data()


    def start_task(self, path):
        assert type(path) == type([])
        self.__task_path = path


    def end_task(self, path):
        assert type(path) == type([])
        self.__task_path = [0]
        self.__cgi_data  = {}


    def get_task_path(self):
        return self.__task_path


    def __compile_markup_tag(self, match):
        tag_name = match.group(1)

        # Label tags.
        if tag_name == 'label':
            return match.group(2)[1:-1]
        if tag_name == 'title':
            return '<h2>' + match.group(2)[1:-1] + '</h2>'

        # Text fields.
        if tag_name == 'entry':
            entry_name = match.group(2)
            return '<input type="text" name="%s" value="" />' % entry_name

        # Hidden fields.
        if tag_name == 'variable':
            var_name  = match.group(2)
            var_value = match.group(3)[1:-1]
            return '<input type="hidden" name="%s" value="%s" />' % (var_name,
                                                                     var_value)

        # Select box tags.
        if tag_name == 'select':
            select_name = match.group(2)
            return '<select name="%s">' % select_name
        if tag_name == 'item':
            item_name = match.group(2)
            item_value = match.group(3)
            if item_value is None:
                item_value = item_name
            return '<option name="%s">%s</option>' % (item_name, item_value)
        if tag_name == 'end_select':
            return '</select>'
        return match.group()


    def render_markup(self, markup):
        word_re = '[\w_]+'
        arg_re  = '(?:' + word_re + '|\"[^\"]+\")'
        tag_re  = re.compile('{(\w+)' +               
                             '(?: (' + arg_re + '))?' + 
                             '(?: (' + arg_re + '))*}')
        data    = tag_re.sub(self.__compile_markup_tag, markup.get_markup())
        data    = data.replace('\n', '<br/>\n')
        tmpl    = TextTemplate(data)
        stream  = tmpl.generate()
        self.__tmpl_data['content'] = stream.render('text')
        self.__tmpl_data['buttons'] = markup.get_buttons()
        self.__flush_template()
        return False


    def get_interaction_result(self):
        if len(self.__cgi_data.keys()) == 0:
            return None
        result = InteractionResult()
        for key in self.__cgi_data.keys():
            result.set(key, self.__cgi_data[key].value)
        return result
