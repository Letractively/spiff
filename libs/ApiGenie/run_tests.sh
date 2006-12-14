#!/bin/sh
find . -name "*.py" | while read i; do
  echo $i
  cd `dirname $i`
  python `basename $i`
  cd - >/dev/null
done
