FROM python:3.9

WORKDIR /code
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY .. .
CMD gunicorn foodgram_back.wsgi:application --bind 0.0.0.0:8000
