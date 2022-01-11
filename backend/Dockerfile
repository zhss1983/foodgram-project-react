FROM python:3.9-slim
WORKDIR /code
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY . /
RUN python manage.py makemigrations
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
