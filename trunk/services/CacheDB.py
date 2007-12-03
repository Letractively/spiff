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
import os, sha
from sqlalchemy import *

class CacheDB(object):
    def __init__(self, guard, session):
        self.__guard       = guard
        self.__db          = guard.db
        self.__session     = session
        self.__perm_hash   = None
        self._table_prefix = ''
        self._table_map    = {}
        self._table_list   = []
        self.__update_table_names()


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
        metadata  = self.__guard.db_metadata
        pfx       = self._table_prefix
        guard_pfx = self.__guard.get_table_prefix()
        self._table_list = []
        self.__add_table(Table(pfx + 'cache_item', metadata,
            Column('id',          Integer,     primary_key = True),
            Column('page_id',     Integer,     index = True),
            Column('permissions', String(42),  index = True),
            Column('uri',         String(250), index = True),
            Column('section',     String(30),  index = True),
            Column('content',     TEXT),
            Column('created',     DateTime,    default = func.now()),
            ForeignKeyConstraint(['page_id'],
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
        Define a string that is prefixed to all table names in the database.
        By default, no prefix is used.

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
        delete = self._table_map['cache_item'].delete()
        result = delete.execute()
        return True


    def _get_permission_hash(self):
        """
        This function returns a string the identifies all permissions
        of the current user on the current group.
        """
        if self.__perm_hash is not None:
            return self.__perm_hash
        page   = self.__session.get_requested_page()
        user   = self.__session.get_user()
        string = page.get_attribute('private') and 'p' or 'np'
        if user is None:
            return string
        guard = self.__guard
        acls  = guard.get_permission_list_with_inheritance(actor    = user,
                                                           resource = page)
        for acl in acls:
            string += str(acl)
        self.__perm_hash = sha.new(string).hexdigest()
        return self.__perm_hash


    def _get_item(self, section):
        """
        There are three possible reasons why a cached item may become
        invalid:
          1. The extension that generates the output changed internally
          such that, given the same parameters, it generates different
          output. This is solved by 
            a) only caching extensions that requested so. This is not
            ensured in this place because we have no knowledge of extensions;
            the choice is currently made by the layout renderer.
            b) Extensions that requested to be cached may call our flush()
            method whenever they did something that breaks the output.
          2. The permissions of the user for whom the item was cached
          changed, such that the extension will now generate a different
          result when making a decision based on the current user. This is
          solved by grouping callers into permission groups, such that all
          callers that have the same permissions use the same cache.
          3. The cached item has expired. After a certain amount of time
          has passed, the item is removed from the cache.
        """
        permissions = self._get_permission_hash()
        page        = self.__session.get_requested_page()
        uri         = os.environ["QUERY_STRING"]
        table       = self._table_map['cache_item']
        #print "GET:", permissions, page.get_id(), uri
        sel         = select([table.c.content],
                             and_(table.c.page_id     == page.get_id(),
                                  table.c.permissions == permissions,
                                  table.c.uri         == uri,
                                  table.c.section     == section),
                             from_obj = [table])
        result      = sel.execute()
        row         = result.fetchone()
        if row is None:
            return None
        #print "Cache hit"
        return row.content


    def add(self, section, content):
        permissions = self._get_permission_hash()
        page        = self.__session.get_requested_page()
        uri         = os.environ["QUERY_STRING"]
        insert      = self._table_map['cache_item'].insert()
        result      = insert.execute(page_id     = page.get_id(),
                                     permissions = permissions,
                                     uri         = uri,
                                     section     = section,
                                     content     = content)
        #print "Cache added"


    def get(self, section):
        cache_item = self._get_item(section)
        if cache_item is None:
            return None
        return cache_item


    def add_page(self, content):
        return self.add('', content)


    def get_page(self):
        return self.get('')


    def is_fresh(self, section):
        permissions = self._get_permission_hash()
        page        = self.__session.get_requested_page()
        uri         = os.environ["QUERY_STRING"]
        table       = self._table_map['cache_item']
        sel         = select([table.c.id],
                             and_(table.c.page_id     == page.get_id(),
                                  table.c.permissions == permissions,
                                  table.c.uri         == uri,
                                  table.c.section     == section),
                             from_obj = [table])
        result      = sel.execute()
        return result.rowcount == 1


    def flush(self, section, **kwargs):
        """
        An extension may wish to invalidate parts of the cache. Those parts
        may fall into one of the following categories:
          1. All pages where the extension is used (default).
          2. The current page and all URLs that have the same handle as the
          current URL in them.
          3. The current page, and all URLs that have a specified variable
          in them.
          3. Only the current page.
        """
        delete = self._table_map['cache_item'].delete()
        delete.execute(section = section, **kwargs)
        delete.execute(section = '', **kwargs) # Also flush the full page.
