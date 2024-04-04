#!/bin/bash

# turn on bash's job control
set -m

# Start the primary process and put it in the background
gunicorn --bind :80 ProjectTime.wsgi &

# Start the helper process
celery -A ProjectTime.celery worker -l info

# the my_helper_process might need to know how to wait on the
# primary process to start before it does its work and returns


# now we bring the primary process back into the foreground
# and leave it there
fg %1