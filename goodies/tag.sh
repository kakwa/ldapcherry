#!/bin/sh

cd  `dirname $0`/../

version=`sed -e "s/version\ * = \ *'\(.*\)'.*/\1/;tx;d;:x" ./ldapcherry/version.py`

git tag "$version" -m "version $version"
git push origin "$version"
