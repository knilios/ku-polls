brew install python@3.11
python3.11 -m pip install --user virtualenv
python3.11 -m venv venv
source venv/bin/activate

echo Installing python requirements
python -m pip install -r requirements.txt
echo Initializing Django
python manage.py migrate
python manage.py loaddata data/users.json
python manage.py loaddata data/polls-v4.json
python manage.py loaddata data/votes-v4.json
echo "Initializing environment"
python -c "from django.core.management.utils import get_random_secret_key; f = open('.env', 'w'); f.write('SECRET_KEY=django-insecure-'+get_random_secret_key()+'\n'); f.close()"
echo "DEBUG=False" >> .env
echo "ALLOWED_HOSTS=*" >> .env
echo "TIME_ZONE=Asia/Bangkok" >> .env
