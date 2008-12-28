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
import os.path # , pickle, pprint
from ConfigParser import RawConfigParser
from State        import State

class StateDB(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.rcparser = RawConfigParser()
        if not os.path.exists(data_dir):
            os.mkdir(self.data_dir)


    def _filename_of(self, id):
        return os.path.join(self.data_dir, 'state%d.cfg' % id)


    def get(self, id):
        """
        Returns the state with the given id. If no such state exists, a new 
        state is returned.
        """
        assert id is not None
        state    = State()
        state.id = id
        if os.path.exists(self._filename_of(id)):
            self.rcparser.read(self._filename_of(id))
            for key, value in self.rcparser.items('state'):
                state.__setattr__(key, value)
        #Unfortunately mod_python does not work with pickle.
        #input = open(self._filename_of(id), 'rb')
        #state = pickle.load(input)
        #input.close()
        return state


    def save(self, id, state):
        """
        Persistently saves the given state under the given id.
        """
        assert id    is not None
        assert state is not None
        output = open(self._filename_of(id), 'wb')
        output.write("[state]\n")
        state.id = id
        for key, value in state.__dict__.iteritems():
            output.write('%s=%s' % (key, value) + "\n")
        #pickle.dump(state, output, -1)
        output.close()
