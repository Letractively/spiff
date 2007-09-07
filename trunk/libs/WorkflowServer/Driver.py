# Copyright (C) 2007 Samuel Abels
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
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
