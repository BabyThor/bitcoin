#!/bin/bash

sleep 30

cd $APPLICATION_ROOT\search_service
python manage.py migrate --noinput
python3 manage.py runserver 0.0.0.0:8000
