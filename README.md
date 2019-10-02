# Lenmo
Home Task using python, django rest framework and psql according to specifications sent by Lenmo.inc using

- Pyhton version : 3.7.4
- Django 2.2

## To Run the application follow these steps

- First make sure you have pipenv installed
- Second clone the project any where to your pc
- PS: Find Postman Collection at the end of this page

```bash
git clone https://github.com/bassemmagdy/Lenmo.git
```

- Then cd to the directory

```bash
cd lenmo
```

- Rename .env.Example to .env
- Change database configurate to match yours in .env.Example.

- After setting database settings, run the next commands to initialize your venv and install dependencies.

```bash
pipenv install
pipenv shell
```

- Next step you will need to create database using psql commandline:

```bash
psql postgres
CREATE DATABASE lenmo-db;
```

- Now it's time to migrate the database, you'll have to install requirements and migrate your database to start playing around with the API.

```bash
python manage.py makemigrations
python manage.py migrate
```

- We are there!


```bash
python manage.py runserver
```

## The available API routes are:

- User Authentication:

```bash
POST /api/register/
POST /api/login/
```

- Loan Crud

```bash
POST /api/loan/
PATCH /api/loan/pk/
RETRIEVE /api/loan/pk/
DESTROY /api/loan/pk/
LIST /api/loan
```

- Offer Crud

```bash
POST /api/offer/
PATCH /api/offer/pk/
RETRIEVE /api/offer/pk/
DESTROY /api/offer/pk/
LIST /api/offer
```

-Accept Offer:

```bash
api/accept_offer/<int:offer>/
```

-Payment:

```bash
PATCH /api/payment/pk/
LIST /api/payment
```

## Postman

- All Api tuning parameters are inside the below collection:

```bash
- https://www.getpostman.com/collections/274cb163a983be7197e5
```