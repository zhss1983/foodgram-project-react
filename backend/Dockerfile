FROM python:3.9-slim
RUN mkdir /code
COPY requirements.txt /code
RUN pip3 install -r /code/requirements.txt
COPY . /code
WORKDIR /code
ENV DB_ENGINE django.db.backends.postgresql_psycopg2
ENV DB_NAME postgres
ENV POSTGRES_USER foodgram_user
ENV POSTGRES_PASSWORD foodgram_16147
ENV DB_HOST db
ENV DB_PORT 5432
ENV CLIENT_ENCODING UTF8
ENV EMAIL_HOST smtp.mail.ru
ENV EMAIL_PORT 2525
ENV EMAIL_HOST_USER zhss.83@mail.ru
ENV EMAIL_HOST_PASSWORD TnWRBWWUSftg1br4PBbB
ENV EMAIL_USE_TLS True
ENV SECRET_KEY django-insecure-f*uc(csx95l66++$&vf2(bamo1ejsa837lo)z7+v&=82cajrft
ENV EMAIL_FOODGRAM zhss.83@mail.ru
RUN python manage.py makemigrations
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
