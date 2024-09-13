@echo off
echo Installing vertual environment
py -3.11 -m venv venv
if [ $? -eq 0] then
    source venv/bin/activate
    echo Installing python requirements
    python -m pip install -r requirements.txt
    echo Initializing Django
    python manage.py migrate
    python manage.py loaddata data/users.json
    python manage.py loaddata data/polls-v3.json

    echo "Initializing environment"
    python -c "from django.core.management.utils import get_random_secret_key; f = open('.env', 'w'); f.write('SECRET_KEY=django-insecure-'+get_random_secret_key()+'\n'); f.close()"
    
    cat >> .env
    DEBUG=False
    ALLOWED_HOSTS=*
    TIME_ZONE=Asia/Bangkok
    ^D
    exit 0

else
    echo "Error: Please install Python 3.11"
    exit 1 
fi
