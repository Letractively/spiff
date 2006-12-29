#!/usr/bin/python
import sys, cgi, os.path
sys.path.append('libs')
import MySQLdb, Integrator
from sqlalchemy   import *
from ConfigParser import RawConfigParser
import Guard

print 'Content-Type: text/html'
print

if not os.path.exists('data/spiff.cfg'):
    print 'You need to configure Spiff before you can access this site.<br/>'
    print 'Plase refer to the INSTALL file shipped with the Spiff'
    print 'installation.'
    sys.exit()

if os.path.exists('install'):
    print 'Out of security reasons, please delete the admin/ directory before'
    print 'accessing this page.'
    sys.exit()

def requested_page():
    vars = cgi.FieldStorage()
    if not vars.has_key('page'):
        return 'system/login'
    return vars['page'].value


# Read config.
cfg = RawConfigParser()
cfg.read('data/spiff.cfg')
dbn = cfg.get('database', 'dbn')

# Connect to MySQL and set up.
db         = create_engine(dbn)
acldb      = Guard.DB(db)
integrator = Integrator.Manager(acldb)
integrator.set_extension_dir('data/repo')

# Lookup page from the given cgi variables.
page     = requested_page()
page_res = acldb.get_resource_from_handle(page, 'content')
if page_res is None:
    print 'error 404'
    sys.exit()

# Load the appended plugins.
print page_res.get_attribute_list()
descriptor = page_res.get_attribute('extension')
extension  = integrator.load_extension_from_descriptor(descriptor)
if extension is None:
    print 'Page "%s" refers to unknown extension "%s"' % (page, descriptor)
