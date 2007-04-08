#!/usr/bin/env python
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sqlalchemy    import *
from ApiDB         import ApiDB
from DocumentModel import Directory, File
import MySQLdb
import Python

supported_types = {
  '.py': Python
}

assert len(sys.argv) > 2
dbn        = sys.argv[1]
path_names = sys.argv[2:]
file_names = []
dir_names  = []
db         = create_engine(dbn)
db         = ApiDB(db)

# Recursively collect file and directory names.
for path_name in path_names:
    if os.path.isdir(path_name):
        for root, dirs, files in os.walk(path_name):
            for filename in files:
                extension = os.path.splitext(filename)[1]
                if extension not in supported_types:
                    print 'Skipping unsupported file %s...' % filename
                    continue
                filename = os.path.join(root, filename)
                dirname  = os.path.dirname(filename)
                file_names.append(filename)
                if dirname not in dir_names:
                    dir_names.append(dirname)
    else:
        extension = os.path.splitext(path_name)[1]
        if extension not in supported_types:
            print 'Skipping unsupported file %s...' % path_name
            continue
        dirname = os.path.dirname(path_name)
        file_names.append(path_name)
        if dirname not in dir_names:
            dir_names.append(dirname)

# Walk through all directories and parse them.
dirs = {}
for dirname in dir_names:
    print 'Importing directory %s...' % dirname
    dir = Directory(dirname)
    assert db.add(None, dir)
    dirs[dirname] = dir

# Walk through all files and parse them.
for filename in file_names:
    dir = dirs[os.path.dirname(filename)]
    print 'Searching parser for %s...' % filename
    extension = os.path.splitext(filename)[1]
    if extension not in supported_types:
        print 'Unsupported file: %s' % filename
        continue
    print 'Parsing file %s...' % filename
    module = supported_types[extension]
    reader = module.Reader()
    file   = reader.read(filename)
    db.add(dir.get_id(), file)
