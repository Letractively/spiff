#!/bin/sh
find . -name "*.py" | while read i; do
  echo $i
  cd `dirname $i`
  python2.3 `basename $i`
  cd - >/dev/null
done
