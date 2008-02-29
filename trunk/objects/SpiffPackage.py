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
from Integrator import Package

class SpiffPackage(Package):
    def __init__(self, *args, **kwargs):
        Package.__init__(self, *args, **kwargs)
        self.__module = None


    def test(self):
        #instance = package.load()
        
        # Check whether the package has an install() method.
        install_func = None
        try:
            install_func = getattr(instance, 'install')
        except:
            pass
        if install_func is not None:
            print "Package has an install() method."

        # Some day we may be smart enough to call install_func() here.
        #FIXME

        return True


    def load(self):
        """
        Imports the package, creates an instance, and returns a reference
        to it. Always returns a reference to the same instance if called
        multiple times.

        @rtype:  object
        @return: The instance of package.
        """
        assert self._parent is not None
        if self.__module is not None:
            return self.__module

        module   = __import__(self.get_module_dir())
        instance = module.Extension(self._parent.package_api)

        self.__module = instance
        self._parent._load_notify(self, instance)
        return self.__module
