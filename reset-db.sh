#!/bin/bash

./manage.py dbshell <<EOF

drop database pikapika;
create database pikapika character set utf8;

EOF

./manage.py syncdb --noinput

./manage.py loaddata fixtures/*.json

