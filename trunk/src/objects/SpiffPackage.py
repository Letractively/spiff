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
from SpiffIntegrator import Package

class SpiffPackage(Package):
    def __init__(self, *args, **kwargs):
        Package.__init__(self, *args, **kwargs)
        self.__controller_module = None
        self.__controller        = None


    def _mkapikey(self):
        return self.get_id() #FIXME: There are probably better keys...


    def _get_controller_module(self):
        """
        Imports the controller without creating an instance.
        Always returns a reference to the same module if called multiple times.

        @rtype:  object
        @return: The controller module.
        """
        assert self._parent is not None
        if self.__controller_module is not None:
            return self.__controller_module

        modname = self.get_module_dir() + '.Controller'
        self.__controller_module = __import__(modname,
                                              globals(),
                                              locals(),
                                              ['Controller', 'check_cache'])
        return self.__controller_module


    def _get_controller(self):
        """
        Imports the package, creates an instance of the controller, and 
        returns a reference to it. Always returns a reference to the same 
        instance if called multiple times.

        @rtype:  object
        @return: The instance of package.
        """
        if self.__controller is not None:
            return self.__controller
        module            = self._get_controller_module()
        self.__controller = module.Controller(self._parent.package_api,
                                              self._mkapikey())
        return self.__controller


    def test(self):
        #FIXME: We should add more tests here.

        # Check whether the package has an install() method.
        install_func = None
        try:
            install_func = getattr(instance, 'install')
        except:
            pass
        if install_func is not None:
            print "Package has an install() method."

        #FIXME: Some day we may be smart enough to call install_func() here.

        return True


    def check_cache(self):
        if self.get_attribute('cacheable') == False:
            return False
        module = self._get_controller_module()
        if 'check_cache' not in dir(module):
            return True
        return module.check_cache(self._parent.package_api, self._mkapikey())


    def render(self):
        controller = self._get_controller()
        args       = dict(self._parent.package_api.get_data())
        args.update(dict(self._parent.package_api.post_data()))
        action     = args.get('action', 'index')

        if action not in dir(controller):
            return 'Controller has no action %s.' % repr(action)

        method = controller.__getattribute__(action)
        method(**args)
        output = self._parent.package_api.get_output()
        self._parent.package_api.clear_output()
        return output
