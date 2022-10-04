#!/bin/sh

gunicorn -w 1 --threads 100 'app:create_app()' -b '0.0.0.0:5000'
