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
import config, util, os.path
from Step import Step

class CheckRequirements(Step):
    def __init__(self, id, request, state):
        Step.__init__(self, id, request, state)
        self.results = [self._is_not_installed(),
                        util.check_python_version((2, 3, 0, '', 0)),
                        util.check_dir_exists(config.data_dir),
                        util.check_is_writable(config.data_dir),
                        util.check_python_module_exists('pywsgi'),
                        util.check_python_module_exists('SpiffGuard'),
                        util.check_python_module_exists('SpiffIntegrator'),
                        util.check_python_module_exists('SpiffSignal'),
                        util.check_python_module_exists('SpiffWarehouse'),
                        util.check_python_module_exists('SpiffWikiMarkup')]
        self.failed  = False in [r for n, r, e in self.results]


    def _is_not_installed(self):
        name = 'Checking whether the installation is already complete.'
        if not os.path.exists(config.cfg_file):
            return name, True, None
        try:
            from ConfigParser import RawConfigParser
            parser = RawConfigParser()
            parser.read(config.cfg_file)
            installed_version = parser.get('installer', 'version')
        except Exception, e:
            return name, False, str(e)
        if installed_version == config.__version__:
            error = 'Version %s is already installed.' % installed_version
            return name, False, error
        return name, True, None


    def show(self):
        self.render('CheckRequirements.tmpl',
                    results = self.results,
                    success = not self.failed)


    def check(self):
        if self.failed:
            self.show()
            return False
        return True
