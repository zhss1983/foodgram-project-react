FROM python:3.9-slim
RUN mkdir /code
COPY requirements.txt /code
RUN pip3 install -r /code/requirements.txt
COPY requirements_db.txt /code
RUN pip3 install -r /code/requirements_db.txt
COPY . /code
WORKDIR /code
RUN python manage.py makemigrations
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
#RUN python manage.py migrate
#RUN python manage.py dumpdata > mytestdump4.json