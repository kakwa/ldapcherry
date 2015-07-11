#!/bin/sh
cd `dirname $0`
python setup.py test &&\
pep8 --repeat --show-source --exclude=.venv,.tox,dist,docs,build,*.egg,tests,misc .
