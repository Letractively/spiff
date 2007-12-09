#!/usr/bin/env python
# Generates the API documentation.
import os, re, sys

doc_file = 'Spiff_Guard.py'
doc_dir  = 'doc'
files = ['DBReader.py',
         'DB.py',
         'DBObject.py',
         'ResourcePath.py',
         'Acl.py',
         'Action.py',
         'Resource.py',
         'ResourceGroup.py']  # Order matters - can't resolve inheritance otherwise.
classes = [os.path.splitext(file)[0] for file in files]

# Concatenate the content of all files into one file.
remove_re = re.compile(r'^from (' + '|'.join(classes) + r') * import .*')
fp_out    = open(doc_file, 'w')
for file in files:
    fp_in = open(file, 'r')
    for line in fp_in:
        if not remove_re.match(line):
            fp_out.write(line)
    fp_in.close()
fp_out.close()

os.system('epydoc ' + ' '.join(['--html',
                                '--parse-only',
                                '--no-private',
                                '--no-source',
                                '--no-frames',
                                '--inheritance=grouped',
                                '-v',
                                '-o %s' % doc_dir, doc_file]))

os.remove(doc_file)
