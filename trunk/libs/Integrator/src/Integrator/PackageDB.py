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
from sqlalchemy      import *
from Package         import Package
from Callback        import Callback
from Guard.functions import make_handle_from_string
from functions       import *

class PackageDB(object):
    def __init__(self, guard):
        """
        Instantiates a new DB.
        
        @type  guard: AclDB
        @param guard: A Spiff Guard AclDB instance.
        @rtype:  DB
        @return: The new instance.
        """
        self.db                  = guard.db
        self._guard              = guard
        self._table_prefix       = 'integrator_'
        self._table_map          = {}
        self._table_list         = []
        self.__update_table_names()
        self._guard.register_type(Package)


    def __add_table(self, table):
        """
        Adds a new table to the internal table list.
        
        @type  table: Table
        @param table: An sqlalchemy table.
        """
        pfx = self._table_prefix
        self._table_list.append(table)
        self._table_map[table.name[len(pfx):]] = table


    def __update_table_names(self):
        """
        Adds all tables to the internal table list.
        """
        metadata  = self._guard.db_metadata
        pfx       = self._table_prefix
        guard_pfx = self._guard.get_table_prefix()
        self._table_list = []
        self.__add_table(Table(pfx + 'package_dependency', metadata,
            Column('id',                  Integer,    primary_key = True),
            Column('package_id',          Integer,    index = True),
            Column('dependency_handle',   String(20), index = True),
            Column('dependency_operator', String(3),  index = True),
            Column('dependency_version',  String(20), index = True),
            ForeignKeyConstraint(['package_id'],
                                 [guard_pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            useexisting = True,
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'package_dependency_map', metadata,
            Column('package_id',    Integer, index = True),
            Column('dependency_id', Integer, index = True),
            ForeignKeyConstraint(['package_id'],
                                 [guard_pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['dependency_id'],
                                 [guard_pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            useexisting = True,
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'package_signal', metadata,
            Column('id',         Integer,     primary_key = True),
            Column('package_id', Integer,     index = True),
            Column('uri',        String(255), index = True),
            ForeignKeyConstraint(['package_id'],
                                 [guard_pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            useexisting = True,
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'package_listener', metadata,
            Column('id',         Integer,     primary_key = True),
            Column('package_id', Integer,     index = True),
            Column('uri',        String(255), index = True),
            ForeignKeyConstraint(['package_id'],
                                 [guard_pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            useexisting = True,
            mysql_engine='INNODB'
        ))


    def debug(self, debug = True):
        """
        Enable/disable debugging.

        @type  debug: Boolean
        @param debug: True to enable debugging.
        """
        self.db.echo = debug


    def set_table_prefix(self, prefix):
        """
        Define a table prefix. Default is 'warehouse_'.

        @type  prefix: string
        @param prefix: The new prefix.
        """
        assert prefix is not None
        self._table_prefix = prefix
        self.__update_table_names()


    def get_table_prefix(self):
        """
        Returns the current database table prefix.
        
        @rtype:  string
        @return: The current prefix.
        """
        return self._table_prefix


    def install(self):
        """
        Installs (or upgrades) database tables.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        for table in self._table_list:
            table.create(checkfirst = True)
        return True


    def uninstall(self):
        """
        Drops all tables from the database. Use with care.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        for table in self._table_list[::-1]:
            table.drop(checkfirst = True)
        return True


    def clear_database(self):
        """
        Drops the content of any database table used by this library.
        Use with care.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        self._guard.delete_resource_from_match(type = Package)
        return True


    def __has_dependency_link_from_id(self, package_id, dependency_id):
        assert package_id  >= 0
        assert dependency_id >= 0
        table  = self._table_map['package_dependency_map']
        query  = select([table.c.package_id],
                        and_(table.c.package_id  == package_id,
                             table.c.dependency_id == dependency_id),
                        from_obj = [table])
        result = query.execute()
        row    = result.fetchone()
        if not row:
            return False
        return True

    
    def __add_dependency_link_from_id(self, package_id, dependency_id):
        assert package_id  >= 0
        assert dependency_id >= 0
        table  = self._table_map['package_dependency_map']
        query  = table.insert()
        result = query.execute(package_id  = package_id,
                               dependency_id = dependency_id)


    def __get_dependency_id_list_from_id(self, package_id):
        assert package_id >= 0
        table  = self._table_map['package_dependency_map']
        query  = select([table.c.dependency_id],
                        table.c.package_id == package_id,
                        from_obj = [table])
        result = query.execute()

        dependency_id_list = []
        for row in result:
            dependency_id_list.append(row[table.c.dependency_id])
        return dependency_id_list


    def __get_dependency_id_list(self, package):
        assert package is not None
        return self.__get_dependency_id_list_from_id(package.get_id())


    def __get_dependency_descriptor_list_from_id(self, package_id):
        assert package_id >= 0
        table  = self._table_map['package_dependency']
        query  = select([table.c.dependency_handle,
                         table.c.dependency_operator,
                         table.c.dependency_version],
                        table.c.package_id == package_id,
                        from_obj = [table])
        result = query.execute()

        dependency_list = []
        for row in result:
            handle   = row[table.c.dependency_handle]
            operator = row[table.c.dependency_operator]
            version  = row[table.c.dependency_version]
            dependency_list.append(handle + operator + version)
        return dependency_list


    def __get_dependency_descriptor_list(self, package):
        assert package is not None
        return self.__get_dependency_descriptor_list_from_id(package.get_id())


    def __load_dependency_descriptor_list(self, package):
        assert package is not None
        list = self.__get_dependency_descriptor_list(package)
        for dependency in list:
            package._add_dependency(dependency)
        return True

    
    def __link_package_id_to_signal(self, package_id, uri):
        """
        Associates the given package with the given signal.

        @type  package_id: int
        @param package_id: The id of the package to be associated.
        @type  uri: URI of a signal.
        @param uri: The signal to be associated.
        @rtype:  int
        @return: The id of the signal, or <0 if an error occured.
        """
        assert package_id >= 0
        assert uri is not None
        
        table  = self._table_map['package_signal']
        query  = table.insert()
        result = query.execute(package_id = package_id, uri = uri)
        assert result is not None
        return result.last_inserted_ids()[0]


    def __link_package_id_to_listener(self, package_id, uri):
        """
        Associates the given package with the given listener.

        @type  package_id: int
        @param package_id: The id of the package to be associated.
        @type  uri: URI of a listener.
        @param uri: The listener to be associated.
        @rtype:  int
        @return: The id of the listener, or <0 if an error occured.
        """
        assert package_id >= 0
        assert uri is not None
        
        table  = self._table_map['package_listener']
        query  = table.insert()
        result = query.execute(package_id = package_id, uri = uri)
        assert result is not None
        return result.last_inserted_ids()[0]


    def __get_package_id_list_rdepends(self, package):
        """
        Returns a list of all ids of all packages that depend on the
        given package.

        @type  package: Package
        @param package: The package to remove.
        @rtype:  list[id]
        @return: A list of package ids.
        """
        assert package.get_id() is not None
        table  = self._table_map['package_dependency_map']
        query  = select([table.c.package_id],
                        table.c.dependency_id == package.get_id(),
                        from_obj = [table])
        result = query.execute()
        return [row[table.c.package_id] for row in result]


    def check_dependencies(self, package):
        """
        Checks whether all required dependencies are registered.

        Returns True if all dependencies needed to register the given
        package are registered, False otherwise.

        @type  package: Package
        @param package: The package whose dependencies will be checked.
        @rtype:  Boolean
        @return: True if all dependency requirements are met, False otherwise.
        """
        assert package is not None
        dependency_list = package.get_dependency_list()
        for descriptor in dependency_list:
            if not self.get_package_from_descriptor(descriptor):
                return False
        return True


    def add_package(self, package):
        """
        Inserts the given Package into the database.
        The method takes no action if the package is already registered.

        @type  package: Package
        @param package: The package to install.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert package is not None
        
        # Check whether the package is already registered.
        installed = self.get_package_from_handle(package.get_handle(),
                                                 package.get_version())
        if installed is not None:
            package.set_id(installed.get_id())
            return True

        # Start transaction.
        connection  = self.db.connect()
        transaction = connection.begin()

        # Make sure that all dependencies are registered.
        assert self.check_dependencies(package)

        # Insert the package into the ACL resource table.
        self._guard.add_resource(None, package)
        
        # Insert the list of signals that this extension may send.
        for uri in package.get_signal_list():
            self.__link_package_id_to_signal(package.get_id(), uri)

        # Insert the list of events to which this extension may respond.
        for uri in package.get_listener_list():
            self.__link_package_id_to_listener(package.get_id(), uri)

        # Create a link to all dependencies (direct dependencies and
        # indirect dependencies as well).
        for descriptor in package.get_dependency_list():
            dependency_handle, \
            dependency_operator, \
            dependency_version = descriptor_parse(descriptor)

            # Add the dependency request into the database.
            table  = self._table_map['package_dependency']
            query  = table.insert()
            result = query.execute(package_id          = package.get_id(),
                                   dependency_handle   = dependency_handle,
                                   dependency_operator = dependency_operator,
                                   dependency_version  = dependency_version)
            assert result is not None

            # And link the package with the best matching dependency.
            best = self.get_package_from_descriptor(descriptor)

            # Retrieve a list of all dependencies of that dependency.
            best_id = best.get_id()
            list    = self.__get_dependency_id_list_from_id(best_id)
            list.append(best_id)

            # Add a link to all of the dependencies as well.
            for id in list:
                self.__add_dependency_link_from_id(package.get_id(), id)

        # Walk through all packages that currently depend on another
        # version of the recently registered package.
        handle  = package.get_handle()
        version = package.get_version()
        table   = self._table_map['package_dependency']
        query   = select([table],
                         and_(table.c.dependency_handle  == handle,
                              table.c.dependency_version == version),
                        from_obj = [table])
        result = query.execute()
        assert result is not None
        for row in result:
            dep_handle   = handle
            dep_operator = row[table.c.dependency_operator]
            dep_version  = row[table.c.dependency_version]
            dependency   = self.get_package_from_descriptor(dep_handle,
                                                            dep_operator,
                                                            dep_version)
            
            # No need to do anything if the registered link is already the
            # best one.
            dep_id = dependency.get_id()
            if self.__has_dependency_link_from_id(package.get_id(), dep_id):
                continue

            # Delete the old dependency links.
            self.__delete_dependency_link_from_id(package.get_id())

            # Retrieve a list of all dependencies of that dependency.
            dep_list = self.__get_dependency_id_list_from_id(dep_id)
            dep_list.append(dep_id)

            for id in dep_list:
                self.__add_dependency_link_from_id(package.get_id(), dep_id)

        # Transaction finish.
        transaction.commit()
        connection.close()
        return True


    def remove_package_from_id(self, id):
        """
        Removes the given package from the database. Warning: Also
        removes any package that requires the given Package.

        @type  id: int
        @param id: The id of the package to remove.
        @rtype:  Boolean
        @return: False if the package did not exist, True otherwise.
        """
        assert id >= 0
        dependency_list = self.__get_dependency_id_list_from_id(id)
        self._guard.delete_resource_from_match(id = id)
        # Unregister all packages that require this package.
        for dependency_id in dependency_list:
            self._guard.delete_resource_from_match(id = id)
        return True


    def remove_package_from_handle(self, handle, version):
        """
        Removes the given Package from the database.

        @type  handle: string
        @param handle: The handle of the package to remove.
        @rtype:  Boolean
        @return: False if the package did not exist, True otherwise.
        """
        assert handle is not None
        package = self.get_package_from_handle(handle, version)
        return self.remove_package_from_id(package.get_id())


    def remove_package(self, package):
        """
        Removes the given Package from the database.

        @type  package: Package
        @param package: The package to remove.
        @rtype:  Boolean
        @return: False if the package did not exist, True otherwise.
        """
        assert package is not None
        self.remove_package_from_id(package.get_id())
        return True


    def get_package_from_id(self, id):
        """
        Returns the package with the given id from the database.

        @type  id: int
        @param id: The id of the wanted package.
        @rtype:  Package
        @return: The package on success, None if it does not exist.
        """
        assert id >= 0
        package = self._guard.get_resource(id = id)
        if package is None:
            return None
        self.__load_dependency_descriptor_list(package)
        return package


    def get_package_from_handle(self, handle, version):
        """
        Returns the package with the given handle from the database.

        @type  handle:  string
        @param handle:  The handle of the wanted package.
        @type  version: string
        @param version: The version number of the wanted package.
        @rtype:  Package
        @return: The Package on success, None if none was found.
        """
        assert handle  is not None
        assert version is not None
        attribute = {'version': version}
        package   = self._guard.get_resource(handle    = handle,
                                             attribute = attribute,
                                             type      = Package)
        if package is None:
            return None
        self.__load_dependency_descriptor_list(package)
        return package


    def get_package_from_descriptor(self, descriptor):
        """
        Returns the package that best matches the given descriptor.

        Looks for all packages that match the given descriptor and
        returns the one with the highest version number.

        The descriptor is defined as follows:
          [handle][descriptor][version]
        where
          handle     is the handle of the package.
          descriptor is one of '>=', '='.
          version    is a version number.
        
        Descriptor examples:
          spiff>=0.1
          spiff_forum=1.2.3

        @type  descriptor: string
        @param descriptor: The descriptor as specified above.
        @rtype:  Package
        @return: The Package on success, None if none was found.
        """
        assert descriptor is not None
        #print "Descriptor:", descriptor
        handle, operator, version = descriptor_parse(descriptor)
        if operator == '=':
            return self.get_package_from_handle(handle, version)

        # Ending up here, the operator is '>='.
        # Select the dependency with the version number that
        # matches the version requirement.
        version_list = self.get_version_list_from_handle(handle)
        best_version = None
        for cur_version in version_list:
            if best_version is None:
                best_version = cur_version
                continue
            if version_is_greater(best_version.get_version(),
                                  cur_version.get_version()):
                continue
            if version_is_greater(cur_version.get_version(),
                                  best_version.get_version()):
                best_version = cur_version
        if best_version is None:
            return None
        return best_version


    def get_package_from_name(self, name):
        """
        Returns the package that matches the given name and that has the
        highest version number.

        @type  name: string
        @param name: The name of the package.
        @rtype:  Package
        @return: The Package on success, None if none was found.
        """
        assert name is not None

        version_list = self.get_version_list_from_name(name)
        best_version = None
        for cur_version in version_list:
            if best_version is None:
                best_version = cur_version
                continue
            if version_is_greater(best_version.get_version(),
                                  cur_version.get_version()):
                continue
            if version_is_greater(cur_version.get_version(),
                                  best_version.get_version()):
                best_version = cur_version
        if best_version is None:
            return None
        return best_version


    def get_package_list(self, offset = 0, limit = 0, **kwargs):
        """
        Returns a list of all installed packages that match the given
        criteria.

        @type  offset: int
        @param offset: The number of packages to skip.
        @type  limit: int
        @param limit: The maximum number of packages returned.
        @type  kwargs: dict
        @param kwargs: The following keywords are accepted:
                        - id: The id of the package.
                        - depends: A package on which the returned
                          package depends.
        @rtype:  list[Package]
        @return: The list of packages.
        """
        if kwargs.has_key('depends'):
            id_list = self.__get_package_id_list_rdepends(kwargs['depends'])
            if kwargs.has_key('id'):
                if kwargs.get('id') not in id_list:
                    return []
                kwargs['id'] = [id]
            else:
                kwargs['id'] = id_list
        if kwargs.has_key('id') and len(kwargs.get('id')) == 0:
            return []
        packages = self._guard.get_resources(offset,
                                             limit,
                                             type = Package,
                                             **kwargs)
        return packages


    def get_version_list_from_handle(self, handle):
        """
        Returns a list of all registered versions that have the given
        handle.

        @type  handle: string
        @param handle: The handle of the wanted package versions.
        @rtype:  list[Package]
        @return: A list containing all versions of the requested package.
        """
        return self._guard.get_resources(handle = handle, type = Package)


    def get_version_list_from_name(self, name):
        """
        Returns a list of all registered versions that have the given
        name.

        @type  name: string
        @param name: The handle of the wanted package versions.
        @rtype:  list[Package]
        @return: A list containing all versions of the requested package.
        """
        return self._guard.get_resources(name = name, type = Package)


    def get_listener_list_from_package_id(self, package_id):
        """
        Returns the list of listeners that the package with the given
        id has registered.

        @type  package_id: integer
        @param package_id: The id of the package.
        @rtype:  list[string]
        @return: A list of URIs.
        """
        assert package_id is not None
        
        table  = self._table_map['package_listener']
        query  = select([table.c.uri],
                        table.c.package_id == package_id,
                        from_obj = [table])
        result = query.execute()
        assert result is not None

        uri_list = []
        for row in result:
            uri_list.append(row[table.c.uri])
        return uri_list


    def get_listener_id_list_from_uri(self, uri):
        """
        Returns a list of all ids of packages that are subscribed to the
        signal with the given URI.

        @type  uri: URI of an event. % wildcard allowed.
        @param uri: The event to look for.
        @rtype:  list[int]
        @return: A list containing all associated package ids, None on error.
        """
        assert uri is not None
        
        table  = self._table_map['package_listener']
        query  = select([table.c.package_id],
                        table.c.uri.like(uri),
                        from_obj = [table])
        result = query.execute()
        return [row[table.c.package_id] for row in result]
