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
import os.path
from ConfigParser import RawConfigParser

__version__   = '0.0.1'
data_dir      = os.path.join(os.path.dirname(__file__), 'data')
plugin_dir    = os.path.join(os.path.dirname(__file__), 'plugins')
cfg_file      = os.path.join(data_dir, 'spiff.cfg')
package_dir   = os.path.join(data_dir, 'repo')
upload_dir    = os.path.join(data_dir, 'uploads')
warehouse_dir = os.path.join(data_dir, 'warehouse')
cache_dir     = os.path.join(data_dir, 'cache')
installer_dir = os.path.join(os.path.dirname(__file__), 'installer')
cfg           = RawConfigParser()
cfg.read(cfg_file)
