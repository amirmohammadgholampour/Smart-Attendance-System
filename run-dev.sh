function activate 
{
    source venv/bin/activate
}

function runserver 
{
    python manage.py runserver
}

function makemigrations 
{
    python manage.py makemigrations 
}

function migrate
{
    python manage.py migrate
}

function superuser 
{
    python manage.py createsuperuser
}