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
import sys, cgi, os, os.path
from genshi.template import TemplateLoader
from genshi.template import TextTemplate
sys.path.insert(0, '.')
sys.path.insert(0, '..')
os.chdir(os.path.dirname(__file__))
import config
from Welcome            import Welcome
from CheckRequirements  import CheckRequirements
from DatabaseSetup      import DatabaseSetup
from CreateDefaultSetup import CreateDefaultSetup
from CreateDefaultUser  import CreateDefaultUser
from Done               import Done
from StateDB            import StateDB

steps = [Welcome,
         CheckRequirements,
         DatabaseSetup,
         CreateDefaultSetup,
         CreateDefaultUser,
         Done]

def run(request):
    # Render the header.
    loader = TemplateLoader(['.'])
    tmpl   = loader.load('header.tmpl', None, TextTemplate)
    output = tmpl.generate(version = config.__version__).render('text')
    request.write(output)

    # Perform the task.
    state_db     = StateDB(os.path.join(config.data_dir, 'installer_states'))
    step_id      = int(request.get_get_data('step', [0])[0])
    prev_step_id = step_id - 1
    state        = state_db.get(prev_step_id)
    step_cls     = steps[step_id]

    if request.has_post_data():
        prev_step = steps[prev_step_id](prev_step_id, request, state)
        if prev_step.check() and prev_step.submit():
            state_db.save(step_id, state)
            step = step_cls(step_id, request, state)
            step.show()
    else:
        step = step_cls(step_id, request, state)
        step.show()

    # Render the footer.
    tmpl   = loader.load('footer.tmpl', None, TextTemplate)
    output = tmpl.generate().render('text')
    request.write(output)
