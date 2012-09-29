#!/bin/bash

test -f env.sh && . env.sh
. $VIRTUAL_ENV/bin/activate
cd $APP_ROOT
exec python$INSTANCE_ID manage.py runfcgi method=threaded daemonize=false

