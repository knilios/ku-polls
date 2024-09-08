# Ku polls : An online survey service

This application is used to open online polls and surveys. It's based on ```Django``` web framework and written in Python.

This app is created as a part of [Individual Software Process](
https://cpske.github.io/ISP) course at [Kasetsart University](https://www.ku.ac.th) in the academic year 2024.

## Installation
```cmd
git clone https://github.com/knilios/ku-polls.git
```

## How to run
```cmd
cd ku-polls
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata data/users.json
python manage.py loaddata data/polls-v3.json
```

Generate your secret key and then put it in the .env file.
```cmd
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
and then
```cmd
python manage.py runserver
```

## Project documents
All of the project documents can be access in [Project Wiki](../../wiki/Home).

- [Vision Statement](../../wiki/Vision-and-Scope)
- [Requirements](../../wiki/Requirements)
- [Project Plan](../../wiki/Project-Plan)
- [Iteration 1 Plan](../../wiki/Iteration-1-Plan)
- [Iteration 2 Plan](../../wiki/Iteration-2-Plan)
