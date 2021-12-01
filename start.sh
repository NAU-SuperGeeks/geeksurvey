#!/usr/bin/env bash

python manage.py makemigrations
python manage.py makemigrations geeksurvey
python manage.py migrate
echo "server running at port 8000"
python manage.py runserver 0:8000

