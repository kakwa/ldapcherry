#!/bin/sh

Red='\33[0;31m';
Gre='\33[0;32m';
RCol='\33[0m';

cd `dirname $0`
python setup.py test &&\
printf "\nPEP 8 compliance check:\n\n"
pep8 \
    --repeat \
    --show-source \
    --exclude=.venv,.tox,dist,docs,build,*.egg,tests,misc . && \
    printf "[${Gre}Passed${RCol}] Yeah! everything is clean\n\n" || \
    printf "[${Red}Failed${RCol}] Oh No! there is some mess to fix\n\n"
