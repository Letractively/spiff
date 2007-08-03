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
class Slot(object):
    def __init__(self):
        self.subscribers = []

    def subscribe(self, func):
        self.subscribers.append(func)

    def emit(self, name, *args, **kwargs):
        for func in self.subscribers:
            func(name, **kwargs)


class Trackable(object):
    def __init__(self):
        self.slots = {}

    def signal_connect(self, name, func):
        if not self.slots.has_key(name):
            self.slots[name] = Slot()
        self.slots[name].subscribe(func)

    def emit(self, name, *args, **kwargs):
        if not self.slots.has_key(name):
            return
        self.slots[name].emit(name, **kwargs)
