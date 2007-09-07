#!/bin/sh
find . -mindepth 2 -name "run_tests.sh" | while read i; do
  echo $i
  cd `dirname $i`
  sh `basename $i`
  cd - >/dev/null
done
find . -mindepth 2 -name "run_suite.py" | while read i; do
  echo $i
  cd `dirname $i`
  python `basename $i`
  cd - >/dev/null
done
