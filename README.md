# API_YAMDB
API_YaMDb

RESTful API code for the YaMDb project.
The YaMDb project collects user reviews on works of art.

**Technologies:**
 - _[Python 3.7](https://docs.python.org/3/)_
 - _[Django 2.2.16](https://docs.djangoproject.com/en/2.2/)_
 - _[Django REST framework 3.12.4](https://www.django-rest-framework.org/)_
 - _[Simple JWT 4.7.1](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)_

**The project provides:**
- superuser (maximum access and editing rights)
- administrator
- moderator
- user

Authorization takes place using a **JWT token**.

The schema of **the database** for which the project is designed is located at the link: https://dbdiagram.io/embed/62f224aac2d9cf52fa715ea5

**To start the project, run the following commands:**
```
git clone <...>
cd <...>
python -m venv env
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

You can view **the API documentation** after launching the project by following the link: 127.0.0.1:8000/swagger/


## The authors of the project:
- Redichkina Aleksandra (https://github.com/AMRedichkina)
- Lisitsyn Vyacheslav (https://github.com/lissitsyn)
