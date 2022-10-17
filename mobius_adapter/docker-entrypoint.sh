#!/bin/sh

if [ -z "${TESTING}" ]; then
    gunicorn -w 1 'app:create_app()' -b '0.0.0.0:5000'
else
    python3 app.py
fi
