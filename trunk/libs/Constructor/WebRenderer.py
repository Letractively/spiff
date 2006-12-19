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
from Renderer import Renderer
import sys
import os.path
sys.path.append('..')
from genshi.template import TextTemplate
from genshi.template import TemplateLoader

class WebRenderer(Renderer):
    __type_section, \
    __type_task = range(2)

    def __init__(self, genshi_template = None):
        Renderer.__init__(self)
        self.__level     = 1
        self.__tmpl      = genshi_template
        self.__tmpl_data = {'data': []}
        if not genshi_template:
            # Load default template from a file.
            loader = TemplateLoader([os.path.dirname(__file__)])
            self.__tmpl = loader.load('setup.tmpl', None, TextTemplate)


    def __flush_template(self):
        if len(self.__tmpl_data['data']) == 0:
            return
        stream = self.__tmpl.generate(app_name    = self._app_name,
                                      app_version = self._app_version,
                                      **self.__tmpl_data)
        print stream.render('text')
        self.__tmpl_data = {'data': []}


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


    def task_done(self, message, result):
        task = dict(level   = self.__level,
                    type    = self.__type_task,
                    message = message,
                    result  = result)
        self.__tmpl_data['data'].append(task)
