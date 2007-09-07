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
from sqlalchemy import *
from DB         import DB

class Driver:
    """
    A store provides an API for storing and loading workflows, receiving
    information regarding running Jobs, and for driving the workflow
    execution.
    """
    
    def __init__(self, db):
        """
        Instantiates a new Driver.
        
        @type  db: DB
        @param db: An Spiff Workflow DB object.
        @rtype:  Driver
        @return: The new instance.
        """
        self.db = db
