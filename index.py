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
    print 'Please configure Spiff before you access this site.<br/>'
    print 'The INSTALL file shipped with the Spiff installation contains'
    print 'instructions on how this can be done.'
    sys.exit()

if os.path.exists('install'):
    print 'Out of security reasons, please delete the install/ directory before'
    print 'accessing this page.'
    sys.exit()

def requested_page(form_data):
    if not form_data.has_key('page'):
        return 'system/login'
    return form_data['page'].value


# Read config.
cfg = RawConfigParser()
cfg.read('data/spiff.cfg')
dbn = cfg.get('database', 'dbn')

# Connect to MySQL and set up.
db         = create_engine(dbn)
acldb      = Guard.DB(db)
form_data  = cgi.FieldStorage()
integrator = Integrator.Manager(acldb, form_data)
integrator.set_extension_dir('data/repo')

# Lookup page from the given cgi variables.
page     = requested_page(form_data)
page_res = acldb.get_resource_from_handle(page, 'content')
if page_res is None:
    print 'error 404'
    sys.exit()

# Load the appended plugins.
descriptor = page_res.get_attribute('extension')
extension  = integrator.load_extension_from_descriptor(descriptor)
if extension is None:
    print 'Page "%s" refers to unknown extension "%s"' % (page, descriptor)

integrator.extension_api.emit_sync('spiff:page_open')
extension.on_render_request()
