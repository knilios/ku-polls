@echo off
py -3.11 -m venv venv 
if %errorlevel% equ 0 (
    cd venv/Scripts
    activate
    cd ../..
    python -m pip install -r requirements.txt
    python manage.py migrate
    python manage.py loaddata data/users.json
    python manage.py loaddata data/polls-v3.json

    SECRET_KEY=django-insecure-$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

    echo SECRET_KEY=$SECRET_KEY \nDEBUG = False \nALLOWED_HOSTS = * \nTIME_ZONE = 'Asia/Bangkok' > .env

) else (
    echo Error: Please install Python 3.11
)