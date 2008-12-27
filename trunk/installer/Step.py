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
from genshi.template import TemplateLoader
from genshi.template import MarkupTemplate

class Step(object):
    def __init__(self, id, request, state):
        self.id      = id
        self.request = request
        self.state   = state


    def render(self, filename, **kwargs):
        loader  = TemplateLoader(['.'])
        tmpl    = loader.load(filename, None, MarkupTemplate)
        next_id = self.id + 1
        output  = tmpl.generate(nextstep = next_id, **kwargs).render('xhtml')
        self.request.write(output)


    def check(self):
        return True


    def submit(self):
        return True
