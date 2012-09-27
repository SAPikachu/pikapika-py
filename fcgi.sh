#!/bin/bash

test -f env.sh && . env.sh
. $VIRTUAL_ENV/bin/activate
cd $VIRTUAL_ENV/production
exec python$INSTANCE_ID manage.py runfcgi method=threaded daemonize=false

