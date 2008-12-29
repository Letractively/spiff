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
import os.path, sys
from ConfigParser import RawConfigParser

# Note that locally installed libs take preference.
sys.path.insert(0, '.')
for lib in ('pywsgi',
            'spiff-signal',
            'spiff-guard',
            'spiff-integrator',
            'spiff-warehouse'):
    dir = os.path.join('libs', lib, 'src')
    sys.path.insert(0, dir)

# Define common variables.
__version__   = '0.0.1'
base_dir      = os.path.dirname(__file__)
installer_dir = os.path.join(base_dir, 'installer')
data_dir      = os.path.join(base_dir, 'data')
cfg_file      = os.path.join(data_dir, 'spiff.cfg')
package_dir   = os.path.join(data_dir, 'repo')
upload_dir    = os.path.join(data_dir, 'uploads')
warehouse_dir = os.path.join(data_dir, 'warehouse')
session_dir   = os.path.join(data_dir, 'sessions')
cache_dir     = os.path.join(data_dir, 'cache')
cfg           = RawConfigParser()
cfg.read(cfg_file)
