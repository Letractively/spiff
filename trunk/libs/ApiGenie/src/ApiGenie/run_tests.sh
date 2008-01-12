#!/bin/sh
find . -name "*.py" -a ! -name "parse2db.py" | while read i; do
  echo $i
  cd `dirname $i`
  python `basename $i`
  cd - >/dev/null
done
