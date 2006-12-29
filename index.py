#!/usr/bin/python
import sys, cgi
sys.path.append('libs')
import MySQLdb, Integrator
from sqlalchemy   import *
from ConfigParser import RawConfigParser
import Guard

print 'Content-Type: text/html'
print

# Read config.
cfg = RawConfigParser()
cfg.read('data/spiff.cfg')
dbn = cfg.get('database', 'dbn')

# Connect to MySQL and set up.
db         = create_engine(dbn)
acldb      = Guard.DB(db)
integrator = Integrator.Manager(acldb)
integrator.set_extension_dir('data/repo')

#TODO: Lookup page from the given cgi variables and load the appended plugins.
