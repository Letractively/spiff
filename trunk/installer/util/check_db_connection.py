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
from sqlalchemy import *

def check_db_connection(dbn):
    name   = 'Checking the database connection'
    hint   = 'The database connection failed. Please check your username,' \
           + ' password, and other database settings.'
    engine = create_engine(dbn)
    try:
        conn = engine.connect()
    except:
        return name, False, hint
    return name, True, None
